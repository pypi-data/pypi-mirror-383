"""
RoPE ViT, adapted from
https://github.com/naver-ai/rope-vit/blob/main/deit/models_v2_rope.py
and
https://github.com/huggingface/pytorch-image-models/blob/main/timm/layers/pos_embed_sincos.py

Paper "Rotary Position Embedding for Vision Transformer", https://arxiv.org/abs/2403.13298

Changes from original:
* Implemented only axial RoPE (EVA style RoPE)
"""

# Reference license: Apache-2.0 and Apache-2.0

import math
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import Literal
from typing import Optional

import torch
import torch.nn.functional as F
from torch import nn
from torchvision.ops import StochasticDepth

from birder.common.masking import mask_tensor
from birder.layers import FFN
from birder.layers import LayerScale
from birder.layers import MultiHeadAttentionPool
from birder.layers import SwiGLU_FFN
from birder.layers.activations import get_activation_module
from birder.model_registry import registry
from birder.net.base import DetectorBackbone
from birder.net.base import MaskedTokenOmissionMixin
from birder.net.base import MaskedTokenRetentionMixin
from birder.net.base import PreTrainEncoder
from birder.net.base import TokenOmissionResultType
from birder.net.base import TokenRetentionResultType
from birder.net.vit import PatchEmbed
from birder.net.vit import adjust_position_embedding


def build_rotary_pos_embed(
    dim: int,
    temperature: float,
    grid_size: tuple[int, int],
    grid_indexing: str,
    grid_offset: int,
    pt_grid_size: Optional[tuple[int, int]],
) -> tuple[torch.Tensor, torch.Tensor]:
    assert dim % 4 == 0
    num_bands = dim // 4
    exp = torch.arange(0, num_bands, 1) / num_bands
    bands = 1.0 / (temperature**exp)

    if pt_grid_size is None:
        pt_grid_size = grid_size

    t = [(torch.arange(s) + grid_offset) / s * p for s, p in zip(grid_size, pt_grid_size)]
    grid = torch.stack(torch.meshgrid(t, indexing=grid_indexing), dim=-1)
    grid = grid.unsqueeze(-1)
    pos = grid * bands
    sin_emb = pos.sin()
    cos_emb = pos.cos()

    num_spatial_dim = grid_size[0] * grid_size[1]

    sin_emb = sin_emb.reshape(num_spatial_dim, -1).repeat_interleave(2, -1)
    cos_emb = cos_emb.reshape(num_spatial_dim, -1).repeat_interleave(2, -1)

    return (sin_emb, cos_emb)


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    # Taken from: https://github.com/facebookresearch/capi/blob/main/model.py
    (x1, x2) = x.chunk(2, dim=-1)
    return torch.concat((-x2, x1), dim=-1)


def rotate_half_interleaved(x: torch.Tensor) -> torch.Tensor:
    return torch.stack([-x[..., 1::2], x[..., ::2]], dim=-1).reshape(x.size())


def apply_rotary_pos_embed(x: torch.Tensor, embed: torch.Tensor) -> torch.Tensor:
    (sin_emb, cos_emb) = embed.tensor_split(2, dim=-1)
    if cos_emb.ndim == 3:
        return x * cos_emb.unsqueeze(1).expand_as(x) + rotate_half(x) * sin_emb.unsqueeze(1).expand_as(x)

    return x * cos_emb + rotate_half(x) * sin_emb


def apply_interleaved_rotary_pos_embed(x: torch.Tensor, embed: torch.Tensor) -> torch.Tensor:
    (sin_emb, cos_emb) = embed.tensor_split(2, dim=-1)
    if cos_emb.ndim == 3:
        return x * cos_emb.unsqueeze(1).expand_as(x) + rotate_half_interleaved(x) * sin_emb.unsqueeze(1).expand_as(x)

    return x * cos_emb + rotate_half_interleaved(x) * sin_emb


class SequentialWithRope(nn.Sequential):
    def forward(self, x: torch.Tensor, rope: torch.Tensor) -> torch.Tensor:  # pylint: disable=arguments-differ
        for module in self:
            x = module(x, rope)

        return x


