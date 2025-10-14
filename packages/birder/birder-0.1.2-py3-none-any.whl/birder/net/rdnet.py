"""
Revitalized DenseNet, adapted from
https://github.com/naver-ai/rdnet/blob/main/rdnet/rdnet.py

Paper "DenseNets Reloaded: Paradigm Shift Beyond ResNets and ViTs", https://arxiv.org/abs/2403.19588
"""

# Reference license: Apache-2.0

from collections import OrderedDict
from collections.abc import Callable
from typing import Any
from typing import Literal
from typing import Optional

import torch
from torch import nn
from torchvision.ops import StochasticDepth

from birder.common.masking import mask_tensor
from birder.layers import LayerNorm2d
from birder.model_registry import registry
from birder.net.base import DetectorBackbone
from birder.net.base import MaskedTokenRetentionMixin
from birder.net.base import PreTrainEncoder
from birder.net.base import TokenRetentionResultType


class EffectiveSEModule(nn.Module):
    """
    From "CenterMask: Real-Time Anchor-Free Instance Segmentation" - https://arxiv.org/abs/1911.06667
    """

    def __init__(self, channels: int, activation: Callable[..., nn.Module] = nn.Hardsigmoid) -> None:
        super().__init__()
        self.fc = nn.Conv2d(channels, channels, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0))
        self.gate = activation()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x_se = x.mean((2, 3), keepdim=True)
        x_se = self.fc(x_se)
        x_se = self.gate(x_se)

        return x * x_se


class Block(nn.Sequential):
    def __init__(self, in_channels: int, inter_channels: int, out_channels: int) -> None:
        super().__init__()
        self.append(
            nn.Conv2d(in_channels, in_channels, groups=in_channels, kernel_size=(7, 7), stride=(1, 1), padding=(3, 3))
        )
        self.append(LayerNorm2d(in_channels, eps=1e-6))
        self.append(nn.Conv2d(in_channels, inter_channels, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0)))
        self.append(nn.GELU())
        self.append(nn.Conv2d(inter_channels, out_channels, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0)))


class BlockESE(nn.Sequential):
    def __init__(self, in_channels: int, inter_channels: int, out_channels: int) -> None:
        super().__init__()
        self.append(
            nn.Conv2d(in_channels, in_channels, groups=in_channels, kernel_size=(7, 7), stride=(1, 1), padding=(3, 3))
        )
        self.append(LayerNorm2d(in_channels, eps=1e-6))
        self.append(nn.Conv2d(in_channels, inter_channels, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0)))
        self.append(nn.GELU())
        self.append(nn.Conv2d(inter_channels, out_channels, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0)))
        self.append(EffectiveSEModule(out_channels))


class DenseBlock(nn.Module):
    def __init__(
        self,
        num_input_features: int,
        growth_rate: int,
        bottleneck_width_ratio: float,
        drop_path_rate: float,
        block_type: type[Block | BlockESE],
        ls_init_value: float,
    ) -> None:
        super().__init__()
        self.gamma = nn.Parameter(ls_init_value * torch.ones(growth_rate))
        growth_rate = int(growth_rate)
        inter_channels = int(num_input_features * bottleneck_width_ratio / 8) * 8

        self.drop_path = StochasticDepth(drop_path_rate, mode="row")

        self.layers = block_type(
            in_channels=num_input_features, inter_channels=inter_channels, out_channels=growth_rate
        )

    def forward(self, xl: list[torch.Tensor]) -> torch.Tensor:
        x = torch.concat(xl, dim=1)
        x = self.layers(x)
        x = x.mul(self.gamma.reshape(1, -1, 1, 1))
        x = self.drop_path(x)

        return x


class DenseStage(nn.Module):
    def __init__(
        self,
        num_block: int,
        num_input_features: int,
        drop_path_rates: list[int],
        growth_rate: int,
        bottleneck_width_ratio: float,
        block_name: str,
        ls_init_value: float,
    ) -> None:
        super().__init__()
        if block_name == "Block":
            block_type = Block
        elif block_name == "BlockESE":
            block_type = BlockESE
        else:
            raise ValueError(f"Unknown block_name '{block_name}'")

        self.layers = nn.ModuleList()
        for i in range(num_block):
            self.layers.append(
                DenseBlock(
                    num_input_features=num_input_features,
                    growth_rate=growth_rate,
                    bottleneck_width_ratio=bottleneck_width_ratio,
                    drop_path_rate=drop_path_rates[i],
                    block_type=block_type,
                    ls_init_value=ls_init_value,
                )
            )
            num_input_features += growth_rate

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = [x]
        for module in self.layers:
            new_feature = module(features)
            features.append(new_feature)

        return torch.concat(features, dim=1)


