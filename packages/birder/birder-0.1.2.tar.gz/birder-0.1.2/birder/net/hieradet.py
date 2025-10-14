"""
HieraDet, adapted from
https://github.com/facebookresearch/sam2/blob/main/sam2/modeling/backbones/hieradet.py

Paper "SAM 2: Segment Anything in Images and Videos", https://arxiv.org/abs/2408.00714

Changes from original:
* Support only 2d
* Allow dynamic window_spec (by defining divisor as a negative number)
"""

# Reference license: Apache-2.0

import copy
from collections import OrderedDict
from typing import Any
from typing import Literal
from typing import Optional

import torch
import torch.nn.functional as F
from torch import nn
from torchvision.ops import MLP
from torchvision.ops import Permute
from torchvision.ops import StochasticDepth

from birder.common.masking import mask_tensor
from birder.model_registry import registry
from birder.net.base import DetectorBackbone
from birder.net.base import MaskedTokenRetentionMixin
from birder.net.base import PreTrainEncoder
from birder.net.base import TokenRetentionResultType


def window_partition(x: torch.Tensor, window_size: int) -> tuple[torch.Tensor, tuple[int, int]]:
    (B, H, W, C) = x.size()

    pad_h = (window_size - H % window_size) % window_size
    pad_w = (window_size - W % window_size) % window_size
    if pad_h > 0 or pad_w > 0:
        x = F.pad(x, (0, 0, 0, pad_w, 0, pad_h))

    h_p = H + pad_h
    w_p = W + pad_w

    x = x.view(B, h_p // window_size, window_size, w_p // window_size, window_size, C)
    windows = x.permute(0, 1, 3, 2, 4, 5).contiguous().view(-1, window_size, window_size, C)

    return (windows, (h_p, w_p))


def window_unpartition(
    windows: torch.Tensor, window_size: int, pad_hw: tuple[int, int], hw: tuple[int, int]
) -> torch.Tensor:
    (h_p, w_p) = pad_hw
    (H, W) = hw
    B = windows.shape[0] // (h_p * w_p // window_size // window_size)
    x = windows.view(B, h_p // window_size, w_p // window_size, window_size, window_size, -1)
    x = x.permute(0, 1, 3, 2, 4, 5).contiguous().view(B, h_p, w_p, -1)

    if h_p > H or w_p > W:
        x = x[:, :H, :W, :].contiguous()

    return x


class PatchEmbed(nn.Module):
    def __init__(
        self, dim_in: int, dim_out: int, kernel: tuple[int, int], stride: tuple[int, int], padding: tuple[int, int]
    ) -> None:
        super().__init__()
        self.proj = nn.Conv2d(dim_in, dim_out, kernel_size=kernel, stride=stride, padding=padding)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.proj(x)
        x = x.permute(0, 2, 3, 1)

        return x


class MultiScaleAttention(nn.Module):
    def __init__(self, dim: int, dim_out: int, num_heads: int, q_pool: Optional[nn.Module]) -> None:
        super().__init__()
        self.num_heads = num_heads
        self.q_pool = q_pool
        self.qkv = nn.Linear(dim, dim_out * 3)
        self.proj = nn.Linear(dim_out, dim_out)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        (B, H, W, _) = x.size()
        qkv = self.qkv(x).reshape(B, H * W, 3, self.num_heads, -1)
        (q, k, v) = qkv.unbind(dim=2)

        # Q pooling (for downsample at stage changes)
        if self.q_pool is not None:
            q = q.reshape(B, H, W, -1).permute(0, 3, 1, 2)
            q = self.q_pool(q).permute(0, 2, 3, 1)
            (H, W) = q.shape[1:3]  # Downsampled shape
            q = q.reshape(B, H * W, self.num_heads, -1)

        x = F.scaled_dot_product_attention(  # pylint: disable=not-callable
            q.transpose(1, 2),
            k.transpose(1, 2),
            v.transpose(1, 2),
        )
        x = x.transpose(1, 2)
        x = x.reshape(B, H, W, -1)
        x = self.proj(x)

        return x


class MultiScaleBlock(nn.Module):
    def __init__(
        self,
        dim: int,
        dim_out: int,
        num_heads: int,
        mlp_ratio: float,
        drop_path: float,
        q_stride: Optional[tuple[int, int]],
        window_size: int,
    ) -> None:
        super().__init__()
        self.dim = dim
        self.dim_out = dim_out

        self.norm1 = nn.LayerNorm(dim)
        if dim != dim_out:
            self.proj = nn.Linear(dim, dim_out)
        else:
            self.proj = nn.Identity()

        self.window_size = window_size
        self.q_stride = q_stride
        if self.q_stride is not None:
            self.pool = nn.MaxPool2d(kernel_size=q_stride, stride=q_stride, ceil_mode=False)
        else:
            self.pool = None

        self.attn = MultiScaleAttention(
            dim,
            dim_out,
            num_heads=num_heads,
            q_pool=copy.deepcopy(self.pool),
        )
        self.norm2 = nn.LayerNorm(dim_out)
        self.mlp = MLP(dim_out, [int(dim_out * mlp_ratio), dim_out], activation_layer=nn.GELU)
        self.drop_path = StochasticDepth(drop_path, mode="row")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        shortcut = x  # (B, H, W, C)
        x = self.norm1(x)

        # Skip connection
        if self.dim != self.dim_out:
            shortcut = self.proj(x)
            if self.pool is not None:
                shortcut = shortcut.permute(0, 3, 1, 2)
                shortcut = self.pool(shortcut).permute(0, 2, 3, 1)

        # Window partition
        window_size = self.window_size
        pad_hw = (shortcut.size(1), shortcut.size(2))
        (H, W) = pad_hw
        if self.window_size > 0:
            H = x.shape[1]
            W = x.shape[2]
            (x, pad_hw) = window_partition(x, window_size)

        # Window Attention + Q Pooling (if stage change)
        x = self.attn(x)
        if self.q_stride is not None:
            # Shapes have changed due to Q pooling
            window_size = self.window_size // self.q_stride[0]
            (H, W) = (shortcut.size(1), shortcut.size(2))

            pad_h = (window_size - H % window_size) % window_size
            pad_w = (window_size - W % window_size) % window_size
            pad_hw = (H + pad_h, W + pad_w)

        # Reverse window partition
        if self.window_size > 0:
            x = window_unpartition(x, window_size, pad_hw, (H, W))

        x = shortcut + self.drop_path(x)
        x = x + self.drop_path(self.mlp(self.norm2(x)))

        return x


class HieraDet(DetectorBackbone, PreTrainEncoder, MaskedTokenRetentionMixin):
    block_group_regex = r"body\.stage(\d+)\.(\d+)"

    # pylint: disable=too-many-locals
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

        patch_kernel = (7, 7)
        patch_stride = (4, 4)
        patch_padding = (3, 3)
        q_stride = (2, 2)
        q_pool = 3
        dim_mul = 2.0
        head_mul = 2.0
        depths: list[int] = self.config["depths"]
        embed_dim: int = self.config["embed_dim"]
        num_heads: int = self.config["num_heads"]
        global_pos_size: tuple[int, int] = self.config["global_pos_size"]
        global_att_blocks: list[int] = self.config["global_att_blocks"]
        window_spec: list[int] = self.config["window_spec"]
        drop_path_rate: float = self.config["drop_path_rate"]

        self.stage_ends = [sum(depths[:i]) - 1 for i in range(1, len(depths) + 1)]
        self.q_pool_blocks = [x + 1 for x in self.stage_ends[:-1]][:q_pool]
        assert 0 <= q_pool <= len(self.stage_ends[:-1])

        stem_dim = embed_dim
        self.stem = PatchEmbed(self.input_channels, stem_dim, patch_kernel, patch_stride, patch_padding)

        self.pos_embed = nn.Parameter(torch.zeros(1, embed_dim, *global_pos_size))
        self.pos_embed_win = nn.Parameter(torch.zeros(1, embed_dim, window_spec[0], window_spec[0]))

        depth = sum(depths)
        dpr = [x.item() for x in torch.linspace(0, drop_path_rate, depth)]  # Stochastic depth decay rule

        cur_stage = 1
        layers = []
        stages: OrderedDict[str, nn.Module] = OrderedDict()
        return_channels: list[int] = []
        for i in range(depth):
            dim_out = embed_dim
            window_size = window_spec[cur_stage - 1]  # Lags by a block

            if i in global_att_blocks:
                window_size = 0
            elif window_size < 0:
                window_size = min(self.size) // -window_size

            if i - 1 in self.stage_ends:
                dim_out = int(embed_dim * dim_mul)
                num_heads = int(num_heads * head_mul)
                cur_stage += 1

            block = MultiScaleBlock(
                dim=embed_dim,
                dim_out=dim_out,
                num_heads=num_heads,
                mlp_ratio=4.0,
                drop_path=dpr[i],
                q_stride=q_stride if i in self.q_pool_blocks else None,
                window_size=window_size,
            )
            embed_dim = dim_out
            layers.append(block)

            if i in self.stage_ends:
                stages[f"stage{cur_stage}"] = nn.Sequential(*layers)
                return_channels.append(dim_out)
                layers = []

        assert len(layers) == 0

        self.body = nn.Sequential(stages)
        self.features = nn.Sequential(
            nn.LayerNorm(embed_dim),
            Permute([0, 3, 1, 2]),  # B H W C -> B C H W
            nn.AdaptiveAvgPool2d(output_size=(1, 1)),
            nn.Flatten(1),
        )
        self.return_channels = return_channels
        self.embedding_size = embed_dim
        self.classifier = self.create_classifier()

        self.stem_stride = patch_stride[0]
        self.stem_width = stem_dim
        self.encoding_size = embed_dim

        # Weight initialization
        nn.init.trunc_normal_(self.pos_embed, std=0.02)
        nn.init.trunc_normal_(self.pos_embed_win, std=0.02)

    def _get_pos_embed(self, x: torch.Tensor) -> torch.Tensor:
        h = x.size(1)
        w = x.size(2)
        window_embed = self.pos_embed_win
        pos_embed = F.interpolate(self.pos_embed, size=(h, w), mode="bicubic")
        pos_embed = pos_embed + window_embed.tile([i // j for i, j in zip(pos_embed.shape, window_embed.shape)])
        pos_embed = pos_embed.permute(0, 2, 3, 1)

        return pos_embed

    def detection_features(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        x = self.stem(x)
        x = x + self._get_pos_embed(x)

        out = {}
        for name, module in self.body.named_children():
            x = module(x)
            if name in self.return_stages:
                out[name] = x.permute(0, 3, 1, 2).contiguous()

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
        x = mask_tensor(
            x, mask, channels_last=True, patch_factor=self.max_stride // self.stem_stride, mask_token=mask_token
        )
        x = x + self._get_pos_embed(x)
        x = self.body(x)

        result: TokenRetentionResultType = {}
        if return_keys in ("all", "features"):
            result["features"] = x.permute(0, 3, 1, 2).contiguous()
        if return_keys in ("all", "embedding"):
            result["embedding"] = self.features(x)

        return result

    def forward_features(self, x: torch.Tensor) -> torch.Tensor:
        x = self.stem(x)
        x = x + self._get_pos_embed(x)
        x = self.body(x)

        return x

    def embedding(self, x: torch.Tensor) -> torch.Tensor:
        x = self.forward_features(x)
        x = self.features(x)

        return x

    def adjust_size(self, new_size: tuple[int, int]) -> None:
        if new_size == self.size:
            return

        super().adjust_size(new_size)

        assert self.config is not None, "must set config"
        global_att_blocks: list[int] = self.config["global_att_blocks"]
        window_spec: list[int] = self.config["window_spec"]

        cur_stage = 1
        i = 0
        for m in self.body.modules():
            if isinstance(m, MultiScaleBlock):
                window_size = window_spec[cur_stage - 1]
                if i in global_att_blocks:
                    window_size = 0
                elif window_size < 0:
                    window_size = min(new_size) // -window_size

                if i - 1 in self.stage_ends:
                    cur_stage += 1

                m.window_size = window_size

                i += 1

    def load_hiera_weights(self, state_dict: dict[str, Any]) -> None:
        # NOTE: Only abswin variant supported, attention pool not supported

        # Remove classifier weights
        if "classifier.weight" in state_dict:
            del state_dict["classifier.weight"]
            del state_dict["classifier.bias"]

        # Adjust pos_embed_win
        if self.pos_embed.size(3) != state_dict["pos_embed"].size(3):
            pos_embed = state_dict["pos_embed"]
            pos_embed = F.interpolate(pos_embed, size=(self.pos_embed.shape[2:4]), mode="bicubic")
            state_dict["pos_embed"] = pos_embed

        # Load the modified state dict
        v = state_dict.pop("features.1.weight")
        state_dict["features.0.weight"] = v
        v = state_dict.pop("features.1.bias")
        state_dict["features.0.bias"] = v
        incompatible_keys = self.load_state_dict(state_dict, strict=False)
        assert len(incompatible_keys.unexpected_keys) == 0


registry.register_model_config(
    "hieradet_tiny",
    HieraDet,
    config={
        "depths": [1, 2, 7, 2],
        "embed_dim": 96,
        "num_heads": 1,
        "global_pos_size": (7, 7),
        "global_att_blocks": [5, 7, 9],
        "window_spec": [8, 4, -16, -32],
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "hieradet_small",
    HieraDet,
    config={
        "depths": [1, 2, 11, 2],
        "embed_dim": 96,
        "num_heads": 1,
        "global_pos_size": (7, 7),
        "global_att_blocks": [7, 10, 13],
        "window_spec": [8, 4, -16, -32],
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "hieradet_base",
    HieraDet,
    config={
        "depths": [2, 3, 16, 3],
        "embed_dim": 96,
        "num_heads": 1,
        "global_pos_size": (14, 14),
        "global_att_blocks": [12, 16, 20],
        "window_spec": [8, 4, -16, -32],
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "hieradet_base_plus",
    HieraDet,
    config={
        "depths": [2, 3, 16, 3],
        "embed_dim": 112,
        "num_heads": 2,
        "global_pos_size": (14, 14),
        "global_att_blocks": [12, 16, 20],
        "window_spec": [8, 4, -16, -32],
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "hieradet_large",
    HieraDet,
    config={
        "depths": [2, 6, 36, 4],
        "embed_dim": 144,
        "num_heads": 2,
        "global_pos_size": (7, 7),
        "global_att_blocks": [23, 33, 43],
        "window_spec": [8, 4, -16, -32],
        "drop_path_rate": 0.2,
    },
)

registry.register_weights(
    "hieradet_small_dino-v2",
    {
        "url": "https://huggingface.co/birder-project/hieradet_small_dino-v2/resolve/main",
        "description": (
            "HieraDet small image encoder pre-trained using DINOv2. "
            "This model has not been fine-tuned for a specific classification task"
        ),
        "resolution": (224, 224),
        "formats": {
            "pt": {
                "file_size": 129.6,
                "sha256": "eb41b8a35445e7f350797094d5e365306b29351e64edd4a316420c23d1e17073",
            }
        },
        "net": {"network": "hieradet_small", "tag": "dino-v2"},
    },
)
registry.register_weights(
    "hieradet_small_dino-v2-inat21-256px",
    {
        "url": "https://huggingface.co/birder-project/hieradet_small_dino-v2-inat21/resolve/main",
        "description": "HieraDet small model pre-trained using DINOv2, then fine-tuned on the iNaturalist 2021 dataset",
        "resolution": (256, 256),
        "formats": {
            "pt": {
                "file_size": 159.8,
                "sha256": "e1bdeba97eae816ec3ab9b3238d97decf2c34d29b70f9291116ce962b9a4f9df",
            }
        },
        "net": {"network": "hieradet_small", "tag": "dino-v2-inat21-256px"},
    },
)
registry.register_weights(
    "hieradet_small_dino-v2-inat21",
    {
        "url": "https://huggingface.co/birder-project/hieradet_small_dino-v2-inat21/resolve/main",
        "description": "HieraDet small model pre-trained using DINOv2, then fine-tuned on the iNaturalist 2021 dataset",
        "resolution": (384, 384),
        "formats": {
            "pt": {
                "file_size": 159.8,
                "sha256": "271fa9ed6a9aa1f4d1fc8bbb4c4cac9d15b264f2ac544efb5cd971412691880d",
            }
        },
        "net": {"network": "hieradet_small", "tag": "dino-v2-inat21"},
    },
)
registry.register_weights(
    "hieradet_small_dino-v2-imagenet12k",
    {
        "url": "https://huggingface.co/birder-project/hieradet_small_dino-v2-imagenet12k/resolve/main",
        "description": "HieraDet small model pre-trained using DINOv2, then fine-tuned on the ImageNet-12K dataset",
        "resolution": (256, 256),
        "formats": {
            "pt": {
                "file_size": 164.8,
                "sha256": "b89dd6c13d061fe8a09d051bb3d76e632e650067ca71578e37b02033107c9963",
            }
        },
        "net": {"network": "hieradet_small", "tag": "dino-v2-imagenet12k"},
    },
)