class RoPE(nn.Module):
    def __init__(
        self,
        dim: int,
        temperature: float,
        grid_size: tuple[int, int],
        grid_indexing: Literal["ij", "xy"],
        grid_offset: int,
        pt_grid_size: Optional[tuple[int, int]] = None,
        rope_rot_type: str = "standard",
    ) -> None:
        super().__init__()
        if rope_rot_type == "standard":
            self.apply_fn = apply_rotary_pos_embed
        elif rope_rot_type == "interleaved":
            self.apply_fn = apply_interleaved_rotary_pos_embed
        else:
            raise ValueError(f"Unknown rope_rot_type, got '{rope_rot_type}'")

        (sin_emb, cos_emb) = build_rotary_pos_embed(
            dim,
            temperature,
            grid_size=grid_size,
            grid_indexing=grid_indexing,
            grid_offset=grid_offset,
            pt_grid_size=pt_grid_size,
        )
        self.pos_embed = nn.Buffer(torch.concat((sin_emb, cos_emb), dim=-1), persistent=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.apply_fn(x, self.pos_embed)


class RoPEAttention(nn.Module):
    def __init__(
        self,
        dim: int,
        num_heads: int,
        attn_drop: float,
        proj_drop: float,
        num_special_tokens: int,
        rope_rot_type: str = "standard",
    ) -> None:
        super().__init__()
        assert dim % num_heads == 0, "dim should be divisible by num_heads"
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        self.scale = self.head_dim**-0.5
        self.num_special_tokens = num_special_tokens
        if rope_rot_type == "standard":
            self.apply_rot_fn = apply_rotary_pos_embed
        elif rope_rot_type == "interleaved":
            self.apply_rot_fn = apply_interleaved_rotary_pos_embed
        else:
            raise ValueError(f"Unknown rope_rot_type, got '{rope_rot_type}'")

        self.qkv = nn.Linear(dim, dim * 3)
        self.attn_drop = nn.Dropout(attn_drop)
        self.proj = nn.Linear(dim, dim)
        self.proj_drop = nn.Dropout(proj_drop)

    def forward(self, x: torch.Tensor, rope: torch.Tensor) -> torch.Tensor:
        (B, N, C) = x.size()
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        (q, k, v) = qkv.unbind(0)

        n = self.num_special_tokens
        q = torch.concat([q[:, :, :n, :], self.apply_rot_fn(q[:, :, n:, :], rope)], dim=2)
        k = torch.concat([k[:, :, :n, :], self.apply_rot_fn(k[:, :, n:, :], rope)], dim=2)

        x = F.scaled_dot_product_attention(  # pylint: disable=not-callable
            q, k, v, dropout_p=self.attn_drop.p if self.training else 0.0, scale=self.scale
        )

        x = x.transpose(1, 2).reshape(B, N, C)
        x = self.proj(x)
        x = self.proj_drop(x)

        return x


class EncoderBlock(nn.Module):
    def __init__(
        self,
        num_heads: int,
        hidden_dim: int,
        mlp_dim: Optional[int],
        num_special_tokens: int,
        dropout: float,
        attention_dropout: float,
        drop_path: float,
        activation_layer: Callable[..., nn.Module],
        layer_scale_init_value: Optional[float] = None,
        norm_layer: Callable[..., nn.Module] = nn.LayerNorm,
        norm_layer_eps: float = 1e-6,
        mlp_layer: Callable[..., nn.Module] = FFN,
        rope_rot_type: str = "standard",
    ) -> None:
        super().__init__()

        if mlp_dim is None:
            mlp_dim = hidden_dim * 4

        # Attention block
        self.norm1 = norm_layer(hidden_dim, eps=norm_layer_eps)
        self.attn = RoPEAttention(
            hidden_dim,
            num_heads,
            attn_drop=attention_dropout,
            proj_drop=dropout,
            num_special_tokens=num_special_tokens,
            rope_rot_type=rope_rot_type,
        )
        if layer_scale_init_value is not None:
            self.layer_scale_1 = LayerScale(hidden_dim, layer_scale_init_value)
        else:
            self.layer_scale_1 = nn.Identity()

        # MLP block
        self.norm2 = norm_layer(hidden_dim, eps=norm_layer_eps)
        self.mlp = mlp_layer(hidden_dim, mlp_dim, act_layer=activation_layer, dropout=dropout)
        self.drop_path = StochasticDepth(drop_path, mode="row")
        if layer_scale_init_value is not None:
            self.layer_scale_2 = LayerScale(hidden_dim, layer_scale_init_value)
        else:
            self.layer_scale_2 = nn.Identity()

    def forward(self, x: torch.Tensor, rope: torch.Tensor) -> torch.Tensor:
        x = x + self.drop_path(self.layer_scale_1(self.attn(self.norm1(x), rope)))
        x = x + self.drop_path(self.layer_scale_2(self.mlp(self.norm2(x))))

        return x


class Encoder(nn.Module):
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        num_layers: int,
        num_heads: int,
        hidden_dim: int,
        mlp_dim: int,
        num_special_tokens: int,
        dropout: float,
        attention_dropout: float,
        dpr: list[float],
        pre_norm: bool = False,
        activation_layer: Callable[..., nn.Module] = nn.GELU,
        layer_scale_init_value: Optional[float] = None,
        norm_layer: Callable[..., nn.Module] = nn.LayerNorm,
        norm_layer_eps: float = 1e-6,
        mlp_layer: Callable[..., nn.Module] = FFN,
        rope_rot_type: str = "standard",
    ) -> None:
        super().__init__()
        pre_layers = []
        if dropout > 0.0:
            pre_layers.append(nn.Dropout(dropout))
        if pre_norm is True:
            pre_layers.append(norm_layer(hidden_dim, eps=norm_layer_eps))

        self.pre_block = nn.Sequential(*pre_layers)

        layers = []
        for i in range(num_layers):
            layers.append(
                EncoderBlock(
                    num_heads,
                    hidden_dim,
                    mlp_dim,
                    num_special_tokens,
                    dropout,
                    attention_dropout,
                    dpr[i],
                    activation_layer=activation_layer,
                    layer_scale_init_value=layer_scale_init_value,
                    norm_layer=norm_layer,
                    norm_layer_eps=norm_layer_eps,
                    mlp_layer=mlp_layer,
                    rope_rot_type=rope_rot_type,
                )
            )

        self.block = SequentialWithRope(*layers)

    def forward(self, x: torch.Tensor, rope: torch.Tensor) -> torch.Tensor:
        x = self.pre_block(x)
        return self.block(x, rope)

    def forward_features(self, x: torch.Tensor, rope: torch.Tensor) -> list[torch.Tensor]:
        x = self.pre_block(x)

        xs = []
        for blk in self.block:
            x = blk(x, rope)
            xs.append(x)

        return xs


class MAEDecoderBlock(nn.Module):
    def __init__(
        self,
        num_heads: int,
        hidden_dim: int,
        num_special_tokens: int,
        activation_layer: Callable[..., nn.Module],
        grid_size: tuple[int, int],
        rope_grid_indexing: Literal["ij", "xy"],
        rope_grid_offset: int,
        rope_temperature: float,
        layer_scale_init_value: Optional[float] = None,
        norm_layer: Callable[..., nn.Module] = nn.LayerNorm,
        mlp_layer: Callable[..., nn.Module] = FFN,
        rope_rot_type: str = "standard",
    ) -> None:
        super().__init__()
        mlp_dim = hidden_dim * 4
        self.rope = RoPE(
            hidden_dim // num_heads,
            temperature=rope_temperature,
            grid_size=grid_size,
            grid_indexing=rope_grid_indexing,
            grid_offset=rope_grid_offset,
            rope_rot_type=rope_rot_type,
        )

        # Attention block
        self.norm1 = norm_layer(hidden_dim, eps=1e-6)
        self.attn = RoPEAttention(
            hidden_dim,
            num_heads,
            attn_drop=0.0,
            proj_drop=0.0,
            num_special_tokens=num_special_tokens,
            rope_rot_type=rope_rot_type,
        )
        if layer_scale_init_value is not None:
            self.layer_scale_1 = LayerScale(hidden_dim, layer_scale_init_value)
        else:
            self.layer_scale_1 = nn.Identity()

        # MLP block
        self.norm2 = norm_layer(hidden_dim, eps=1e-6)
        self.mlp = mlp_layer(hidden_dim, mlp_dim, act_layer=activation_layer, dropout=0.0)
        if layer_scale_init_value is not None:
            self.layer_scale_2 = LayerScale(hidden_dim, layer_scale_init_value)
        else:
            self.layer_scale_2 = nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.layer_scale_1(self.attn(self.norm1(x), self.rope.pos_embed))
        x = x + self.layer_scale_2(self.mlp(self.norm2(x)))

        return x


