"""
DINO v2 distillation

Paper "DINOv2: Learning Robust Visual Features without Supervision", https://arxiv.org/abs/2304.07193
"""

import argparse
import json
import logging
import math
import random
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import torch
import torchinfo
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from torchvision.datasets.folder import pil_loader  # Slower but Handles external dataset quirks better
from torchvision.transforms import v2
from tqdm import tqdm

import birder
from birder.common import cli
from birder.common import fs_ops
from birder.common import training_cli
from birder.common import training_utils
from birder.common.lib import format_duration
from birder.common.lib import get_mim_network_name
from birder.common.lib import get_network_name
from birder.common.lib import set_random_seeds
from birder.common.masking import BlockMasking
from birder.conf import settings
from birder.data.dataloader.webdataset import make_wds_loader
from birder.data.datasets.directory import make_image_dataset
from birder.data.datasets.directory import tv_loader
from birder.data.datasets.fake import FakeDataWithPaths
from birder.data.datasets.webdataset import make_wds_dataset
from birder.data.datasets.webdataset import prepare_wds_args
from birder.data.datasets.webdataset import wds_args_from_info
from birder.data.transforms.classification import RGBType
from birder.data.transforms.classification import get_rgb_stats
from birder.model_registry import Task
from birder.model_registry import registry
from birder.net.base import MaskedTokenRetentionMixin
from birder.net.base import get_signature
from birder.net.ssl.base import get_ssl_signature
from birder.net.ssl.dino_v2 import DINOLoss
from birder.net.ssl.dino_v2 import DINOv2Student
from birder.net.ssl.dino_v2 import DINOv2Teacher
from birder.net.ssl.dino_v2 import KoLeoLoss
from birder.net.ssl.dino_v2 import iBOTPatchLoss

logger = logging.getLogger(__name__)


class DINOv2BlockMasking(BlockMasking):
    def __call__(self, num_masking_patches: int) -> torch.Tensor:
        mask = torch.zeros(*self.get_shape())
        mask_count = 0
        while mask_count < num_masking_patches:
            max_mask_patches = num_masking_patches - mask_count
            max_mask_patches = min(max_mask_patches, self.max_num_patches)

            delta = self._mask(mask, max_mask_patches)
            if delta == 0:
                break

            mask_count += delta

        return mask


class TrainTransform:
    def __init__(
        self,
        global_transform: Callable[..., torch.Tensor],
        crop_size: tuple[int, int],
        rgv_values: RGBType,
        local_crops_number: int,
    ) -> None:
        self.global_transform = global_transform
        self.local_crops_number = local_crops_number

        # Local small crops
        mean = rgv_values["mean"]
        std = rgv_values["std"]
        self.local_transform = v2.Compose(
            [
                v2.PILToTensor(),
                v2.RandomResizedCrop(crop_size, scale=(0.1, 0.35), interpolation=v2.InterpolationMode.BICUBIC),
                v2.RandomHorizontalFlip(p=0.5),
                v2.RandomApply([v2.ColorJitter(brightness=0.25, contrast=0.15, hue=0.04)], p=0.8),
                v2.RandomApply([v2.GaussianBlur(kernel_size=(3, 3), sigma=(0.5, 1.2))], p=0.5),
                v2.ToDtype(torch.float32, scale=True),
                v2.Normalize(mean=mean, std=std),
            ]
        )

    def __call__(self, image: Any) -> dict[str, list[torch.Tensor]]:
        output = {}
        output["global_crops"] = [self.global_transform(image), self.global_transform(image)]

        local_crops = []
        for _ in range(self.local_crops_number):
            local_crops.append(self.local_transform(image))

        output["local_crops"] = local_crops

        return output


class TrainCollator:
    def __init__(
        self,
        mask_generator: Callable[[int], tuple[list[torch.Tensor], list[torch.Tensor]]],
        seq_len: int,
        mask_probability: float,
        mask_ratio_tuple: tuple[float, float],
    ) -> None:
        self.mask_generator = mask_generator
        self.seq_len = seq_len
        self.mask_probability = mask_probability
        self.mask_ratio_tuple = mask_ratio_tuple

    def __call__(self, batch: Any) -> dict[str, Any]:
        n_global_crops = len(batch[0][1]["global_crops"])
        n_local_crops = len(batch[0][1]["local_crops"])

        collated_global_crops = torch.stack([s[1]["global_crops"][i] for i in range(n_global_crops) for s in batch])
        collated_local_crops = torch.stack([s[1]["local_crops"][i] for i in range(n_local_crops) for s in batch])

        B = len(collated_global_crops)
        N = self.seq_len
        n_samples_masked = int(B * self.mask_probability)
        probs = torch.linspace(*self.mask_ratio_tuple, n_samples_masked + 1)
        upper_bound = 0
        masks_list = []
        for i in range(0, n_samples_masked):
            prob_min = probs[i]
            prob_max = probs[i + 1]
            masks_list.append(self.mask_generator(int(N * random.uniform(prob_min, prob_max))))
            upper_bound += int(N * prob_max)

        for i in range(n_samples_masked, B):
            masks_list.append(self.mask_generator(0))

        random.shuffle(masks_list)

        collated_masks = torch.stack(masks_list).flatten(1)
        mask_indices_list = collated_masks.flatten().nonzero().flatten()

        masks_weight = (
            (1 / collated_masks.sum(-1).clamp(min=1.0)).unsqueeze(-1).expand_as(collated_masks)[collated_masks.bool()]
        )

        # Keep everything intact for loss calculation (with the randomness of the fake masking)
        # Just the remove actual masking
        collated_masks = torch.zeros_like(collated_masks)

        return {
            "collated_global_crops": collated_global_crops,
            "collated_local_crops": collated_local_crops,
            "collated_masks": collated_masks,
            "mask_indices_list": mask_indices_list,
            "masks_weight": masks_weight,
            "upper_bound": upper_bound,
            "n_masked_patches": torch.full((1,), fill_value=mask_indices_list.size(0), dtype=torch.long),
        }


