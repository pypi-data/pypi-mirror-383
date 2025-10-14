"""
MobileNet v1, adapted from
https://github.com/apache/mxnet/blob/1.9.1/example/image-classification/symbols/mobilenet.py

Paper "MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications",
https://arxiv.org/abs/1704.04861
"""

# Reference license: Apache-2.0

from collections import OrderedDict
from typing import Any
from typing import Optional

import torch
from torch import nn
from torchvision.ops import Conv2dNormActivation

from birder.model_registry import registry
from birder.net.base import DetectorBackbone


class DepthwiseSeparableNormConv2d(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, stride: tuple[int, int]) -> None:
        super().__init__()
        self.dpw_bn_conv = nn.Sequential(
            Conv2dNormActivation(
                in_channels,
                in_channels,
                kernel_size=(3, 3),
                stride=stride,
                padding=(1, 1),
                groups=in_channels,
                bias=False,
            ),
            Conv2dNormActivation(
                in_channels,
                out_channels,
                kernel_size=(1, 1),
                stride=(1, 1),
                padding=(0, 0),
                bias=False,
            ),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dpw_bn_conv(x)


# pylint: disable=invalid-name
class MobileNet_v1(DetectorBackbone):
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

        alpha: float = self.config["alpha"]

        base = int(32 * alpha)
        self.stem = nn.Sequential(
            Conv2dNormActivation(
                self.input_channels, base, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), bias=False
            ),
            Conv2dNormActivation(
                base, base, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), groups=base, bias=False
            ),
            Conv2dNormActivation(base, base * 2, kernel_size=(1, 1), stride=(1, 1), padding=(0, 0), bias=False),
        )

        stages: OrderedDict[str, nn.Module] = OrderedDict()
        return_channels: list[int] = []

        stages["stage1"] = nn.Sequential(
            DepthwiseSeparableNormConv2d(base * 2, base * 4, stride=(2, 2)),
            DepthwiseSeparableNormConv2d(base * 4, base * 4, stride=(1, 1)),
        )
        return_channels.append(base * 4)

        stages["stage2"] = nn.Sequential(
            DepthwiseSeparableNormConv2d(base * 4, base * 8, stride=(2, 2)),
            DepthwiseSeparableNormConv2d(base * 8, base * 8, stride=(1, 1)),
        )
        return_channels.append(base * 8)

        stages["stage3"] = nn.Sequential(
            DepthwiseSeparableNormConv2d(base * 8, base * 16, stride=(2, 2)),
            DepthwiseSeparableNormConv2d(base * 16, base * 16, stride=(1, 1)),
            DepthwiseSeparableNormConv2d(base * 16, base * 16, stride=(1, 1)),
            DepthwiseSeparableNormConv2d(base * 16, base * 16, stride=(1, 1)),
            DepthwiseSeparableNormConv2d(base * 16, base * 16, stride=(1, 1)),
            DepthwiseSeparableNormConv2d(base * 16, base * 16, stride=(1, 1)),
        )
        return_channels.append(base * 16)

        stages["stage4"] = nn.Sequential(
            DepthwiseSeparableNormConv2d(base * 16, base * 32, stride=(2, 2)),
            # 32
            DepthwiseSeparableNormConv2d(base * 32, base * 32, stride=(1, 1)),
        )
        return_channels.append(base * 32)

        self.body = nn.Sequential(stages)
        self.features = nn.Sequential(
            Conv2dNormActivation(
                base * 32,
                base * 32,
                kernel_size=(1, 1),
                stride=(1, 1),
                padding=(0, 0),
                bias=False,
                activation_layer=None,
            ),
            nn.AdaptiveAvgPool2d(output_size=(1, 1)),
            nn.Flatten(1),
        )
        self.return_channels = return_channels
        self.embedding_size = base * 32
        self.classifier = self.create_classifier()

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

    def forward_features(self, x: torch.Tensor) -> torch.Tensor:
        x = self.stem(x)
        return self.body(x)

    def embedding(self, x: torch.Tensor) -> torch.Tensor:
        x = self.forward_features(x)
        return self.features(x)


registry.register_model_config("mobilenet_v1_0_25", MobileNet_v1, config={"alpha": 0.25})
registry.register_model_config("mobilenet_v1_0_5", MobileNet_v1, config={"alpha": 0.5})
registry.register_model_config("mobilenet_v1_0_75", MobileNet_v1, config={"alpha": 0.75})
registry.register_model_config("mobilenet_v1_1_0", MobileNet_v1, config={"alpha": 1.0})