# pylint: disable=invalid-name,too-many-instance-attributes
class RoPE_ViT(DetectorBackbone, PreTrainEncoder, MaskedTokenOmissionMixin, MaskedTokenRetentionMixin):
    block_group_regex = r"encoder\.block\.(\d+)"

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
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

        image_size = self.size
        attention_dropout = 0.0
        dropout = 0.0
        pos_embed_special_tokens: bool = self.config.get("pos_embed_special_tokens", True)
        patch_size: int = self.config["patch_size"]
        num_layers: int = self.config["num_layers"]
        num_heads: int = self.config["num_heads"]
        hidden_dim: int = self.config["hidden_dim"]
        mlp_dim: int = self.config["mlp_dim"]
        layer_scale_init_value: Optional[float] = self.config.get("layer_scale_init_value", None)
        pre_norm: bool = self.config.get("pre_norm", False)
        post_norm: bool = self.config.get("post_norm", True)
        num_reg_tokens: int = self.config.get("num_reg_tokens", 0)
        class_token: bool = self.config.get("class_token", True)
        attn_pool_head: bool = self.config.get("attn_pool_head", False)
        attn_pool_num_heads: Optional[int] = self.config.get("attn_pool_num_heads", None)
        attn_pool_special_tokens: bool = self.config.get("attn_pool_special_tokens", False)
        norm_layer_type: str = self.config.get("norm_layer_type", "LayerNorm")
        norm_layer_eps: float = self.config.get("norm_layer_eps", 1e-6)
        mlp_layer_type: str = self.config.get("mlp_layer_type", "FFN")
        act_layer_type: Optional[str] = self.config.get("act_layer_type", None)  # Default according to mlp type
        rope_rot_type: Literal["standard", "interleaved"] = self.config.get("rope_rot_type", "standard")
        rope_grid_indexing: Literal["ij", "xy"] = self.config.get("rope_grid_indexing", "ij")
        rope_grid_offset: int = self.config.get("rope_grid_offset", 0)
        rope_temperature: float = self.config.get("rope_temperature", 100.0)
        pt_grid_size: Optional[tuple[int, int]] = self.config.get("pt_grid_size", None)
        drop_path_rate: float = self.config["drop_path_rate"]

        if norm_layer_type == "LayerNorm":
            norm_layer = nn.LayerNorm
        elif norm_layer_type == "RMSNorm":
            norm_layer = nn.RMSNorm
        else:
            raise ValueError(f"Unknown norm_layer_type '{norm_layer_type}'")

        if mlp_layer_type == "FFN":
            mlp_layer = FFN
            act_layer = nn.GELU
        elif mlp_layer_type == "SwiGLU_FFN":
            mlp_layer = SwiGLU_FFN
            act_layer = nn.SiLU
        else:
            raise ValueError(f"Unknown mlp_layer_type '{mlp_layer_type}'")

        if act_layer_type is not None:
            act_layer = get_activation_module(act_layer_type)

        torch._assert(image_size[0] % patch_size == 0, "Input shape indivisible by patch size!")
        torch._assert(image_size[1] % patch_size == 0, "Input shape indivisible by patch size!")
        torch._assert(hidden_dim % num_heads == 0, "Hidden dim indivisible by num heads!")
        self.pos_embed_special_tokens = pos_embed_special_tokens
        self.patch_size = patch_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.hidden_dim = hidden_dim
        self.layer_scale_init_value = layer_scale_init_value
        self.num_reg_tokens = num_reg_tokens
        self.attn_pool_special_tokens = attn_pool_special_tokens
        self.norm_layer = norm_layer
        self.mlp_layer = mlp_layer
        self.act_layer = act_layer
        self.rope_rot_type = rope_rot_type
        self.rope_grid_indexing = rope_grid_indexing
        self.rope_grid_offset = rope_grid_offset
        self.rope_temperature = rope_temperature

        # Cast in case config was loaded from a json (no tuples),
        # TorchScript does not accept a list when tuple expected
        if isinstance(pt_grid_size, list):
            pt_grid_size = tuple(pt_grid_size)  # type: ignore[unreachable]

        self.pt_grid_size = pt_grid_size
        dpr = [x.item() for x in torch.linspace(0, drop_path_rate, num_layers)]  # Stochastic depth decay rule

        self.conv_proj = nn.Conv2d(
            self.input_channels,
            hidden_dim,
            kernel_size=(patch_size, patch_size),
            stride=(patch_size, patch_size),
            padding=(0, 0),
            bias=not pre_norm,
        )
        self.patch_embed = PatchEmbed()

        seq_length = (image_size[0] // patch_size) * (image_size[1] // patch_size)
        self.num_special_tokens = 0

        # Add a class token
        if class_token is True:
            self.class_token = nn.Parameter(torch.zeros(1, 1, hidden_dim))
            self.num_special_tokens += 1
            if pos_embed_special_tokens is True:
                seq_length += 1
        else:
            self.class_token = None

        # Add optional register tokens
        if self.num_reg_tokens > 0:
            self.reg_tokens = nn.Parameter(torch.zeros(1, self.num_reg_tokens, hidden_dim))
            self.num_special_tokens += self.num_reg_tokens
            if pos_embed_special_tokens is True:
                seq_length += self.num_reg_tokens
        else:
            self.reg_tokens = None

        # Add positional embedding
        self.pos_embedding = nn.Parameter(torch.empty(1, seq_length, hidden_dim).normal_(std=0.02))

        # RoPE
        self.rope = RoPE(
            hidden_dim // num_heads,
            temperature=self.rope_temperature,
            grid_size=(image_size[0] // patch_size, image_size[1] // patch_size),
            grid_indexing=rope_grid_indexing,
            grid_offset=rope_grid_offset,
            pt_grid_size=self.pt_grid_size,
            rope_rot_type=rope_rot_type,
        )

        # Encoder
        self.encoder = Encoder(
            num_layers,
            num_heads,
            hidden_dim,
            mlp_dim,
            self.num_special_tokens,
            dropout,
            attention_dropout,
            dpr,
            pre_norm=pre_norm,
            activation_layer=act_layer,
            layer_scale_init_value=layer_scale_init_value,
            norm_layer=norm_layer,
            norm_layer_eps=norm_layer_eps,
            mlp_layer=mlp_layer,
            rope_rot_type=rope_rot_type,
        )

        if post_norm is True:
            self.norm = norm_layer(hidden_dim, eps=norm_layer_eps)
        else:
            self.norm = nn.Identity()

        if attn_pool_head is False:
            self.attn_pool = None
        else:
            if attn_pool_num_heads is None:
                attn_pool_num_heads = num_heads

            self.attn_pool = MultiHeadAttentionPool(hidden_dim, attn_pool_num_heads, mlp_dim, qkv_bias=True)

        self.return_stages = ["neck"]  # Actually meaningless, just for completeness
        self.return_channels = [hidden_dim]
        self.embedding_size = hidden_dim
        self.classifier = self.create_classifier()

        self.max_stride = patch_size
        self.stem_stride = patch_size
        self.stem_width = hidden_dim
        self.encoding_size = hidden_dim
        self.decoder_block = partial(
            MAEDecoderBlock,
            16,
            num_special_tokens=self.num_special_tokens,
            activation_layer=act_layer,
            grid_size=(image_size[0] // patch_size, image_size[1] // patch_size),
            rope_grid_indexing=rope_grid_indexing,
            rope_grid_offset=rope_grid_offset,
            rope_temperature=rope_temperature,
            layer_scale_init_value=layer_scale_init_value,
            norm_layer=norm_layer,
            mlp_layer=mlp_layer,
            rope_rot_type=rope_rot_type,
        )

        # Weight initialization
        if isinstance(self.conv_proj, nn.Conv2d):
            # Init the patchify stem
            fan_in = self.conv_proj.in_channels * self.conv_proj.kernel_size[0] * self.conv_proj.kernel_size[1]
            nn.init.trunc_normal_(self.conv_proj.weight, std=math.sqrt(1 / fan_in))
            if self.conv_proj.bias is not None:
                nn.init.zeros_(self.conv_proj.bias)

        if isinstance(self.classifier, nn.Linear):
            nn.init.zeros_(self.classifier.weight)
            nn.init.zeros_(self.classifier.bias)

    def _get_pos_embed(self, H: int, W: int) -> torch.Tensor:
        if self.dynamic_size is False:
            return self.pos_embedding

        if H == self.size[0] and W == self.size[1]:
            return self.pos_embedding

        return adjust_position_embedding(
            self.pos_embedding,
            (self.size[0] // self.patch_size, self.size[1] // self.patch_size),
            (H // self.patch_size, W // self.patch_size),
            self.num_special_tokens if self.pos_embed_special_tokens is True else 0,
            antialias=False,
        )

    def _get_rope_embed(self, H: int, W: int) -> torch.Tensor:
        if self.dynamic_size is False:
            return self.rope.pos_embed

        if H == self.size[0] and W == self.size[1]:
            return self.rope.pos_embed

        return torch.concat(
            build_rotary_pos_embed(
                self.hidden_dim // self.num_heads,
                self.rope_temperature,
                grid_size=(H // self.patch_size, W // self.patch_size),
                grid_indexing=self.rope_grid_indexing,
                grid_offset=self.rope_grid_offset,
                pt_grid_size=self.pt_grid_size,
            ),
            dim=-1,
        ).to(self.rope.pos_embed.device)

    def freeze(self, freeze_classifier: bool = True, unfreeze_features: bool = False) -> None:
        for param in self.parameters():
            param.requires_grad = False

        if freeze_classifier is False:
            for param in self.classifier.parameters():
                param.requires_grad = True

        if unfreeze_features is True:
            if self.attn_pool is not None:
                for param in self.attn_pool.parameters():
                    param.requires_grad = True

    def detection_features(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        (H, W) = x.shape[-2:]
        x = self.conv_proj(x)
        x = self.patch_embed(x)

        if self.pos_embed_special_tokens is False:
            x = x + self._get_pos_embed(H, W)

        # Expand the class token to the full batch
        if self.class_token is not None:
            batch_class_token = self.class_token.expand(x.shape[0], -1, -1)
            x = torch.concat([batch_class_token, x], dim=1)

        # Expand the register tokens to the full batch
        if self.reg_tokens is not None:
            batch_reg_tokens = self.reg_tokens.expand(x.shape[0], -1, -1)
            x = torch.concat([batch_reg_tokens, x], dim=1)

        if self.pos_embed_special_tokens is True:
            x = x + self._get_pos_embed(H, W)

        x = self.encoder(x, self._get_rope_embed(H, W))
        x = self.norm(x)

        x = x[:, self.num_special_tokens :]
        x = x.permute(0, 2, 1)
        (B, C, _) = x.size()
        x = x.reshape(B, C, H // self.patch_size, W // self.patch_size)

        return {self.return_stages[0]: x}

    def freeze_stages(self, up_to_stage: int) -> None:
        for param in self.conv_proj.parameters():
            param.requires_grad = False

        self.pos_embedding.requires_grad = False

        for idx, module in enumerate(self.encoder.children()):
            if idx >= up_to_stage:
                break

            for param in module.parameters():
                param.requires_grad = False

    def masked_encoding_omission(
        self,
        x: torch.Tensor,
        ids_keep: Optional[torch.Tensor] = None,
        return_all_features: bool = False,
        return_keys: Literal["all", "tokens", "embedding"] = "tokens",
    ) -> TokenOmissionResultType:
        (H, W) = x.shape[-2:]

        # Reshape and permute the input tensor
        x = self.conv_proj(x)
        x = self.patch_embed(x)

        # Add pos embedding without special tokens
        pos_embedding = self._get_pos_embed(H, W)
        if self.pos_embed_special_tokens is True:
            x = x + pos_embedding[:, self.num_special_tokens :, :]
        else:
            x = x + pos_embedding

        # Mask tokens
        if ids_keep is not None:
            x = torch.gather(x, dim=1, index=ids_keep.unsqueeze(-1).repeat(1, 1, x.size(2)))

            rope_dim = self.rope.pos_embed.size(1)
            rope = self.rope.pos_embed.unsqueeze(0).repeat(x.size(0), 1, 1)
            rope_masked = torch.gather(rope, dim=1, index=ids_keep.unsqueeze(-1).repeat(1, 1, rope_dim))
        else:
            rope_masked = self.rope.pos_embed

        # Append class and register tokens
        if self.class_token is not None:
            if self.pos_embed_special_tokens is True:
                cls_token = self.class_token + pos_embedding[:, self.num_reg_tokens : self.num_reg_tokens + 1, :]
            else:
                cls_token = self.class_token

            batch_class_token = cls_token.expand(x.shape[0], -1, -1)
            x = torch.concat((batch_class_token, x), dim=1)

        if self.reg_tokens is not None:
            if self.pos_embed_special_tokens is True:
                reg_tokens = self.reg_tokens + pos_embedding[:, 0 : self.num_reg_tokens, :]
            else:
                reg_tokens = self.reg_tokens

            batch_reg_tokens = reg_tokens.expand(x.shape[0], -1, -1)
            x = torch.concat([batch_reg_tokens, x], dim=1)

        # Apply transformer
        if return_all_features is True:
            xs = self.encoder.forward_features(x, rope_masked)
            xs[-1] = self.norm(xs[-1])
            x = torch.stack(xs, dim=-1)
        else:
            x = self.encoder(x, rope_masked)
            x = self.norm(x)

        result: TokenOmissionResultType = {}
        if return_keys in ("all", "tokens"):
            result["tokens"] = x

        if return_keys in ("all", "embedding"):
            if return_all_features is True:
                x = x[..., -1]

            if self.attn_pool is not None:
                if self.attn_pool_special_tokens is False:
                    x = x[:, self.num_special_tokens :]

                x = self.attn_pool(x)
                result["embedding"] = x[:, 0]
            elif self.class_token is None:
                x = x[:, self.num_special_tokens :]
                result["embedding"] = x.mean(dim=1)
            else:
                result["embedding"] = x[:, self.num_reg_tokens]

        return result

    def masked_encoding_retention(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
        mask_token: Optional[torch.Tensor] = None,
        return_keys: Literal["all", "features", "embedding"] = "features",
    ) -> TokenRetentionResultType:
        (H, W) = x.shape[-2:]

        x = self.conv_proj(x)
        x = mask_tensor(x, mask, mask_token=mask_token, patch_factor=self.max_stride // self.stem_stride)

        # Reshape and permute the input tensor
        x = self.patch_embed(x)

        if self.pos_embed_special_tokens is False:
            x = x + self._get_pos_embed(H, W)

        # Expand the class token to the full batch
        if self.class_token is not None:
            batch_class_token = self.class_token.expand(x.shape[0], -1, -1)
            x = torch.concat([batch_class_token, x], dim=1)

        # Expand the register tokens to the full batch
        if self.reg_tokens is not None:
            batch_reg_tokens = self.reg_tokens.expand(x.shape[0], -1, -1)
            x = torch.concat([batch_reg_tokens, x], dim=1)

        if self.pos_embed_special_tokens is True:
            x = x + self._get_pos_embed(H, W)

        x = self.encoder(x, self._get_rope_embed(H, W))
        x = self.norm(x)

        result: TokenRetentionResultType = {}
        if return_keys in ("all", "features"):
            features = x[:, self.num_special_tokens :]
            features = features.permute(0, 2, 1)
            (B, C, _) = features.size()
            features = features.reshape(B, C, H // self.patch_size, W // self.patch_size)
            result["features"] = features

        if return_keys in ("all", "embedding"):
            if self.attn_pool is not None:
                if self.attn_pool_special_tokens is False:
                    x = x[:, self.num_special_tokens :]

                x = self.attn_pool(x)
                result["embedding"] = x[:, 0]
            elif self.class_token is None:
                x = x[:, self.num_special_tokens :]
                result["embedding"] = x.mean(dim=1)
            else:
                result["embedding"] = x[:, self.num_reg_tokens]

        return result

    def forward_features(self, x: torch.Tensor) -> torch.Tensor:
        (H, W) = x.shape[-2:]

        # Reshape and permute the input tensor
        x = self.conv_proj(x)
        x = self.patch_embed(x)

        if self.pos_embed_special_tokens is False:
            x = x + self._get_pos_embed(H, W)

        # Expand the class token to the full batch
        if self.class_token is not None:
            batch_class_token = self.class_token.expand(x.shape[0], -1, -1)
            x = torch.concat([batch_class_token, x], dim=1)

        # Expand the register tokens to the full batch
        if self.reg_tokens is not None:
            batch_reg_tokens = self.reg_tokens.expand(x.shape[0], -1, -1)
            x = torch.concat([batch_reg_tokens, x], dim=1)

        if self.pos_embed_special_tokens is True:
            x = x + self._get_pos_embed(H, W)

        x = self.encoder(x, self._get_rope_embed(H, W))
        x = self.norm(x)

        return x

    def embedding(self, x: torch.Tensor) -> torch.Tensor:
        x = self.forward_features(x)

        if self.attn_pool is not None:
            if self.attn_pool_special_tokens is False:
                x = x[:, self.num_special_tokens :]

            x = self.attn_pool(x)
            return x[:, 0]

        if self.class_token is None:
            x = x[:, self.num_special_tokens :]
            return x.mean(dim=1)

        # Classifier "token" as used by standard language architectures
        return x[:, self.num_reg_tokens]

    def adjust_size(self, new_size: tuple[int, int]) -> None:
        if new_size == self.size:
            return

        assert new_size[0] % self.patch_size == 0, "Input shape indivisible by patch size!"
        assert new_size[1] % self.patch_size == 0, "Input shape indivisible by patch size!"

        old_size = self.size
        super().adjust_size(new_size)

        if self.pos_embed_special_tokens is True:
            num_prefix_tokens = self.num_special_tokens
        else:
            num_prefix_tokens = 0

        # Add back class tokens
        self.pos_embedding = nn.Parameter(
            adjust_position_embedding(
                self.pos_embedding,
                (old_size[0] // self.patch_size, old_size[1] // self.patch_size),
                (new_size[0] // self.patch_size, new_size[1] // self.patch_size),
                num_prefix_tokens,
            )
        )

        # Adjust RoPE
        self.rope = RoPE(
            self.hidden_dim // self.num_heads,
            temperature=self.rope_temperature,
            grid_size=(new_size[0] // self.patch_size, new_size[1] // self.patch_size),
            grid_indexing=self.rope_grid_indexing,
            grid_offset=self.rope_grid_offset,
            pt_grid_size=self.pt_grid_size,
            rope_rot_type=self.rope_rot_type,
        )

        # Define adjusted decoder block
        self.decoder_block = partial(
            MAEDecoderBlock,
            16,
            num_special_tokens=self.num_special_tokens,
            activation_layer=self.act_layer,
            grid_size=(new_size[0] // self.patch_size, new_size[1] // self.patch_size),
            rope_grid_indexing=self.rope_grid_indexing,
            rope_grid_offset=self.rope_grid_offset,
            rope_temperature=self.rope_temperature,
            layer_scale_init_value=self.layer_scale_init_value,
            norm_layer=self.norm_layer,
            mlp_layer=self.mlp_layer,
            rope_rot_type=self.rope_rot_type,
        )


# Vision Transformer Model Naming Convention
# ==========================================
#
# Model names follow a structured pattern to encode architectural choices:
# [rope_]vit_[reg{N}_][size][patch_size][_components][_pooling][_c{N}]
#
# Core Components:
# - rope_       : Rotary Position Embedding (RoPE) enabled
# - rope_i_     : Rotary Position Embedding (RoPE) enabled with interleaved rotation - implies different temp, indexing
# - vit_        : Vision Transformer base architecture
# - reg{N}_     : Register tokens (N = number of register tokens, e.g., reg4, reg8)
# - size        : Model size (s=small, b=base, l=large, or specific like so150m)
# - patch_size  : Patch size (e.g., 14, 16, 32 for 14x14, 16x16, 32x32 patches)
#
# Optional Components:
#     Position Embeddings:
#     - nps         : No Position embedding on Special tokens
#
#     Normalization:
#     - rms         : RMSNorm (instead of LayerNorm)
#     - pn          : Pre-Norm (layer norm before the encoder) - implies different norm eps
#     - npn         : No Post Norm (disables post-normalization layer)
#
#     Feed-Forward Network:
#     - swiglu      : SwiGLU FFN layer type (instead of standard FFN)
#
#     Activation:
#     - quick_gelu  : QuickGELU activation type
#     - ...
#
#     Regularization:
#     - ls          : Layer Scaling applied
#
#     Pooling/Reduction:
#     - avg         : Average pooling for sequence reduction
#     - ap          : Attention Pooling for sequence reduction
#     - aps         : Attention Pooling inc. Special tokens for sequence reduction
#
#     Custom Variants:
#     - c{N}        : Custom variant (N = version number) for models with fine-grained or non-standard
#                     modifications not fully reflected in the name

registry.register_model_config(
    "rope_vit_s32",
    RoPE_ViT,
    config={
        "patch_size": 32,
        "num_layers": 12,
        "num_heads": 6,
        "hidden_dim": 384,
        "mlp_dim": 1536,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_s16",
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 12,
        "num_heads": 6,
        "hidden_dim": 384,
        "mlp_dim": 1536,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_i_vit_s16_pn_aps_c1",  # For PE Core - https://arxiv.org/abs/2504.13181
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 12,
        "num_heads": 6,
        "hidden_dim": 384,
        "mlp_dim": 1536,
        "pre_norm": True,
        "attn_pool_head": True,
        "attn_pool_num_heads": 8,
        "attn_pool_special_tokens": True,
        "norm_layer_eps": 1e-5,
        "rope_rot_type": "interleaved",
        "rope_grid_indexing": "xy",
        "rope_grid_offset": 1,
        "rope_temperature": 10000.0,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_s14",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 12,
        "num_heads": 6,
        "hidden_dim": 384,
        "mlp_dim": 1536,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_m32",
    RoPE_ViT,
    config={
        "patch_size": 32,
        "num_layers": 12,
        "num_heads": 8,
        "hidden_dim": 512,
        "mlp_dim": 2048,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_m16",
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 12,
        "num_heads": 8,
        "hidden_dim": 512,
        "mlp_dim": 2048,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_m14",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 12,
        "num_heads": 8,
        "hidden_dim": 512,
        "mlp_dim": 2048,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_b32",
    RoPE_ViT,
    config={
        "patch_size": 32,
        "num_layers": 12,
        "num_heads": 12,
        "hidden_dim": 768,
        "mlp_dim": 3072,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_b16",
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 12,
        "num_heads": 12,
        "hidden_dim": 768,
        "mlp_dim": 3072,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_i_vit_b16_pn_aps_c1",  # For PE Core - https://arxiv.org/abs/2504.13181
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 12,
        "num_heads": 12,
        "hidden_dim": 768,
        "mlp_dim": 3072,
        "pre_norm": True,
        "attn_pool_head": True,
        "attn_pool_num_heads": 8,
        "attn_pool_special_tokens": True,
        "norm_layer_eps": 1e-5,
        "rope_rot_type": "interleaved",
        "rope_grid_indexing": "xy",
        "rope_grid_offset": 1,
        "rope_temperature": 10000.0,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_b14",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 12,
        "num_heads": 12,
        "hidden_dim": 768,
        "mlp_dim": 3072,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_l32",
    RoPE_ViT,
    config={
        "patch_size": 32,
        "num_layers": 24,
        "num_heads": 16,
        "hidden_dim": 1024,
        "mlp_dim": 4096,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_l16",
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 24,
        "num_heads": 16,
        "hidden_dim": 1024,
        "mlp_dim": 4096,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_l14",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 24,
        "num_heads": 16,
        "hidden_dim": 1024,
        "mlp_dim": 4096,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_i_vit_l14_pn_aps_c1",  # For PE Core - https://arxiv.org/abs/2504.13181
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 24,
        "num_heads": 16,
        "hidden_dim": 1024,
        "mlp_dim": 4096,
        "pre_norm": True,
        "attn_pool_head": True,
        "attn_pool_num_heads": 8,
        "attn_pool_special_tokens": True,
        "norm_layer_eps": 1e-5,
        "rope_rot_type": "interleaved",
        "rope_grid_indexing": "xy",
        "rope_grid_offset": 1,
        "rope_temperature": 10000.0,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_h16",
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 32,
        "num_heads": 16,
        "hidden_dim": 1280,
        "mlp_dim": 5120,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_h14",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 32,
        "num_heads": 16,
        "hidden_dim": 1280,
        "mlp_dim": 5120,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(  # From "Scaling Vision Transformers"
    "rope_vit_g14",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 40,
        "num_heads": 16,
        "hidden_dim": 1408,
        "mlp_dim": 6144,
        "drop_path_rate": 0.1,
    },
)

# With registers
registry.register_model_config(
    "rope_vit_reg1_s32",
    RoPE_ViT,
    config={
        "patch_size": 32,
        "num_layers": 12,
        "num_heads": 6,
        "hidden_dim": 384,
        "mlp_dim": 1536,
        "num_reg_tokens": 1,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_reg1_s16",
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 12,
        "num_heads": 6,
        "hidden_dim": 384,
        "mlp_dim": 1536,
        "num_reg_tokens": 1,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_i_vit_reg1_s16_pn_npn_avg_c1",  # For PE Spatial - https://arxiv.org/abs/2504.13181
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 12,
        "num_heads": 6,
        "hidden_dim": 384,
        "mlp_dim": 1536,
        "num_reg_tokens": 1,
        "class_token": False,
        "pre_norm": True,
        "post_norm": False,
        "norm_layer_eps": 1e-5,
        "rope_rot_type": "interleaved",
        "rope_grid_indexing": "xy",
        "rope_grid_offset": 1,
        "rope_temperature": 10000.0,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_reg1_s14",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 12,
        "num_heads": 6,
        "hidden_dim": 384,
        "mlp_dim": 1536,
        "num_reg_tokens": 1,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_reg4_m32",
    RoPE_ViT,
    config={
        "patch_size": 32,
        "num_layers": 12,
        "num_heads": 8,
        "hidden_dim": 512,
        "mlp_dim": 2048,
        "num_reg_tokens": 4,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_reg4_m16",
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 12,
        "num_heads": 8,
        "hidden_dim": 512,
        "mlp_dim": 2048,
        "num_reg_tokens": 4,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_reg4_m16_rms_avg",
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 12,
        "num_heads": 8,
        "hidden_dim": 512,
        "mlp_dim": 2048,
        "num_reg_tokens": 4,
        "class_token": False,
        "norm_layer_type": "RMSNorm",
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_reg4_m14",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 12,
        "num_heads": 8,
        "hidden_dim": 512,
        "mlp_dim": 2048,
        "num_reg_tokens": 4,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_reg4_b32",
    RoPE_ViT,
    config={
        "patch_size": 32,
        "num_layers": 12,
        "num_heads": 12,
        "hidden_dim": 768,
        "mlp_dim": 3072,
        "num_reg_tokens": 4,
        "drop_path_rate": 0.0,
    },
)
registry.register_model_config(
    "rope_vit_reg4_b16",
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 12,
        "num_heads": 12,
        "hidden_dim": 768,
        "mlp_dim": 3072,
        "num_reg_tokens": 4,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg4_b14",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 12,
        "num_heads": 12,
        "hidden_dim": 768,
        "mlp_dim": 3072,
        "num_reg_tokens": 4,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg8_nps_b14_ap",
    RoPE_ViT,
    config={
        "pos_embed_special_tokens": False,
        "patch_size": 14,
        "num_layers": 12,
        "num_heads": 12,
        "hidden_dim": 768,
        "mlp_dim": 3072,
        "num_reg_tokens": 8,
        "class_token": False,
        "attn_pool_head": True,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg4_l32",
    RoPE_ViT,
    config={
        "patch_size": 32,
        "num_layers": 24,
        "num_heads": 16,
        "hidden_dim": 1024,
        "mlp_dim": 4096,
        "num_reg_tokens": 4,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg4_l16",
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 24,
        "num_heads": 16,
        "hidden_dim": 1024,
        "mlp_dim": 4096,
        "num_reg_tokens": 4,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg4_l14",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 24,
        "num_heads": 16,
        "hidden_dim": 1024,
        "mlp_dim": 4096,
        "num_reg_tokens": 4,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg8_l14_ap",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 24,
        "num_heads": 16,
        "hidden_dim": 1024,
        "mlp_dim": 4096,
        "num_reg_tokens": 8,
        "class_token": False,
        "attn_pool_head": True,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg8_l14_rms_ap",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 24,
        "num_heads": 16,
        "hidden_dim": 1024,
        "mlp_dim": 4096,
        "num_reg_tokens": 8,
        "class_token": False,
        "attn_pool_head": True,
        "norm_layer_type": "RMSNorm",
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg4_h16",
    RoPE_ViT,
    config={
        "patch_size": 16,
        "num_layers": 32,
        "num_heads": 16,
        "hidden_dim": 1280,
        "mlp_dim": 5120,
        "num_reg_tokens": 4,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg4_h14",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 32,
        "num_heads": 16,
        "hidden_dim": 1280,
        "mlp_dim": 5120,
        "num_reg_tokens": 4,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(  # From "Scaling Vision Transformers"
    "rope_vit_reg4_g14",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 40,
        "num_heads": 16,
        "hidden_dim": 1408,
        "mlp_dim": 6144,
        "num_reg_tokens": 4,
        "drop_path_rate": 0.1,
    },
)

# Shape-optimized vision transformer (SoViT)
registry.register_model_config(
    "rope_vit_so150m_p14_ap",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 18,
        "num_heads": 16,
        "hidden_dim": 896,  # Changed from 880 for RoPE divisibility
        "mlp_dim": 2320,
        "class_token": False,
        "attn_pool_head": True,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_so400m_p14_ap",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 27,
        "num_heads": 16,
        "hidden_dim": 1152,
        "mlp_dim": 4304,
        "class_token": False,
        "attn_pool_head": True,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg4_so150m_p14_ap",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 18,
        "num_heads": 16,
        "hidden_dim": 896,  # Changed from 880 for RoPE divisibility
        "mlp_dim": 2320,
        "num_reg_tokens": 4,
        "class_token": False,
        "attn_pool_head": True,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg8_so150m_p14_swiglu_rms_avg",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 18,
        "num_heads": 16,
        "hidden_dim": 896,  # Changed from 880 for RoPE divisibility
        "mlp_dim": 2320,
        "num_reg_tokens": 8,
        "class_token": False,
        "norm_layer_type": "RMSNorm",
        "mlp_layer_type": "SwiGLU_FFN",
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg8_so150m_p14_swiglu_rms_ap",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 18,
        "num_heads": 16,
        "hidden_dim": 896,  # Changed from 880 for RoPE divisibility
        "mlp_dim": 2320,
        "num_reg_tokens": 8,
        "class_token": False,
        "attn_pool_head": True,
        "norm_layer_type": "RMSNorm",
        "mlp_layer_type": "SwiGLU_FFN",
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg8_so150m_p14_swiglu_rms_aps",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 18,
        "num_heads": 16,
        "hidden_dim": 896,  # Changed from 880 for RoPE divisibility
        "mlp_dim": 2320,
        "num_reg_tokens": 8,
        "class_token": False,
        "attn_pool_head": True,
        "attn_pool_special_tokens": True,
        "norm_layer_type": "RMSNorm",
        "mlp_layer_type": "SwiGLU_FFN",
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg8_so150m_p14_ap",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 18,
        "num_heads": 16,
        "hidden_dim": 896,  # Changed from 880 for RoPE divisibility
        "mlp_dim": 2320,
        "num_reg_tokens": 8,
        "class_token": False,
        "attn_pool_head": True,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg4_so400m_p14_ap",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 27,
        "num_heads": 16,
        "hidden_dim": 1152,
        "mlp_dim": 4304,
        "num_reg_tokens": 4,
        "class_token": False,
        "attn_pool_head": True,
        "drop_path_rate": 0.1,
    },
)
registry.register_model_config(
    "rope_vit_reg8_so400m_p14_ap",
    RoPE_ViT,
    config={
        "patch_size": 14,
        "num_layers": 27,
        "num_heads": 16,
        "hidden_dim": 1152,
        "mlp_dim": 4304,
        "num_reg_tokens": 8,
        "class_token": False,
        "attn_pool_head": True,
        "drop_path_rate": 0.1,
    },
)

registry.register_weights(
    "rope_vit_reg4_b14_capi",
    {
        "url": "https://huggingface.co/birder-project/rope_vit_reg4_b14_capi/resolve/main",
        "description": (
            "RoPE ViT b14 image encoder pre-trained using CAPI. "
            "This model has not been fine-tuned for a specific classification task"
        ),
        "resolution": (224, 224),
        "formats": {
            "pt": {
                "file_size": 327.0,
                "sha256": "175378d81734649567bfe82aac9557f9b0bf48dbd562f26e338b1958fa057472",
            }
        },
        "net": {"network": "rope_vit_reg4_b14", "tag": "capi"},
    },
)
registry.register_weights(
    "rope_vit_reg4_b14_capi-places365",
    {
        "url": "https://huggingface.co/birder-project/rope_vit_reg4_b14_capi-places365/resolve/main",
        "description": "RoPE ViT b14 model pre-trained using CAPI, then fine-tuned on the Places365 dataset",
        "resolution": (224, 224),
        "formats": {
            "pt": {
                "file_size": 328.1,
                "sha256": "4d3ef700eb0d454c9406e9b5c11f70106b46ed4a6ca24c1d89a60097ad78ea9a",
            }
        },
        "net": {"network": "rope_vit_reg4_b14", "tag": "capi-places365"},
    },
)
registry.register_weights(
    "rope_vit_reg4_b14_capi-inat21-224px",
    {
        "url": "https://huggingface.co/birder-project/rope_vit_reg4_b14_capi-inat21/resolve/main",
        "description": "RoPE ViT b14 model pre-trained using CAPI, then fine-tuned on the iNaturalist 2021 dataset",
        "resolution": (224, 224),
        "formats": {
            "pt": {
                "file_size": 357.2,
                "sha256": "fb98a4f29a1c6e552a4e22eaf614b0f2d2adedefe2d510fa7e69309208dc0f9f",
            }
        },
        "net": {"network": "rope_vit_reg4_b14", "tag": "capi-inat21-224px"},
    },
)
registry.register_weights(
    "rope_vit_reg4_b14_capi-inat21",
    {
        "url": "https://huggingface.co/birder-project/rope_vit_reg4_b14_capi-inat21/resolve/main",
        "description": "RoPE ViT b14 model pre-trained using CAPI, then fine-tuned on the iNaturalist 2021 dataset",
        "resolution": (336, 336),
        "formats": {
            "pt": {
                "file_size": 358.2,
                "sha256": "25befb5a460cc80a5a7961db61e747916461bf6967f3d39d9294ee474bd31304",
            }
        },
        "net": {"network": "rope_vit_reg4_b14", "tag": "capi-inat21"},
    },
)
registry.register_weights(
    "rope_vit_reg4_b14_capi-imagenet21k",
    {
        "url": "https://huggingface.co/birder-project/rope_vit_reg4_b14_capi-imagenet21k/resolve/main",
        "description": "RoPE ViT b14 model pre-trained using CAPI, then fine-tuned on the ImageNet-21K dataset",
        "resolution": (224, 224),
        "formats": {
            "pt": {
                "file_size": 383.7,
                "sha256": "1325f35f0d8dff3270d6ce645f81865e9b8de7bacf17f94a9f5e2ef0cd66f56d",
            }
        },
        "net": {"network": "rope_vit_reg4_b14", "tag": "capi-imagenet21k"},
    },
)
registry.register_weights(
    "rope_vit_reg8_so150m_p14_swiglu_rms_avg_capi",
    {
        "url": "https://huggingface.co/birder-project/rope_vit_reg8_so150m_p14_swiglu_rms_avg_capi/resolve/main",
        "description": (
            "RoPE SoViT 150m p14 image encoder pre-trained using CAPI. "
            "This model has not been fine-tuned for a specific classification task"
        ),
        "resolution": (224, 224),
        "formats": {
            "pt": {
                "file_size": 652.5,
                "sha256": "84808bdb7a46c70eb13a67a766c2c3c9a4a9a37a90679e03fd75619aa5517e80",
            }
        },
        "net": {"network": "rope_vit_reg8_so150m_p14_swiglu_rms_avg", "tag": "capi"},
    },
)
registry.register_weights(
    "rope_vit_reg8_so150m_p14_swiglu_rms_ap_rotnet-capi",
    {
        "url": "https://huggingface.co/birder-project/rope_vit_reg8_so150m_p14_swiglu_rms_ap_rotnet-capi/resolve/main",
        "description": (
            "RoPE SoViT 150m p14 image encoder pre-trained using CAPI, then trained to estimate image orientation"
        ),
        "resolution": (252, 252),
        "formats": {
            "pt": {
                "file_size": 680.9,
                "sha256": "57465120826faa1e61accfb0e51b529c6ae431cc1f6960e4cdd5278d8dbd1edf",
            }
        },
        "net": {"network": "rope_vit_reg8_so150m_p14_swiglu_rms_ap", "tag": "rotnet-capi"},
    },
)

# Perception Encoder: The best visual embeddings are not at the output of the network, by Meta FAIR
# https://arxiv.org/abs/2504.13181
registry.register_weights(
    "rope_i_vit_s16_pn_aps_c1_pe-core",
    {
        "url": "https://huggingface.co/birder-project/rope_i_vit_s16_pn_aps_c1_pe-core/resolve/main",
        "description": (
            "ViT s16 image encoder pre-trained by Meta FAIR using CLIP. "
            "This model has not been fine-tuned for a specific classification task"
        ),
        "resolution": (384, 384),
        "formats": {
            "pt": {
                "file_size": 90.0,
                "sha256": "e4429b0bafb9f827698dde73c882c70deb994329ea0dd169f68e76ad256bbb74",
            },
        },
        "net": {"network": "rope_i_vit_s16_pn_aps_c1", "tag": "pe-core"},
    },
)
registry.register_weights(
    "rope_i_vit_reg1_s16_pn_npn_avg_c1_pe-spatial",
    {
        "url": "https://huggingface.co/birder-project/rope_i_vit_reg1_s16_pn_npn_avg_c1_pe-spatial/resolve/main",
        "description": (
            "ViT s16 image encoder pre-trained by Meta FAIR using CLIP. "
            "This model has not been fine-tuned for a specific classification task"
        ),
        "resolution": (512, 512),
        "formats": {
            "pt": {
                "file_size": 83.9,
                "sha256": "4e65e500f2a7d2b11fc28aaa0b1ad4921692780507de014ebc5659e757327fde",
            },
        },
        "net": {"network": "rope_i_vit_reg1_s16_pn_npn_avg_c1", "tag": "pe-spatial"},
    },
)
registry.register_weights(
    "rope_i_vit_b16_pn_aps_c1_pe-core",
    {
        "url": "https://huggingface.co/birder-project/rope_i_vit_b16_pn_aps_c1_pe-core/resolve/main",
        "description": (
            "ViT b16 image encoder pre-trained by Meta FAIR using CLIP. "
            "This model has not been fine-tuned for a specific classification task"
        ),
        "resolution": (224, 224),
        "formats": {
            "pt": {
                "file_size": 354.4,
                "sha256": "d1c1ba1e8c841f495ff3c0e5e6963a39c8d1ae07dea30d3b82422017a4062d97",
            },
        },
        "net": {"network": "rope_i_vit_b16_pn_aps_c1", "tag": "pe-core"},
    },
)
registry.register_weights(
    "rope_i_vit_l14_pn_aps_c1_pe-core",
    {
        "url": "https://huggingface.co/birder-project/rope_i_vit_l14_pn_aps_c1_pe-core/resolve/main",
        "description": (
            "ViT l14 image encoder pre-trained by Meta FAIR using CLIP. "
            "This model has not been fine-tuned for a specific classification task"
        ),
        "resolution": (336, 336),
        "formats": {
            "pt": {
                "file_size": 1206.0,
                "sha256": "26c2188116cb254d2870c23cc3ab7d60d9ee0606c803b8dbe359e5716498b5c4",
            },
        },
        "net": {"network": "rope_i_vit_l14_pn_aps_c1", "tag": "pe-core"},
    },
)