# pylint: disable=too-many-locals,too-many-branches,too-many-statements
def train(args: argparse.Namespace) -> None:
    #
    # Initialize
    #
    training_utils.init_distributed_mode(args)
    logger.info(f"Starting training, birder version: {birder.__version__}, pytorch version: {torch.__version__}")
    training_utils.log_git_info()

    if args.size is None:
        args.size = registry.get_default_size(args.network)

    logger.info(f"Using size={args.size}")

    if args.cpu is True:
        device = torch.device("cpu")
        device_id = 0
    else:
        device = torch.device("cuda")
        device_id = torch.cuda.current_device()

    if args.use_deterministic_algorithms is True:
        torch.backends.cudnn.benchmark = False
        torch.use_deterministic_algorithms(True)
    else:
        torch.backends.cudnn.benchmark = True

    if args.seed is not None:
        set_random_seeds(args.seed)

    if args.non_interactive is True or training_utils.is_local_primary(args) is False:
        disable_tqdm = True
    elif sys.stderr.isatty() is False:
        disable_tqdm = True
    else:
        disable_tqdm = False

    # Enable or disable the autograd anomaly detection
    torch.autograd.set_detect_anomaly(args.grad_anomaly_detection)

    batch_size: int = args.batch_size
    logger.debug(f"Effective batch size = {args.batch_size * args.grad_accum_steps * args.world_size}")

    begin_epoch = 1
    epochs = args.epochs + 1
    if args.stop_epoch is None:
        args.stop_epoch = epochs
    else:
        args.stop_epoch += 1

    #
    # Initialize network
    #
    model_dtype: torch.dtype = getattr(torch, args.model_dtype)
    sample_shape = (batch_size, args.channels, *args.size)  # B, C, H, W
    backbone_name = get_network_name(args.network, tag="dino-v2-dist")
    if args.tag is not None:
        backbone_name = f"{backbone_name}-{args.tag}"

    network_name = get_mim_network_name("dino_v2_dist", encoder=args.network, tag=args.tag)

    student_backbone = registry.net_factory(args.network, sample_shape[1], 0, config=args.model_config, size=args.size)
    student_backbone_ema = registry.net_factory(
        args.network, sample_shape[1], 0, config=args.model_config, size=args.size
    )
    student_backbone_ema.load_state_dict(student_backbone.state_dict())

    teacher_backbone = registry.net_factory(
        args.teacher,
        sample_shape[1],
        0,
        config=args.teacher_model_config,
        size=args.size,
    )
    student_backbone.set_dynamic_size()
    if args.ibot_separate_head is False:
        args.ibot_out_dim = args.dino_out_dim

    student = DINOv2Student(
        student_backbone,
        config={
            "dino_out_dim": args.dino_out_dim,
            "use_bn": False,
            "num_layers": 3,
            "hidden_dim": 2048,
            "head_bottleneck_dim": args.head_bottleneck_dim,
            "ibot_separate_head": args.ibot_separate_head,
            "ibot_out_dim": args.ibot_out_dim,
        },
    )
    teacher = DINOv2Teacher(
        teacher_backbone,
        config={
            "dino_out_dim": args.dino_out_dim,
            "use_bn": False,
            "num_layers": 3,
            "hidden_dim": 2048,
            "head_bottleneck_dim": args.head_bottleneck_dim,
            "ibot_separate_head": args.ibot_separate_head,
            "ibot_out_dim": args.ibot_out_dim,
        },
    )
    teacher.eval()

    dino_loss = DINOLoss(args.dino_out_dim, student_temp=0.1, center_momentum=0.9)
    koleo_loss = KoLeoLoss()
    ibot_patch_loss = iBOTPatchLoss(args.ibot_out_dim, student_temp=0.1, center_momentum=0.9)

    net = torch.nn.ModuleDict(
        {
            "student": student,
            "student_backbone_ema": student_backbone_ema,
            "teacher": teacher,
            "dino_loss": dino_loss,
            "koleo_loss": koleo_loss,
            "ibot_patch_loss": ibot_patch_loss,
        }
    )
    net.task = teacher.task

    if args.resume_epoch is not None:
        begin_epoch = args.resume_epoch + 1
        (net, training_states) = fs_ops.load_simple_checkpoint(
            device, net, network_name, epoch=args.resume_epoch, strict=not args.non_strict_weights
        )
        student = net["student"]
        student_backbone_ema = net["student_backbone_ema"]
        teacher = net["teacher"]
        dino_loss = net["dino_loss"]
        koleo_loss = net["koleo_loss"]
        ibot_patch_loss = net["ibot_patch_loss"]

    else:
        state = fs_ops.load_state_dict(
            device,
            get_mim_network_name("dino_v2", encoder=args.teacher, tag=args.teacher_tag),
            epoch=args.teacher_epoch,
        )
        filtered_state = {}
        for name, p in state.items():
            if name.startswith("teacher.") is True:
                filtered_state[name.removeprefix("teacher.")] = p

        teacher.load_state_dict(filtered_state)
        training_states = fs_ops.TrainingStates.empty()

    assert isinstance(student_backbone, MaskedTokenRetentionMixin)
    assert isinstance(net, torch.nn.Module)

    net.to(device, dtype=model_dtype)
    if args.freeze_bn is True:
        student = training_utils.freeze_batchnorm2d(student)
        teacher = training_utils.freeze_batchnorm2d(teacher)
    elif args.sync_bn is True and args.distributed is True:
        student = torch.nn.SyncBatchNorm.convert_sync_batchnorm(student)
        teacher = torch.nn.SyncBatchNorm.convert_sync_batchnorm(teacher)

    if args.fast_matmul is True or args.amp is True:
        torch.set_float32_matmul_precision("high")

    # Compile networks
    teacher_compile_flag = args.compile is True or args.compile_teacher is True
    if args.compile is True:
        student = torch.compile(student)
        teacher = torch.compile(teacher)
    elif args.compile_teacher is True:
        teacher = torch.compile(teacher)

    #
    # Data
    #
    rgb_stats = get_rgb_stats(args.rgb_mode, args.rgb_mean, args.rgb_std)
    logger.debug(f"Using RGB stats: {rgb_stats}")

    mask_size = (args.size[0] // student_backbone.max_stride, args.size[1] // student_backbone.max_stride)
    seq_len = mask_size[0] * mask_size[1]

    mask_generator = DINOv2BlockMasking(
        mask_size, min_num_patches=4, max_num_patches=mask_size[0] * mask_size[1] // 2, min_aspect=0.33, max_aspect=3.33
    )
    training_transform = TrainTransform(
        training_utils.get_training_transform(args), args.local_crop_size, rgb_stats, args.local_crops_number
    )
    collator = TrainCollator(
        mask_generator, seq_len=seq_len, mask_probability=args.ibot_mask_probability, mask_ratio_tuple=(0.1, 0.5)
    )

    n_local_crops = args.local_crops_number
    n_global_crops = 2
    ibot_loss_scale = 1.0 / n_global_crops

    if args.use_fake_data is True:
        logger.warning("Using fake data")
        training_dataset = FakeDataWithPaths(
            10000, (args.channels, *args.size), num_classes=10, transform=training_transform
        )

    elif args.wds is True:
        wds_path: str | list[str]
        if args.wds_info is not None:
            (wds_path, dataset_size) = wds_args_from_info(args.wds_info, args.wds_split)
            if args.wds_train_size is not None:
                dataset_size = args.wds_train_size
        else:
            (wds_path, dataset_size) = prepare_wds_args(args.data_path[0], args.wds_train_size, device)

        training_dataset = make_wds_dataset(
            wds_path,
            dataset_size=dataset_size,
            shuffle=True,
            samples_names=True,
            transform=training_transform,
            img_loader=args.img_loader,
            cls_key=None,
            cache_dir=args.wds_cache_dir,
        )

    else:
        training_dataset = make_image_dataset(
            args.data_path,
            {},
            transforms=training_transform,
            loader=pil_loader if args.img_loader == "pil" else tv_loader,
        )

    logger.info(f"Using device {device}:{device_id}")
    logger.info(f"Training on {len(training_dataset):,} samples")

    # Data loaders and samplers
    if args.distributed is True:
        train_sampler = torch.utils.data.distributed.DistributedSampler(training_dataset, shuffle=True)
    else:
        train_sampler = torch.utils.data.RandomSampler(training_dataset)

    if args.wds is True:
        training_loader = make_wds_loader(
            training_dataset,
            batch_size,
            num_workers=args.num_workers,
            prefetch_factor=args.prefetch_factor,
            collate_fn=collator,
            world_size=args.world_size,
            pin_memory=True,
            drop_last=args.drop_last,
            shuffle=args.wds_extra_shuffle,
        )

    else:
        training_loader = DataLoader(
            training_dataset,
            batch_size=batch_size,
            sampler=train_sampler,
            num_workers=args.num_workers,
            prefetch_factor=args.prefetch_factor,
            collate_fn=collator,
            pin_memory=True,
            drop_last=args.drop_last,
        )

    last_batch_idx = len(training_loader) - 1

    #
    # Optimizer, learning rate scheduler and training parameter groups
    #

    # Training parameter groups
    custom_keys_weight_decay = training_utils.get_wd_custom_keys(args)
    parameters = training_utils.optimizer_parameter_groups(
        net,
        args.wd,
        norm_weight_decay=args.norm_wd,
        custom_keys_weight_decay=custom_keys_weight_decay,
        layer_decay=args.layer_decay,
        layer_decay_min_scale=args.layer_decay_min_scale,
        layer_decay_no_opt_scale=args.layer_decay_no_opt_scale,
        bias_lr=args.bias_lr,
    )

    # Learning rate scaling
    lr = training_utils.scale_lr(args)
    grad_accum_steps: int = args.grad_accum_steps

    if args.lr_scheduler_update == "epoch":
        iter_update = False
        iters_per_epoch = 1
    elif args.lr_scheduler_update == "iter":
        iter_update = True
        iters_per_epoch = math.ceil(len(training_loader) / grad_accum_steps)
    else:
        raise ValueError("Unsupported lr_scheduler_update")

    # Optimizer and learning rate scheduler
    optimizer = training_utils.get_optimizer(parameters, lr, args)
    scheduler = training_utils.get_scheduler(optimizer, iters_per_epoch, args)
    if args.compile_opt is True:
        optimizer.step = torch.compile(optimizer.step, fullgraph=False)

    # Temperature and weight decay schedule
    teacher_temp_schedule = training_utils.cosine_scheduler(
        args.teacher_temp,
        args.teacher_temp,
        args.epochs,
        args.warmup_teacher_temp_epochs,
        last_batch_idx + 1,
        args.warmup_teacher_temp,
    )
    if args.wd_end is not None:
        wd_schedule = training_utils.cosine_scheduler(args.wd, args.wd_end, args.epochs, 0, 1)
    else:
        wd_schedule = None

    # Gradient scaler and AMP related tasks
    (scaler, amp_dtype) = training_utils.get_amp_scaler(args.amp, args.amp_dtype)

    # Load states
    if args.load_states is True:
        optimizer.load_state_dict(training_states.optimizer_state)
        scheduler.load_state_dict(training_states.scheduler_state)
        if scaler is not None:
            scaler.load_state_dict(training_states.scaler_state)

    elif args.load_scheduler is True:
        scheduler.load_state_dict(training_states.scheduler_state)
        last_lrs = scheduler.get_last_lr()
        for g, last_lr in zip(optimizer.param_groups, last_lrs):
            g["lr"] = last_lr

    last_lr = max(scheduler.get_last_lr())
    if args.plot_lr is True:
        logger.info("Fast forwarding scheduler...")
        optimizer.step()
        lrs = []
        for _ in range(begin_epoch, epochs):
            for _ in range(iters_per_epoch):
                lrs.append(max(scheduler.get_last_lr()))
                scheduler.step()

        plt.plot(np.linspace(begin_epoch, epochs, iters_per_epoch * (epochs - begin_epoch), endpoint=False), lrs)
        plt.show()
        raise SystemExit(0)

    #
    # Distributed (DDP)
    #

    # There is no backpropagation through the teacher
    for p in teacher.parameters():
        p.requires_grad = False

    if args.distributed is True:
        student = torch.nn.parallel.DistributedDataParallel(
            student, device_ids=[args.local_rank], find_unused_parameters=args.find_unused_parameters
        )

    model_to_save = net
    if teacher_compile_flag is True and hasattr(model_to_save["teacher"], "_orig_mod") is True:
        model_to_save["teacher"] = model_to_save["teacher"]._orig_mod  # pylint: disable=protected-access
    if args.compile is True and hasattr(model_to_save["student"], "_orig_mod") is True:
        model_to_save["student"] = model_to_save["student"]._orig_mod  # pylint: disable=protected-access

    #
    # Misc
    #

    # Print network summary
    net_for_info = teacher
    if teacher_compile_flag is True and hasattr(teacher, "_orig_mod") is True:
        net_for_info = teacher._orig_mod  # pylint: disable=protected-access

    if args.no_summary is False:
        mask_indices_list = torch.tensor([0, 1])
        upper_bound = 3
        summary = torchinfo.summary(
            net_for_info,
            device=device,
            input_data={
                "x": torch.rand(sample_shape),
                "n_crops": sample_shape[0] // 2,
                "upper_bound": upper_bound,
                "mask_indices_list": mask_indices_list,
            },
            dtypes=[model_dtype],
            col_names=["input_size", "output_size", "kernel_size", "num_params"],
            depth=4,
            verbose=0,
        )
        if training_utils.is_global_primary(args) is True:
            # Write to stderr, same as all the logs
            print(summary, file=sys.stderr)

    # Training logs
    training_log_path = training_utils.training_log_path(network_name, device, args.experiment)
    logger.info(f"Logging training run at {training_log_path}")
    summary_writer = SummaryWriter(training_log_path)

    signature = get_ssl_signature(input_shape=sample_shape)
    backbone_signature = get_signature(input_shape=sample_shape, num_outputs=0)
    file_handler: logging.Handler = logging.NullHandler()
    if training_utils.is_local_primary(args) is True:
        summary_writer.flush()
        fs_ops.write_config(network_name, net_for_info, signature=signature, rgb_stats=rgb_stats)
        file_handler = training_utils.setup_file_logging(training_log_path.joinpath("training.log"))
        with open(training_log_path.joinpath("training_args.json"), "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "birder_version": birder.__version__,
                    "pytorch_version": torch.__version__,
                    "cmdline": " ".join(sys.argv),
                    **vars(args),
                },
                handle,
                indent=2,
            )

        with open(training_log_path.joinpath("training_data.json"), "w", encoding="utf-8") as handle:
            json.dump(
                {"training_samples": len(training_dataset)},
                handle,
                indent=2,
            )

    #
    # Training loop
    #
    logger.info(f"Starting training with learning rate of {last_lr}")
    for epoch in range(begin_epoch, args.stop_epoch):
        tic = time.time()
        net.train()
        running_loss = training_utils.SmoothedValue()
        running_loss_dino_local = training_utils.SmoothedValue()
        running_loss_dino_global = training_utils.SmoothedValue()
        running_loss_koleo = training_utils.SmoothedValue()
        running_loss_ibot_patch = training_utils.SmoothedValue()

        if args.distributed is True:
            train_sampler.set_epoch(epoch)

        if wd_schedule is not None:
            wd = wd_schedule[epoch - 1]
            for param_group in optimizer.param_groups:
                if param_group["weight_decay"] > 0:
                    param_group["weight_decay"] = wd

            logger.info(f"Updated wd to: {wd}")

        progress = tqdm(
            desc=f"Epoch {epoch}/{epochs-1}",
            total=len(training_dataset),
            leave=False,
            disable=disable_tqdm,
            unit="samples",
            initial=0,
        )

        # Zero the parameter gradients
        optimizer.zero_grad()

        epoch_start = time.time()
        start_time = epoch_start
        last_idx = 0
        for i, data in enumerate(training_loader):
            global_step = ((epoch - 1) * (last_batch_idx + 1)) + i
            optimizer_update = (i == last_batch_idx) or ((i + 1) % grad_accum_steps == 0)
            teacher_temp = teacher_temp_schedule[global_step]

            global_crops = data["collated_global_crops"].to(device, dtype=model_dtype, non_blocking=True)
            local_crops = data["collated_local_crops"].to(device, dtype=model_dtype, non_blocking=True)

            masks = data["collated_masks"].to(device, non_blocking=True)
            mask_indices_list = data["mask_indices_list"].to(device, non_blocking=True)
            n_masked_patches_tensor = data["n_masked_patches"].to(device, non_blocking=True)
            n_masked_patches = mask_indices_list.size(0)
            upper_bound = data["upper_bound"]
            masks_weight = data["masks_weight"].to(device, non_blocking=True)

            n_local_crops_loss_terms = max(n_local_crops * n_global_crops, 1)
            n_global_crops_loss_terms = (n_global_crops - 1) * n_global_crops

            # Forward, backward and optimize
            with torch.amp.autocast("cuda", enabled=args.amp, dtype=amp_dtype):
                # Teacher
                (teacher_embedding_after_head, teacher_masked_patch_tokens_after_head) = teacher(
                    global_crops, n_global_crops, upper_bound, mask_indices_list
                )
                if args.centering == "centering":
                    teacher_dino_softmax_centered_list = dino_loss.softmax_center_teacher(
                        teacher_embedding_after_head, teacher_temp=teacher_temp
                    ).view(n_global_crops, -1, *teacher_embedding_after_head.shape[1:])
                    dino_loss.update_center(teacher_embedding_after_head)

                    teacher_masked_patch_tokens_after_head = teacher_masked_patch_tokens_after_head.unsqueeze(0)
                    masked_teacher_ibot_softmax_centered = ibot_patch_loss.softmax_center_teacher(
                        teacher_masked_patch_tokens_after_head[:, :n_masked_patches], teacher_temp=teacher_temp
                    )
                    masked_teacher_ibot_softmax_centered = masked_teacher_ibot_softmax_centered.squeeze(0)
                    ibot_patch_loss.update_center(teacher_masked_patch_tokens_after_head[:n_masked_patches])

                else:  # sinkhorn_knopp
                    teacher_dino_softmax_centered_list = dino_loss.sinkhorn_knopp_teacher(
                        teacher_embedding_after_head, teacher_temp=teacher_temp
                    ).view(n_global_crops, -1, *teacher_embedding_after_head.shape[1:])

                    masked_teacher_ibot_softmax_centered = ibot_patch_loss.sinkhorn_knopp_teacher(
                        teacher_masked_patch_tokens_after_head,
                        teacher_temp=teacher_temp,
                        n_masked_patches_tensor=n_masked_patches_tensor,
                    )

                # Student
                (
                    student_global_embedding,
                    student_global_embedding_after_head,
                    student_local_embedding_after_head,
                    student_global_masked_patch_tokens_after_head,
                ) = student(global_crops, local_crops, masks, upper_bound, mask_indices_list)

                # Local DINO loss
                loss_dino_local_crops = dino_loss(
                    student_local_embedding_after_head.chunk(n_local_crops),
                    teacher_dino_softmax_centered_list,
                ) / (n_global_crops_loss_terms + n_local_crops_loss_terms)
                loss = args.dino_loss_weight * loss_dino_local_crops

                # Global DINO loss
                loss_scales = n_global_crops
                loss_dino_global_crops = (
                    dino_loss(
                        [student_global_embedding_after_head],
                        [
                            teacher_dino_softmax_centered_list.flatten(0, 1)
                        ],  # These were chunked and stacked in reverse so A is matched to B
                    )
                    * loss_scales
                    / (n_global_crops_loss_terms + n_local_crops_loss_terms)
                )
                loss += args.dino_loss_weight * loss_dino_global_crops

                # KoLeo loss
                loss_koleo = sum(koleo_loss(p) for p in student_global_embedding.chunk(n_global_crops))
                loss += args.koleo_loss_weight * loss_koleo

                # iBOT loss
                loss_ibot_patch = (
                    ibot_patch_loss.forward_masked(
                        student_global_masked_patch_tokens_after_head,
                        masked_teacher_ibot_softmax_centered,
                        student_masks_flat=masks,
                        masks_weight=masks_weight,
                        n_masked_patches=n_masked_patches,
                    )
                    * loss_scales
                    * ibot_loss_scale
                )
                loss += args.ibot_loss_weight * loss_ibot_patch

            if scaler is not None:
                scaler.scale(loss).backward()
                if optimizer_update is True:
                    if args.clip_grad_norm is not None:
                        scaler.unscale_(optimizer)
                        torch.nn.utils.clip_grad_norm_(net.parameters(), args.clip_grad_norm)

                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad()
                    if iter_update is True:
                        scheduler.step()

            else:
                loss.backward()
                if optimizer_update is True:
                    if args.clip_grad_norm is not None:
                        torch.nn.utils.clip_grad_norm_(net.parameters(), args.clip_grad_norm)

                    optimizer.step()
                    optimizer.zero_grad()
                    if iter_update is True:
                        scheduler.step()

            if optimizer_update is True:
                # EMA update for the student backbone
                with torch.no_grad():
                    m = 0.999
                    for param_q, param_k in zip(student.backbone.parameters(), student_backbone_ema.parameters()):
                        param_k.data.mul_(m).add_((1 - m) * param_q.detach().data)

            # Statistics
            running_loss.update(loss.detach())
            running_loss_dino_local.update(loss_dino_local_crops.detach())
            running_loss_dino_global.update(loss_dino_global_crops.detach())
            running_loss_koleo.update(loss_koleo.detach())
            running_loss_ibot_patch.update(loss_ibot_patch.detach())

            # Write statistics
            if (i == last_batch_idx) or (i + 1) % args.log_interval == 0:
                time_now = time.time()
                time_cost = time_now - start_time
                steps_processed_in_interval = i - last_idx
                rate = steps_processed_in_interval * (batch_size * args.world_size) / time_cost

                avg_time_per_step = time_cost / steps_processed_in_interval
                remaining_steps_in_epoch = last_batch_idx - i
                estimated_time_to_finish_epoch = remaining_steps_in_epoch * avg_time_per_step

                start_time = time_now
                last_idx = i
                cur_lr = max(scheduler.get_last_lr())

                running_loss.synchronize_between_processes(device)
                running_loss_dino_local.synchronize_between_processes(device)
                running_loss_dino_global.synchronize_between_processes(device)
                running_loss_koleo.synchronize_between_processes(device)
                running_loss_ibot_patch.synchronize_between_processes(device)
                with training_utils.single_handler_logging(logger, file_handler, enabled=not disable_tqdm) as log:
                    log.info(
                        f"[Trn] Epoch {epoch}/{epochs-1}, step {i+1}/{last_batch_idx+1}  "
                        f"Loss: {running_loss.avg:.4f}  "
                        f"Elapsed: {format_duration(time_now-epoch_start)}  "
                        f"ETA: {format_duration(estimated_time_to_finish_epoch)}  "
                        f"T: {time_cost:.1f}s  "
                        f"R: {rate:.1f} samples/s  "
                        f"LR: {cur_lr:.4e}"
                    )

                if training_utils.is_local_primary(args) is True:
                    summary_writer.add_scalars(
                        "loss",
                        {
                            "training": running_loss.avg,
                            "local": running_loss_dino_local.avg,
                            "global": running_loss_dino_global.avg,
                            "koleo": running_loss_koleo.avg,
                            "patch": running_loss_ibot_patch.avg,
                        },
                        ((epoch - 1) * len(training_dataset)) + (i * batch_size * args.world_size),
                    )

            # Update progress bar
            progress.update(n=batch_size * args.world_size)

        progress.close()

        # Epoch training metrics
        logger.info(f"[Trn] Epoch {epoch}/{epochs-1} training_loss: {running_loss.global_avg:.4f}")
        logger.info(f"[Trn] Epoch {epoch}/{epochs-1} dino_local_loss: {running_loss_dino_local.global_avg:.4f}")
        logger.info(f"[Trn] Epoch {epoch}/{epochs-1} dino_global_loss: {running_loss_dino_global.global_avg:.4f}")
        logger.info(f"[Trn] Epoch {epoch}/{epochs-1} koleo_loss: {running_loss_koleo.global_avg:.4f}")
        logger.info(f"[Trn] Epoch {epoch}/{epochs-1} ibot_patch_loss: {running_loss_ibot_patch.global_avg:.4f}")

        # Learning rate scheduler update
        if iter_update is False:
            scheduler.step()
        if last_lr != max(scheduler.get_last_lr()):
            last_lr = max(scheduler.get_last_lr())
            logger.info(f"Updated learning rate to: {last_lr}")

        if training_utils.is_local_primary(args) is True:
            # Checkpoint model
            if epoch % args.save_frequency == 0:
                fs_ops.checkpoint_model(
                    network_name,
                    epoch,
                    model_to_save,
                    signature,
                    {},
                    rgb_stats,
                    optimizer,
                    scheduler,
                    scaler,
                    None,
                )
                fs_ops.checkpoint_model(
                    backbone_name,
                    epoch,
                    student_backbone_ema,
                    backbone_signature,
                    {},
                    rgb_stats,
                    optimizer=None,
                    scheduler=None,
                    scaler=None,
                    model_base=None,
                )
                if args.keep_last is not None:
                    fs_ops.clean_checkpoints(network_name, args.keep_last)
                    fs_ops.clean_checkpoints(backbone_name, args.keep_last)

        # Epoch timing
        toc = time.time()
        logger.info(f"Total time: {format_duration(toc - tic)}")
        logger.info("---")

        # Reset counters
        epoch_start = time.time()
        start_time = epoch_start
        last_idx = 0

    summary_writer.close()

    # Checkpoint model
    if training_utils.is_local_primary(args) is True:
        fs_ops.checkpoint_model(
            network_name,
            epoch,
            model_to_save,
            signature,
            {},
            rgb_stats,
            optimizer,
            scheduler,
            scaler,
            None,
        )
        fs_ops.checkpoint_model(
            backbone_name,
            epoch,
            student_backbone_ema,
            backbone_signature,
            {},
            rgb_stats,
            optimizer=None,
            scheduler=None,
            scaler=None,
            model_base=None,
        )

    training_utils.shutdown_distributed_mode(args)


