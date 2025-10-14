import os
import random
from typing import Any
from typing import Optional

import numpy as np
import torch

from birder.conf import settings
from birder.data.transforms.classification import RGBType
from birder.model_registry import registry
from birder.net.base import BaseNet
from birder.net.base import SignatureType
from birder.net.base import reparameterize_available
from birder.net.detection.base import DetectionBaseNet
from birder.net.detection.base import DetectionSignatureType
from birder.net.mim.base import MIMBaseNet
from birder.net.ssl.base import SSLBaseNet
from birder.version import __version__


def set_random_seeds(seed: int) -> None:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)


def get_size_from_signature(signature: SignatureType | DetectionSignatureType) -> tuple[int, int]:
    return tuple(signature["inputs"][0]["data_shape"][2:4])  # type: ignore[return-value]


def get_channels_from_signature(signature: SignatureType | DetectionSignatureType) -> int:
    return signature["inputs"][0]["data_shape"][1]


def get_num_labels_from_signature(signature: SignatureType | DetectionSignatureType) -> int:
    if "num_labels" in signature:
        return signature["num_labels"]  # type: ignore[typeddict-item]

    return signature["outputs"][0]["data_shape"][1]


def get_label_from_path(path: str, hierarchical: bool = False, root: str = "", separator: str = "_") -> str:
    """
    Returns the last directory from the path.

    Standard mode (hierarchical=False):
        data/validation/Alpine swift/000001.jpeg -> 'Alpine swift'
        data/train/cats/img1.jpg -> 'cats'

    Hierarchical mode (hierarchical=True):
        data/validation/Aves/Alpine swift/000001.jpeg -> 'Aves_Alpine swift'
        data/train/animals/cats/img1.jpg -> 'animals_cats'
    """

    if hierarchical is False:
        return os.path.basename(os.path.dirname(path))

    directory = os.path.dirname(path)
    rel_path = os.path.relpath(directory, root)
    return rel_path.replace(os.sep, separator)


def get_network_name(network: str, tag: Optional[str] = None) -> str:
    network_name = network
    if tag is not None:
        network_name = f"{network_name}_{tag}"

    return network_name


def get_mim_network_name(network: str, encoder: str, tag: Optional[str] = None) -> str:
    prefix = get_network_name(network)
    suffix = get_network_name(encoder, tag)
    return f"{prefix}_{suffix}"


def get_detection_network_name(network: str, tag: Optional[str], backbone: str, backbone_tag: Optional[str]) -> str:
    prefix = get_network_name(network, tag)
    suffix = get_network_name(backbone, backbone_tag)
    return f"{prefix}_{suffix}"


def detection_class_to_idx(class_to_idx: dict[str, int]) -> dict[str, int]:
    # Give place to "background" class (always index 0)
    for key in class_to_idx:
        class_to_idx[key] += 1

    return class_to_idx


def class_to_idx_from_coco(cats: dict[int, Any]) -> dict[str, int]:
    class_list = [item["name"] for item in sorted(cats.values(), key=lambda x: x["id"])]
    class_to_idx = {k: v for v, k in enumerate(class_list)}
    return class_to_idx


def get_network_config(
    net: BaseNet | DetectionBaseNet | MIMBaseNet | SSLBaseNet,
    signature: SignatureType | DetectionSignatureType,
    rgb_stats: RGBType,
) -> dict[str, Any]:
    model_name = registry.get_model_base_name(net)
    alias = registry.get_model_alias(net)
    model_config = None
    if net.config is not None:
        model_config = net.config

    backbone_config: dict[str, Any] = {}
    if isinstance(net, DetectionBaseNet):
        backbone_config["backbone"] = registry.get_model_base_name(net.backbone)
        backbone_config["backbone_alias"] = registry.get_model_alias(net.backbone)
        if net.backbone.config is not None:
            backbone_config["backbone_config"] = net.backbone.config
        if reparameterize_available(net.backbone) is True:
            backbone_config["backbone_reparameterized"] = net.backbone.reparameterized

    encoder_config: dict[str, Any] = {}
    if isinstance(net, MIMBaseNet):
        encoder_config["encoder"] = registry.get_model_base_name(net.encoder)
        encoder_config["encoder_alias"] = registry.get_model_alias(net.encoder)
        if net.encoder.config is not None:
            encoder_config["encoder_config"] = net.encoder.config
        if reparameterize_available(net.encoder) is True:
            encoder_config["encoder_reparameterized"] = net.encoder.reparameterized

    base_net_config: dict[str, Any] = {}
    if isinstance(net, SSLBaseNet):
        base_net_config["base_net"] = registry.get_model_base_name(net.backbone)
        base_net_config["base_net_alias"] = registry.get_model_alias(net.backbone)
        if net.backbone.config is not None:
            base_net_config["base_net_config"] = net.backbone.config
        if reparameterize_available(net.backbone) is True:
            base_net_config["base_net_reparameterized"] = net.backbone.reparameterized

    net_config = {
        "birder_version": __version__,
        "name": model_name,
        "alias": alias,
        "task": net.task,
        "model_config": model_config,
        **backbone_config,
        **encoder_config,
        **base_net_config,
        "signature": signature,
        "rgb_stats": rgb_stats,
    }

    if reparameterize_available(net) is True:
        net_config["reparameterized"] = net.reparameterized

    return net_config


def get_pretrained_model_url(weights: str, file_format: str) -> tuple[str, str]:
    model_metadata = registry.get_pretrained_metadata(weights)
    model_file = f"{weights}.{file_format}"
    base_url = model_metadata.get("url", settings.REGISTRY_BASE_UTL)
    url = f"{base_url}/{model_file}"

    return (model_file, url)


def format_duration(seconds: float) -> str:
    s = int(seconds)
    (mm, ss) = divmod(s, 60)
    (hh, mm) = divmod(mm, 60)
    return f"{hh:d}:{mm:02d}:{ss:02d}"