class RDNet(DetectorBackbone, PreTrainEncoder, MaskedTokenRetentionMixin):
    block_group_regex = r"body\.stage(\d+)\.\d+\.layers\.(\d+)"

    def __init__(
        self,
        input_channels: int,
        num_classes: int,
        *,
        config: Optional[dict[str, Any]] = None,
        size: Optional[tuple[int, int]] = None,
    ) -> None:
        super().__init__(input_channels, num_classes, config=config, size=size)
        assert self.config is not None, "must set config"

        bottleneck_width_ratio = 4.0
        ls_init_value = 1e-6
        num_init_features: int = self.config["num_init_features"]
        growth_rates = self.config["growth_rates"]
        num_blocks_list: list[int] = self.config["num_blocks_list"]
        is_downsample_block: list[bool] = self.config["is_downsample_block"]
        transition_compression_ratio: float = self.config["transition_compression_ratio"]
        block_type_name: list[str] = self.config["block_type_name"]
        drop_path_rate: float = self.config["drop_path_rate"]

        self.stem = nn.Sequential(
            nn.Conv2d(self.input_channels, num_init_features, kernel_size=(4, 4), stride=(4, 4), padding=(0, 0)),
            LayerNorm2d(num_init_features),
        )

        num_stages = len(growth_rates)
        num_features = num_init_features
        dp_rates = [x.tolist() for x in torch.linspace(0, drop_path_rate, sum(num_blocks_list)).split(num_blocks_list)]

        # Add dense blocks
        stages: OrderedDict[str, nn.Module] = OrderedDict()
        return_channels: list[int] = []
        dense_stage_layers: list[nn.Module] = []
        idx = 0
        for i in range(num_stages):
            if i > 0:
                compressed_num_features = int(num_features * transition_compression_ratio / 8) * 8
                k_size = (1, 1)
                if is_downsample_block[i] is True:
                    stages[f"stage{idx+1}"] = nn.Sequential(*dense_stage_layers)
                    return_channels.append(num_features)
                    dense_stage_layers = []
                    idx += 1
                    k_size = (2, 2)

                dense_stage_layers.append(LayerNorm2d(num_features))
                dense_stage_layers.append(
                    nn.Conv2d(num_features, compressed_num_features, kernel_size=k_size, stride=k_size, padding=(0, 0))
                )
                num_features = compressed_num_features

            dense_stage_layers.append(
                DenseStage(
                    num_block=num_blocks_list[i],
                    num_input_features=num_features,
                    drop_path_rates=dp_rates[i],
                    growth_rate=growth_rates[i],
                    bottleneck_width_ratio=bottleneck_width_ratio,
                    block_name=block_type_name[i],
                    ls_init_value=ls_init_value,
                )
            )
            num_features += num_blocks_list[i] * growth_rates[i]

        stages[f"stage{idx+1}"] = nn.Sequential(*dense_stage_layers)
        return_channels.append(num_features)

        self.body = nn.Sequential(stages)
        self.features = nn.Sequential(
            nn.AdaptiveAvgPool2d(output_size=(1, 1)),
            LayerNorm2d(num_features, eps=1e-6),
            nn.Flatten(1),
        )
        self.return_channels = return_channels
        self.embedding_size = num_features
        self.classifier = self.create_classifier()

        self.stem_stride = 4
        self.stem_width = num_init_features
        self.encoding_size = num_features

        # Weight initialization
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight)

            elif isinstance(m, nn.Linear):
                nn.init.zeros_(m.bias)

    def detection_features(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        x = self.stem(x)

        out = {}
        for name, module in self.body.named_children():
            x = module(x)
            if name in self.return_stages:
                out[name] = x

        return out

    def freeze_stages(self, up_to_stage: int) -> None:
        for param in self.stem.parameters():
            param.requires_grad = False

        for idx, module in enumerate(self.body.children()):
            if idx >= up_to_stage:
                break

            for param in module.parameters():
                param.requires_grad = False

    def masked_encoding_retention(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
        mask_token: Optional[torch.Tensor] = None,
        return_keys: Literal["all", "features", "embedding"] = "features",
    ) -> TokenRetentionResultType:
        x = self.stem(x)
        x = mask_tensor(x, mask, patch_factor=self.max_stride // self.stem_stride, mask_token=mask_token)
        x = self.body(x)

        result: TokenRetentionResultType = {}
        if return_keys in ("all", "features"):
            result["features"] = x
        if return_keys in ("all", "embedding"):
            result["embedding"] = self.features(x)

        return result

    def forward_features(self, x: torch.Tensor) -> torch.Tensor:
        x = self.stem(x)
        return self.body(x)

    def embedding(self, x: torch.Tensor) -> torch.Tensor:
        x = self.forward_features(x)
        return self.features(x)


registry.register_model_config(
    "rdnet_t",
    RDNet,
    config={
        # n_layer = 7
        "num_init_features": 64,
        "growth_rates": [64] + [104] + [128] * 4 + [224],
        "num_blocks_list": [3] * 7,
        "is_downsample_block": [False, True, True, False, False, False, True],
        "transition_compression_ratio": 0.5,
        "block_type_name": ["Block"] + ["Block"] + ["BlockESE"] * 4 + ["BlockESE"],
        "drop_path_rate": 0.15,
    },
)
registry.register_model_config(
    "rdnet_s",
    RDNet,
    config={
        # n_layer = 11
        "num_init_features": 72,
        "growth_rates": [64] + [128] + [128] * (11 - 4) + [240] * 2,
        "num_blocks_list": [3] * 11,
        "is_downsample_block": [False, True, True, False, False, False, False, False, False, True, False],
        "transition_compression_ratio": 0.5,
        "block_type_name": ["Block"] + ["Block"] + ["BlockESE"] * (11 - 4) + ["BlockESE"] * 2,
        "drop_path_rate": 0.35,
    },
)
registry.register_model_config(
    "rdnet_b",
    RDNet,
    config={
        # n_layer = 11
        "num_init_features": 120,
        "growth_rates": [96] + [128] + [168] * (11 - 4) + [336] * 2,
        "num_blocks_list": [3] * 11,
        "is_downsample_block": [False, True, True, False, False, False, False, False, False, True, False],
        "transition_compression_ratio": 0.5,
        "block_type_name": ["Block"] + ["Block"] + ["BlockESE"] * (11 - 4) + ["BlockESE"] * 2,
        "drop_path_rate": 0.4,
    },
)
registry.register_model_config(
    "rdnet_l",
    RDNet,
    config={
        # n_layer = 12
        "num_init_features": 144,
        "growth_rates": [128] + [192] + [256] * (12 - 4) + [360] * 2,
        "num_blocks_list": [3] * 12,
        "is_downsample_block": [False, True, True, False, False, False, False, False, False, False, True, False],
        "transition_compression_ratio": 0.5,
        "block_type_name": ["Block"] + ["Block"] + ["BlockESE"] * (12 - 4) + ["BlockESE"] * 2,
        "drop_path_rate": 0.5,
    },
)

registry.register_weights(
    "rdnet_t_ibot-bioscan5m",
    {
        "url": "https://huggingface.co/birder-project/rdnet_t_ibot-bioscan5m/resolve/main",
        "description": "RDNet tiny model pre-trained using iBOT on the BIOSCAN-5M dataset",
        "resolution": (224, 224),
        "formats": {
            "pt": {
                "file_size": 87.2,
                "sha256": "ff68958f31557d9d753cdea759c371dcefa807e134afeb2a247aba99f67e72ab",
            }
        },
        "net": {"network": "rdnet_t", "tag": "ibot-bioscan5m"},
    },
)
registry.register_weights(
    "rdnet_s_arabian-peninsula256px",
    {
        "url": "https://huggingface.co/birder-project/rdnet_s_arabian-peninsula/resolve/main",
        "description": "RDNet small model trained on the arabian-peninsula dataset",
        "resolution": (256, 256),
        "formats": {
            "pt": {
                "file_size": 191.3,
                "sha256": "db19d6a637b3f88c397fb89cc97d0db99f6921c3042cf0ee0ecc98ed77012b47",
            }
        },
        "net": {"network": "rdnet_s", "tag": "arabian-peninsula256px"},
    },
)
registry.register_weights(
    "rdnet_s_arabian-peninsula",
    {
        "url": "https://huggingface.co/birder-project/rdnet_s_arabian-peninsula/resolve/main",
        "description": "RDNet small model trained on the arabian-peninsula dataset",
        "resolution": (384, 384),
        "formats": {
            "pt": {
                "file_size": 191.3,
                "sha256": "b3905cbae41dd71451d3508be45f6f2ab939bc23c49df512e5eb35513d8d6601",
            }
        },
        "net": {"network": "rdnet_s", "tag": "arabian-peninsula"},
    },
)