def get_args_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description="Pre-train model",
        epilog=(
            "Usage examples\n"
            "==============\n"
            "torchrun --nproc_per_node=2 -m birder.scripts.train_dino_v2_dist \\\n"
            "    --network vit_s16 \\\n"
            "    --teacher vit_l16 \\\n"
            "    --ibot-separate-head \\\n"
            "    --local-crop-size 98 98 \\\n"
            "    --centering sinkhorn_knopp \\\n"
            "    --opt adamw \\\n"
            "    --lr 0.0002 \\\n"
            "    --lr-scheduler cosine \\\n"
            "    --lr-cosine-min 1e-6 \\\n"
            "    --epochs 100 \\\n"
            "    --warmup-epochs 10 \\\n"
            "    --batch-size 16 \\\n"
            "    --wd 0.04 \\\n"
            "    --wd-end 0.2 \\\n"
            "    --norm-wd 0 \\\n"
            "    --clip-grad-norm 3 \\\n"
            "    --amp --amp-dtype bfloat16 \\\n"
            "    --compile \\\n"
            "    --data-path data/training data/raw_data\n"
        ),
        formatter_class=cli.ArgumentHelpFormatter,
    )
    parser.add_argument("-n", "--network", type=str, help="the neural network to use")
    parser.add_argument(
        "--model-config",
        action=cli.FlexibleDictAction,
        help=(
            "override the model default configuration, accepts key-value pairs or JSON "
            "('drop_path_rate=0.2' or '{\"units\": [3, 24, 36, 3], \"dropout\": 0.2}'"
        ),
    )
    parser.add_argument("-t", "--tag", type=str, help="add model tag")
    parser.add_argument("--teacher", type=str, help="the neural network to use as teacher")
    parser.add_argument(
        "--teacher-model-config",
        action=cli.FlexibleDictAction,
        help=(
            "override the teacher backbone default configuration, accepts key-value pairs or JSON "
            "('drop_path_rate=0.2' or '{\"units\": [3, 24, 36, 3], \"dropout\": 0.2}'"
        ),
    )
    parser.add_argument("--teacher-tag", type=str, help="teacher training logs tag")
    parser.add_argument("--teacher-epoch", type=int, metavar="N", help="load teacher weights from selected epoch")
    parser.add_argument("--dino-loss-weight", type=float, default=1.0, help="weight for the DINO loss component")
    parser.add_argument("--dino-out-dim", type=int, default=65536, help="dimensionality of the DINO head output")
    parser.add_argument("--head-bottleneck-dim", type=int, default=256, help="dimensionality of heads output")
    parser.add_argument("--koleo-loss-weight", type=float, default=0.1, help="weight for the KoLeo regularization loss")
    parser.add_argument("--ibot-loss-weight", type=float, default=1.0, help="weight for the iBOT loss component")
    parser.add_argument(
        "--ibot-mask-probability", type=float, default=0.5, help="probability of applying masking for iBOT training"
    )
    parser.add_argument(
        "--ibot-separate-head", default=False, action="store_true", help="use separate head for iBOT loss computation"
    )
    parser.add_argument("--ibot-out-dim", type=int, default=65536, help="dimensionality of the iBOT head output")
    parser.add_argument(
        "--warmup-teacher-temp",
        type=float,
        default=0.04,
        help="initial value for the teacher temperature, try decreasing it if the training loss does not decrease",
    )
    parser.add_argument(
        "--teacher-temp", type=float, default=0.07, help="final value (after linear warmup) of the teacher temperature"
    )
    parser.add_argument(
        "--warmup-teacher-temp-epochs", type=int, default=30, help="number of warmup epochs for the teacher temperature"
    )
    parser.add_argument(
        "--freeze-last-layer-epochs",
        default=1,
        type=int,
        help=(
            "number of epochs during which the output layer is frozen, "
            "try increasing this value if the loss does not decrease"
        ),
    )
    parser.add_argument("--local-crops-number", type=int, default=8, help="number of small local views to generate")
    parser.add_argument(
        "--local-crop-size", type=int, nargs="+", default=[96, 96], metavar=("H", "W"), help="local view size"
    )
    parser.add_argument(
        "--centering",
        type=str,
        choices=["centering", "sinkhorn_knopp"],
        default="centering",
        help="algorithm for centering",
    )
    training_cli.add_optimization_args(parser)
    training_cli.add_lr_wd_args(parser, wd_end=True)
    training_cli.add_lr_scheduler_args(parser)
    training_cli.add_training_schedule_args(parser, default_epochs=200)
    training_cli.add_input_args(parser)
    training_cli.add_data_aug_args(parser, default_level=5, default_min_scale=0.35, default_re_prob=0.0)
    training_cli.add_dataloader_args(parser, default_drop_last=True)
    training_cli.add_batch_norm_args(parser)
    training_cli.add_precision_args(parser)
    training_cli.add_compile_args(parser, teacher=True)
    training_cli.add_checkpoint_args(parser)
    training_cli.add_distributed_args(parser)
    training_cli.add_logging_and_debug_args(parser, default_log_interval=100)
    training_cli.add_training_data_args(parser, unsupervised=True)

    return parser


