"""
Paper "FlexiViT: One Model for All Patch Sizes", https://arxiv.org/abs/2212.08013
"""

# Reference license: Apache-2.0

import logging
import math
import random
from functools import partial
from typing import Any
from typing import Literal
from typing import Optional

import torch
from torch import nn

from birder.common.masking import mask_tensor
from birder.layers import FFN
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
from birder.net.flexivit import flex_proj
from birder.net.flexivit import get_patch_sizes
from birder.net.flexivit import interpolate_proj
from birder.net.rope_vit import Encoder
from birder.net.rope_vit import MAEDecoderBlock
from birder.net.rope_vit import RoPE
from birder.net.rope_vit import build_rotary_pos_embed
from birder.net.vit import PatchEmbed
from birder.net.vit import adjust_position_embedding

logger = logging.getLogger(__name__)


# pylint: disable=invalid-name,too-many-instance-attributes
class RoPE_FlexiViT(DetectorBackbone, PreTrainEncoder, MaskedTokenOmissionMixin, MaskedTokenRetentionMixin):
    default_size = (240, 240)
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
        pos_embed_special_tokens: bool = self.config.get("pos_embed_special_tokens", False)
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
        min_patch_size: int = self.config.get("min_patch_size", 8)
        max_patch_size: int = self.config.get("max_patch_size", 48)
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
        self.patch_size_list = get_patch_sizes(min_patch_size, max_patch_size, self.size)

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
            bias=True,
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

        self.set_dynamic_size()

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

    def _get_pos_embed(self, H: int, W: int, patch_size: Optional[int] = None) -> torch.Tensor:
        if patch_size is None:
            patch_size = self.patch_size

        if H == self.size[0] and W == self.size[1] and patch_size == self.patch_size:
            return self.pos_embedding

        return adjust_position_embedding(
            self.pos_embedding,
            (self.size[0] // self.patch_size, self.size[1] // self.patch_size),
            (H // patch_size, W // patch_size),
            self.num_special_tokens if self.pos_embed_special_tokens is True else 0,
            antialias=False,
        )

    def _get_rope_embed(self, H: int, W: int, patch_size: Optional[int] = None) -> torch.Tensor:
        if patch_size is None:
            patch_size = self.patch_size

        if H == self.size[0] and W == self.size[1] and patch_size == self.patch_size:
            return self.rope.pos_embed

        return torch.concat(
            build_rotary_pos_embed(
                self.hidden_dim // self.num_heads,
                self.rope_temperature,
                grid_size=(H // patch_size, W // patch_size),
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

    # pylint: disable=too-many-branches
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

    def forward_features(self, x: torch.Tensor, patch_size: Optional[int] = None) -> torch.Tensor:
        (H, W) = x.shape[-2:]

        # Reshape and permute the input tensor
        x = flex_proj(x, self.conv_proj.weight, self.conv_proj.bias, patch_size)
        x = self.patch_embed(x)

        if self.pos_embed_special_tokens is False:
            x = x + self._get_pos_embed(H, W, patch_size=patch_size)

        # Expand the class token to the full batch
        if self.class_token is not None:
            batch_class_token = self.class_token.expand(x.shape[0], -1, -1)
            x = torch.concat([batch_class_token, x], dim=1)

        # Expand the register tokens to the full batch
        if self.reg_tokens is not None:
            batch_reg_tokens = self.reg_tokens.expand(x.shape[0], -1, -1)
            x = torch.concat([batch_reg_tokens, x], dim=1)

        if self.pos_embed_special_tokens is True:
            x = x + self._get_pos_embed(H, W, patch_size=patch_size)

        x = self.encoder(x, self._get_rope_embed(H, W, patch_size=patch_size))
        x = self.norm(x)

        return x

    def embedding(self, x: torch.Tensor, patch_size: Optional[int] = None) -> torch.Tensor:
        x = self.forward_features(x, patch_size)

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

    def forward(self, x: torch.Tensor, patch_size: Optional[int] = None) -> torch.Tensor:
        if self.training is True and patch_size is None and not torch.jit.is_tracing() and not torch.jit.is_scripting():
            patch_size = random.choice(self.patch_size_list)

        x = self.embedding(x, patch_size)
        return self.classify(x)

    def set_dynamic_size(self, dynamic_size: bool = True) -> None:
        super().set_dynamic_size(dynamic_size)
        assert self.dynamic_size is True, "FlexiViT only support dynamic mode"

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
            # On rounding error see: https://github.com/facebookresearch/dino/issues/8
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

    def adjust_patch_size(self, patch_size: int) -> None:
        if self.patch_size == patch_size:
            return

        logger.debug(f"Setting patch size to: {patch_size}")
        self.conv_proj.weight = nn.Parameter(interpolate_proj(self.conv_proj.weight, patch_size))

        # Adjust pos_embedding accordingly
        if self.pos_embed_special_tokens is True:
            num_prefix_tokens = self.num_special_tokens
        else:
            num_prefix_tokens = 0

        self.pos_embedding = nn.Parameter(
            adjust_position_embedding(
                self.pos_embedding,
                (self.size[0] // self.patch_size, self.size[1] // self.patch_size),
                (self.size[0] // patch_size, self.size[1] // patch_size),
                num_prefix_tokens,
            )
        )

        # Adjust RoPE
        self.rope = RoPE(
            self.hidden_dim // self.num_heads,
            temperature=self.rope_temperature,
            grid_size=(self.size[0] // patch_size, self.size[1] // patch_size),
            grid_indexing=self.rope_grid_indexing,
            grid_offset=self.rope_grid_offset,
            pt_grid_size=self.pt_grid_size,
            rope_rot_type=self.rope_rot_type,
        )

        self.patch_size = patch_size

    def load_rope_vit_weights(self, state_dict: dict[str, Any]) -> None:
        num_special_tokens = 0
        if "class_token" in state_dict:
            num_special_tokens += 1

        if "reg_tokens" in state_dict:
            num_special_tokens += state_dict["reg_tokens"].size(1)

        seq_length = (self.size[0] // self.patch_size) * (self.size[1] // self.patch_size)
        vit_pos_embed_special_tokens = state_dict["pos_embedding"].size(1) != seq_length

        # Adjust pos_embedding
        if self.pos_embed_special_tokens is False and vit_pos_embed_special_tokens is True:
            if state_dict["pos_embedding"].ndim == 2:
                state_dict["pos_embedding"] = state_dict["pos_embedding"][num_special_tokens:, :]
            else:
                state_dict["pos_embedding"] = state_dict["pos_embedding"][:, num_special_tokens:, :]

        self.load_state_dict(state_dict, strict=True)


# For the model naming convention see rope_vit.py

registry.register_model_config(
    "rope_flexivit_s16",
    RoPE_FlexiViT,
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
    "rope_flexivit_reg4_b16_avg",
    RoPE_FlexiViT,
    config={
        "patch_size": 16,
        "num_layers": 12,
        "num_heads": 12,
        "hidden_dim": 768,
        "mlp_dim": 3072,
        "num_reg_tokens": 4,
        "class_token": False,
        "drop_path_rate": 0.1,
    },
)
