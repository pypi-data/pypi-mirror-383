import logging
import unittest

import torch
import torch.nn.functional as F

from birder.common import masking
from birder.model_registry import registry
from birder.net.ssl import barlow_twins
from birder.net.ssl import byol
from birder.net.ssl import capi
from birder.net.ssl import data2vec
from birder.net.ssl import data2vec2
from birder.net.ssl import dino_v1
from birder.net.ssl import dino_v2
from birder.net.ssl import i_jepa
from birder.net.ssl import ibot
from birder.net.ssl import mmcr
from birder.net.ssl import simclr
from birder.net.ssl import sscd
from birder.net.ssl import vicreg

logging.disable(logging.CRITICAL)


class TestNetSSL(unittest.TestCase):
    def test_barlow_twins(self) -> None:
        batch_size = 4
        backbone = registry.net_factory("resnet_v1_50", 3, 0)
        net = barlow_twins.BarlowTwins(backbone, config={"projector_sizes": [512, 512, 512], "off_lambda": 0.005})

        # Test network
        out = net(torch.rand((batch_size, 3, 128, 128)), torch.rand((batch_size, 3, 128, 128)))
        self.assertFalse(torch.isnan(out).any())
        self.assertEqual(out.ndim, 0)

    def test_byol(self) -> None:
        batch_size = 2
        backbone = registry.net_factory("resnet_v1_18", 3, 0)
        net = byol.BYOL(backbone, config={"projection_size": 64, "projection_hidden_size": 128})

        # Test network
        out = net(torch.rand((batch_size, 3, 96, 96)))
        self.assertFalse(torch.isnan(out).any())
        self.assertEqual(out.ndim, 0)

    def test_capi(self) -> None:
        batch_size = 4
        size = (192, 192)
        num_clusters = 320
        backbone = registry.net_factory("vit_s16", 3, 0, size=size)
        input_size = (size[0] // backbone.max_stride, size[1] // backbone.max_stride)
        seq_len = input_size[0] * input_size[1]
        n_masked = int(seq_len * 0.65)
        prediction_subsampling = 0.05

        teacher = capi.CAPITeacher(
            backbone,
            config={"num_clusters": num_clusters, "bias": True, "n_sk_iter": 3, "target_temp": 0.06, "pred_temp": 0.12},
        )
        student = capi.CAPIStudent(
            backbone, config={"decoder_layers": 4, "decoder_dim": 256, "num_clusters": num_clusters}
        )
        mask_generator = masking.InverseRollBlockMasking(input_size, n_masked)

        masks = mask_generator(batch_size)
        ids_keep = masking.get_ids_keep(masks)
        n_predict = int(n_masked * prediction_subsampling)
        predict_indices = masking.get_random_masked_indices(masks, n_predict)
        masks = masking.mask_from_indices(predict_indices, seq_len)

        x = torch.rand(batch_size, 3, *size)
        # all_ids = torch.arange(input_size[0] * input_size[1]).unsqueeze(0).repeat(batch_size, 1)

        #
        # Simulate a full step
        #

        # Teacher
        (selected_assignments, clustering_loss) = teacher(x, None, predict_indices)
        self.assertFalse(torch.isnan(clustering_loss).any())
        self.assertFalse(torch.isnan(selected_assignments).any())
        self.assertEqual(selected_assignments.size(), (batch_size * n_predict, num_clusters))

        # Student
        pred = student(x, ids_keep, predict_indices)
        self.assertEqual(pred.size(), (masks.count_nonzero().item(), num_clusters))
        self.assertFalse(torch.isnan(pred).any())

        # Loss
        loss = -torch.sum(selected_assignments * F.log_softmax(pred / 0.12, dim=-1), dim=-1)
        self.assertFalse(torch.isnan(loss.sum() / len(loss)).any())
        self.assertEqual(loss.sum().ndim, 0)

        # Test with Hiera backbone
        backbone = registry.net_factory("hiera_tiny", 3, 0, size=size)
        input_size = (size[0] // backbone.max_stride, size[1] // backbone.max_stride)
        seq_len = input_size[0] * input_size[1]
        n_masked = int(seq_len * 0.65)
        prediction_subsampling = 0.05

        teacher = capi.CAPITeacher(
            backbone,
            config={"num_clusters": num_clusters, "bias": True, "n_sk_iter": 3, "target_temp": 0.06, "pred_temp": 0.12},
        )
        student = capi.CAPIStudent(
            backbone, config={"decoder_layers": 4, "decoder_dim": 256, "num_clusters": num_clusters}
        )
        mask_generator = masking.InverseRollBlockMasking(input_size, n_masked)

        masks = mask_generator(batch_size)
        ids_keep = masking.get_ids_keep(masks)
        n_predict = int(n_masked * prediction_subsampling)
        predict_indices = masking.get_random_masked_indices(masks, n_predict)
        masks = masking.mask_from_indices(predict_indices, seq_len)

        x = torch.rand(batch_size, 3, *size)

        # Teacher
        (selected_assignments, clustering_loss) = teacher(x, None, predict_indices)
        self.assertFalse(torch.isnan(clustering_loss).any())
        self.assertFalse(torch.isnan(selected_assignments).any())
        self.assertEqual(selected_assignments.size(), (batch_size * n_predict, num_clusters))

        # Student
        pred = student(x, ids_keep, predict_indices)
        self.assertEqual(pred.size(), (masks.count_nonzero().item(), num_clusters))
        self.assertFalse(torch.isnan(pred).any())

    def test_data2vec(self) -> None:
        batch_size = 2
        backbone = registry.net_factory("vit_t16", 3, 0, size=(96, 96))
        net = data2vec.Data2Vec(
            backbone, config={"normalize_targets": True, "average_top_k_layers": 6, "loss_beta": 2.0}
        )

        mask_generator = masking.BlockMasking((96 // backbone.stem_stride, 96 // backbone.stem_stride), 1, 3, 0.66, 1.5)
        masks = mask_generator(batch_size)

        # Test network
        out = net(torch.rand((batch_size, 3, 96, 96)), masks)
        self.assertFalse(torch.isnan(out).any())
        self.assertEqual(out.ndim, 0)

    def test_data2vec2(self) -> None:
        batch_size = 2
        backbone = registry.net_factory("vit_t16", 3, 0, size=(128, 128))
        net = data2vec2.Data2Vec2(
            backbone,
            config={
                "average_top_k_layers": 6,
                "decoder_dim": 128,
                "decoder_kernel_size": 3,
                "decoder_layers": 4,
                "clone_batch": 3,
                "cls_loss_weight": 0.1,
            },
        )

        mask_generator = masking.InverseRollBlockMasking(
            (128 // backbone.stem_stride, 128 // backbone.stem_stride),
            num_masking_patches=32,
            min_aspect=0.66,
            max_aspect=1.5,
        )
        masks = mask_generator(batch_size * 3)

        # Test network
        out = net(torch.rand((batch_size, 3, 128, 128)), masks)
        self.assertFalse(torch.isnan(out).any())
        self.assertEqual(out.ndim, 0)

    def test_dino_v1(self) -> None:
        batch_size = 4
        backbone = registry.net_factory("resnet_v2_18", 3, 0)
        net = dino_v1.DINO_v1(
            backbone,
            config={
                "out_dim": 128,
                "use_bn": True,
                "norm_last_layer": True,
                "num_layers": 3,
                "hidden_dim": 512,
                "bottleneck_dim": 256,
            },
        )

        # Test network
        out = net(
            [
                torch.rand((batch_size, 3, 128, 128)),
                torch.rand((batch_size, 3, 128, 128)),
                torch.rand((batch_size, 3, 96, 96)),
                torch.rand((batch_size, 3, 96, 96)),
                torch.rand((batch_size, 3, 96, 96)),
                torch.rand((batch_size, 3, 96, 96)),
            ]
        )
        self.assertFalse(torch.isnan(out).any())

        teacher_out = net([torch.rand((batch_size, 3, 128, 128)), torch.rand((batch_size, 3, 128, 128))])
        dino_loss = dino_v1.DINOLoss(
            128,
            6,
            warmup_teacher_temp=0.2,
            teacher_temp=0.8,
            warmup_teacher_temp_epochs=10,
            num_epochs=100,
            student_temp=0.5,
            center_momentum=0.99,
        )
        loss = dino_loss(out, teacher_out, epoch=2)
        self.assertFalse(torch.isnan(loss).any())
        self.assertEqual(loss.ndim, 0)

    # pylint: disable=too-many-locals
    def test_dino_v2(self) -> None:
        batch_size = 4
        size = (192, 192)
        backbone = registry.net_factory("vit_s16", 3, 0, size=size)
        backbone.set_dynamic_size()

        # Without iBOT head
        teacher = dino_v2.DINOv2Teacher(
            backbone,
            config={
                "dino_out_dim": 4096,
                "use_bn": False,
                "num_layers": 3,
                "hidden_dim": 2048,
                "head_bottleneck_dim": 256,
                "ibot_separate_head": False,
            },
        )
        student = dino_v2.DINOv2Student(
            backbone,
            config={
                "dino_out_dim": 4096,
                "use_bn": False,
                "num_layers": 3,
                "hidden_dim": 2048,
                "head_bottleneck_dim": 256,
                "ibot_separate_head": False,
            },
        )

        x = torch.rand(batch_size * 2, 3, *size)
        local_x = torch.rand(batch_size * 4, 3, size[0] // 2, size[1] // 2)
        mask_generator = masking.BlockMasking(
            (size[0] // backbone.stem_stride, size[1] // backbone.stem_stride), 1, 3, 0.66, 1.5
        )
        masks = mask_generator(batch_size * 2)  # Not quite the same, but close enough
        mask_indices_list = masks.flatten().nonzero().flatten()
        upper_bound = len(mask_indices_list) + 16

        with torch.no_grad():
            (teacher_embedding_after_head, teacher_masked_patch_tokens_after_head) = teacher(
                x, 2, upper_bound=upper_bound, mask_indices_list=mask_indices_list
            )

        (
            student_global_embedding,
            student_global_embedding_after_head,
            student_local_embedding_after_head,
            student_global_masked_patch_tokens_after_head,
        ) = student(x, local_x, masks, upper_bound, mask_indices_list)

        self.assertFalse(torch.isnan(teacher_embedding_after_head).any())
        self.assertEqual(teacher_embedding_after_head.size(), (batch_size * 2, 4096))
        self.assertFalse(torch.isnan(teacher_masked_patch_tokens_after_head).any())
        self.assertEqual(teacher_masked_patch_tokens_after_head.size(), (len(mask_indices_list), 4096))

        self.assertFalse(torch.isnan(student_global_embedding).any())
        self.assertEqual(student_global_embedding.size(), (batch_size * 2, backbone.embedding_size))
        self.assertFalse(torch.isnan(student_global_embedding_after_head).any())
        self.assertEqual(student_global_embedding_after_head.size(), (batch_size * 2, 4096))
        self.assertFalse(torch.isnan(student_local_embedding_after_head).any())
        self.assertEqual(student_local_embedding_after_head.size(), (batch_size * 4, 4096))
        self.assertFalse(torch.isnan(student_global_masked_patch_tokens_after_head).any())
        self.assertEqual(student_global_masked_patch_tokens_after_head.size(), (len(mask_indices_list), 4096))

        # With iBOT head
        teacher = dino_v2.DINOv2Teacher(
            backbone,
            config={
                "dino_out_dim": 4096,
                "use_bn": False,
                "num_layers": 3,
                "hidden_dim": 2048,
                "head_bottleneck_dim": 256,
                "ibot_separate_head": True,
                "ibot_out_dim": 4096,
            },
        )
        student = dino_v2.DINOv2Student(
            backbone,
            config={
                "dino_out_dim": 4096,
                "use_bn": False,
                "num_layers": 3,
                "hidden_dim": 2048,
                "head_bottleneck_dim": 256,
                "ibot_separate_head": True,
                "ibot_out_dim": 4096,
            },
        )

        x = torch.rand(batch_size * 2, 3, *size)
        local_x = torch.rand(batch_size * 4, 3, size[0] // 2, size[1] // 2)
        mask_generator = masking.BlockMasking(
            (size[0] // backbone.stem_stride, size[1] // backbone.stem_stride), 1, 3, 0.66, 1.5
        )
        masks = mask_generator(batch_size * 2)  # Not quite the same, but close enough
        masks = masks.to(torch.long)
        mask_indices_list = masks.flatten().nonzero().flatten()
        upper_bound = len(mask_indices_list) + 16

        with torch.no_grad():
            (teacher_embedding_after_head, teacher_masked_patch_tokens_after_head) = teacher(
                x, 2, upper_bound=upper_bound, mask_indices_list=mask_indices_list
            )

        (
            student_global_embedding,
            student_global_embedding_after_head,
            student_local_embedding_after_head,
            student_global_masked_patch_tokens_after_head,
        ) = student(x, local_x, masks, upper_bound, mask_indices_list)

        self.assertFalse(torch.isnan(teacher_embedding_after_head).any())
        self.assertEqual(teacher_embedding_after_head.size(), (batch_size * 2, 4096))
        self.assertFalse(torch.isnan(teacher_masked_patch_tokens_after_head).any())
        self.assertEqual(teacher_masked_patch_tokens_after_head.size(), (len(mask_indices_list), 4096))

        self.assertFalse(torch.isnan(student_global_embedding).any())
        self.assertEqual(student_global_embedding.size(), (batch_size * 2, backbone.embedding_size))
        self.assertFalse(torch.isnan(student_global_embedding_after_head).any())
        self.assertEqual(student_global_embedding_after_head.size(), (batch_size * 2, 4096))
        self.assertFalse(torch.isnan(student_local_embedding_after_head).any())
        self.assertEqual(student_local_embedding_after_head.size(), (batch_size * 4, 4096))
        self.assertFalse(torch.isnan(student_global_masked_patch_tokens_after_head).any())
        self.assertEqual(student_global_masked_patch_tokens_after_head.size(), (len(mask_indices_list), 4096))

        # Loss
        dino_loss = dino_v2.DINOLoss(4096, student_temp=0.1, center_momentum=0.9)
        koleo_loss = dino_v2.KoLeoLoss()
        ibot_patch_loss = dino_v2.iBOTPatchLoss(4096, student_temp=0.1, center_momentum=0.9)

        # Loss centering
        teacher_temp = 0.04
        n_masked_patches = len(mask_indices_list)

        teacher_dino_softmax_centered_list = dino_loss.softmax_center_teacher(
            teacher_embedding_after_head, teacher_temp=teacher_temp
        ).view(2, -1, *teacher_embedding_after_head.shape[1:])
        dino_loss.update_center(teacher_embedding_after_head)

        teacher_masked_patch_tokens_after_head_d = teacher_masked_patch_tokens_after_head.unsqueeze(0)
        masked_teacher_ibot_softmax_centered = ibot_patch_loss.softmax_center_teacher(
            teacher_masked_patch_tokens_after_head_d[:, :n_masked_patches], teacher_temp=teacher_temp
        )
        masked_teacher_ibot_softmax_centered = masked_teacher_ibot_softmax_centered.squeeze(0)
        ibot_patch_loss.update_center(teacher_masked_patch_tokens_after_head_d[:n_masked_patches])

        self.assertFalse(torch.isnan(teacher_dino_softmax_centered_list).any())
        self.assertEqual(teacher_dino_softmax_centered_list.size(), (2, batch_size, 4096))
        self.assertFalse(torch.isnan(masked_teacher_ibot_softmax_centered).any())
        self.assertEqual(masked_teacher_ibot_softmax_centered.size(), (len(mask_indices_list), 4096))

        # Loss centering - Sinkhorn Knopp
        teacher_dino_softmax_centered_list = dino_loss.sinkhorn_knopp_teacher(
            teacher_embedding_after_head, teacher_temp=teacher_temp
        ).view(2, -1, *teacher_embedding_after_head.shape[1:])

        masked_teacher_ibot_softmax_centered = ibot_patch_loss.sinkhorn_knopp_teacher(
            teacher_masked_patch_tokens_after_head,
            teacher_temp=teacher_temp,
            n_masked_patches_tensor=torch.full((1,), fill_value=mask_indices_list.size(0), dtype=torch.long),
        )

        self.assertFalse(torch.isnan(teacher_dino_softmax_centered_list).any())
        self.assertEqual(teacher_dino_softmax_centered_list.size(), (2, batch_size, 4096))
        self.assertFalse(torch.isnan(masked_teacher_ibot_softmax_centered).any())
        self.assertEqual(masked_teacher_ibot_softmax_centered.size(), (len(mask_indices_list), 4096))

        # DINO loss
        loss_dino = dino_loss(student_local_embedding_after_head.chunk(4), teacher_dino_softmax_centered_list)
        self.assertFalse(torch.isnan(loss_dino).any())
        self.assertEqual(loss_dino.ndim, 0)

        # KoLeo loss
        loss_koleo = sum(koleo_loss(p) for p in student_global_embedding.chunk(2))
        self.assertFalse(torch.isnan(loss_koleo).any())
        self.assertEqual(loss_koleo.ndim, 0)

        # iBOT loss
        masks_weight = (1 / masks.sum(-1).clamp(min=1.0)).unsqueeze(-1).expand_as(masks)[masks.bool()]
        loss_ibot_patch = ibot_patch_loss.forward_masked(
            student_global_masked_patch_tokens_after_head,
            masked_teacher_ibot_softmax_centered,
            student_masks_flat=masks,
            masks_weight=masks_weight,
            n_masked_patches=n_masked_patches,
        )
        self.assertFalse(torch.isnan(loss_ibot_patch).any())
        self.assertEqual(loss_ibot_patch.ndim, 0)

    def test_i_jepa(self) -> None:
        batch_size = 4
        size = (192, 192)
        backbone = registry.net_factory("vit_s16", 3, 0, size=size)
        input_size = (size[0] // backbone.stem_stride, size[1] // backbone.stem_stride)
        predictor = i_jepa.VisionTransformerPredictor(
            input_size,
            backbone.embedding_size,
            128,
            512,
            8,
            2,
            0.0,
        )
        mask_generator = i_jepa.MultiBlockMasking(
            input_size,
            enc_mask_scale=(0.85, 1.0),
            pred_mask_scale=(0.15, 0.25),
            aspect_ratio=(0.75, 1.5),
            n_enc=2,
            n_pred=3,
            min_keep=10,
            allow_overlap=False,
        )
        masks = mask_generator(batch_size)
        enc_masks = masks[0]
        pred_masks = masks[1]

        x = torch.rand(batch_size, 3, *size)

        #
        # Simulate a full step
        #

        # Target encoder
        h = backbone.masked_encoding_omission(x)["tokens"]
        h = h[:, backbone.num_special_tokens :, :]  # Remove special tokens
        h = i_jepa.apply_masks(h, pred_masks)
        h = i_jepa.repeat_interleave_batch(h, batch_size, repeat=len(enc_masks))

        # Context
        z = torch.concat([backbone.masked_encoding_omission(x, enc_mask)["tokens"] for enc_mask in enc_masks], dim=0)
        z = z[:, backbone.num_special_tokens :, :]  # Remove special tokens
        z = predictor(z, enc_masks, pred_masks)

        loss = F.smooth_l1_loss(z, h)

        self.assertEqual(h.size(0), batch_size * len(enc_masks) * len(pred_masks))
        self.assertEqual(z.size(0), batch_size * len(enc_masks) * len(pred_masks))

        self.assertEqual(h.size(2), backbone.embedding_size)
        self.assertEqual(z.size(2), backbone.embedding_size)

        self.assertEqual(h.size(1), z.size(1))

        self.assertEqual(loss.ndim, 0)

    def test_ibot(self) -> None:
        batch_size = 4
        backbone = registry.net_factory("vit_b32", 3, 0)
        backbone.set_dynamic_size()
        net = ibot.iBOT(
            backbone,
            config={
                "out_dim": 128,
                "norm_last_layer": True,
                "num_layers": 3,
                "hidden_dim": 512,
                "bottleneck_dim": 256,
                "patch_out_dim": 192,
                "shared_head": False,
            },
        )

        # Test network
        images = [
            # Global
            torch.rand((batch_size, 3, 128, 128)),
            torch.rand((batch_size, 3, 128, 128)),
            # Local
            torch.rand((batch_size, 3, 96, 96)),
            torch.rand((batch_size, 3, 96, 96)),
            torch.rand((batch_size, 3, 96, 96)),
            torch.rand((batch_size, 3, 96, 96)),
        ]

        mask_generator = masking.BlockMasking(
            (128 // backbone.stem_stride, 128 // backbone.stem_stride), 1, 3, 0.66, 1.5
        )
        masks = mask_generator(batch_size * 2)

        (embedding_g, features_g) = net(torch.concat(images[:2], dim=0), masks=masks)
        self.assertFalse(torch.isnan(embedding_g).any())
        self.assertFalse(torch.isnan(features_g).any())
        self.assertEqual(features_g.size(), (batch_size * 2, (128 // 32) ** 2, 192))
        self.assertEqual(embedding_g.size(), (batch_size * 2, 128))

        (embedding_l, features_l) = net(torch.concat(images[2:], dim=0), masks=None)
        self.assertFalse(torch.isnan(embedding_l).any())
        self.assertFalse(torch.isnan(features_l).any())
        self.assertEqual(features_l.size(), (batch_size * 4, (96 // 32) ** 2, 192))
        self.assertEqual(embedding_l.size(), (batch_size * 4, 128))

        ibot_loss = ibot.iBOTLoss(
            128,
            192,
            num_global_crops=2,
            num_local_crops=4,
            warmup_teacher_temp=0.1,
            teacher_temp=0.9,
            warmup_teacher_temp2=0.2,
            teacher_temp2=0.99,
            warmup_teacher_temp_epochs=5,
            epochs=100,
            student_temp=0.5,
            center_momentum=0.98,
            center_momentum2=0.97,
            lambda1=0.2,
            lambda2=0.1,
            mim_start_epoch=1,
        )

        loss = ibot_loss.forward(
            embedding_g,
            features_g,
            torch.rand_like(embedding_g),
            torch.rand_like(features_g),
            student_local_embedding=embedding_l,
            student_mask=masks,
            epoch=2,
        )

        self.assertFalse(torch.isnan(loss["all"]).any())
        self.assertFalse(torch.isnan(loss["embedding"]).any())
        self.assertFalse(torch.isnan(loss["features"]).any())

        self.assertEqual(loss["all"].ndim, 0)
        self.assertEqual(loss["embedding"].ndim, 0)
        self.assertEqual(loss["features"].ndim, 0)

    def test_mmcr(self) -> None:
        batch_size = 4
        backbone = registry.net_factory("resnet_v1_50", 3, 0)
        net = mmcr.MMCR(backbone, config={"projector_dims": [512, 512, 512]})
        mmcr_loss = mmcr.MMCRMomentumLoss(0.0, 2)

        # Test network
        (out, out_m) = net(torch.rand((batch_size, 2, 3, 128, 128)))
        self.assertFalse(torch.isnan(out).any())
        self.assertEqual(out.ndim, 2)
        self.assertFalse(torch.isnan(out_m).any())
        self.assertEqual(out_m.ndim, 2)

        # Test loss
        loss = mmcr_loss(out, out_m)
        self.assertFalse(torch.isnan(loss).any())
        self.assertEqual(loss.ndim, 0)

    def test_simclr(self) -> None:
        batch_size = 4
        backbone = registry.net_factory("resnet_v2_18", 3, 0)
        net = simclr.SimCLR(
            backbone,
            config={
                "projection_dim": 96,
                "projection_hidden_dim": 128,
                "temperature": 0.1,
            },
        )

        # Test network
        out = net(torch.rand((batch_size, 3, 128, 128)), torch.rand((batch_size, 3, 128, 128)))
        self.assertFalse(torch.isnan(out).any())
        self.assertEqual(out.ndim, 0)

    def test_sscd(self) -> None:
        batch_size = 4
        backbone = registry.net_factory("resnet_v2_18", 3, 512)
        net = sscd.SSCD(backbone)
        out = net(torch.rand(batch_size, 3, 128, 128))
        self.assertFalse(torch.isnan(out).any())
        self.assertEqual(out.ndim, 2)

    def test_vicreg(self) -> None:
        batch_size = 4
        backbone = registry.net_factory("resnet_v1_18", 3, 0)
        net = vicreg.VICReg(
            backbone,
            config={
                "mlp_dim": 128,
                "batch_size": batch_size,
                "sim_coeff": 0.1,
                "std_coeff": 0.1,
                "cov_coeff": 0.1,
            },
        )

        # Test network
        out = net(torch.rand((batch_size, 3, 128, 128)), torch.rand((batch_size, 3, 128, 128)))
        self.assertFalse(torch.isnan(out).any())
        self.assertEqual(out.ndim, 0)