def validate_args(args: argparse.Namespace) -> None:
    args.data_path = [str(p) for p in args.data_path]
    args.size = cli.parse_size(args.size)
    args.local_crop_size = cli.parse_size(args.local_crop_size)

    # This will capture the common argument mistakes
    training_cli.common_args_validation(args)

    # Script specific checks
    if registry.exists(args.network, task=Task.IMAGE_CLASSIFICATION, net_type=MaskedTokenRetentionMixin) is False:
        raise cli.ValidationError(f"--network {args.network} not supported, see list-models tool for available options")
    if registry.exists(args.teacher, task=Task.IMAGE_CLASSIFICATION, net_type=MaskedTokenRetentionMixin) is False:
        raise cli.ValidationError(f"--teacher {args.teacher} not supported, see list-models tool for available options")


def args_from_dict(**kwargs: Any) -> argparse.Namespace:
    parser = get_args_parser()
    parser.set_defaults(**kwargs)
    args = parser.parse_args([])
    validate_args(args)

    return args


def main() -> None:
    parser = get_args_parser()
    args = parser.parse_args()
    validate_args(args)

    if settings.MODELS_DIR.exists() is False:
        logger.info(f"Creating {settings.MODELS_DIR} directory...")
        settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    if args.wds_cache_dir is not None and Path(args.wds_cache_dir).exists() is False:
        logger.info(f"Creating {args.wds_cache_dir} directory...")
        Path(args.wds_cache_dir).mkdir(parents=True, exist_ok=True)

    train(args)


if __name__ == "__main__":
    logger = logging.getLogger(getattr(__spec__, "name", __name__))
    main()
