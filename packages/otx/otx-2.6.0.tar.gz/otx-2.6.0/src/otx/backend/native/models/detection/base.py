# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Class definition for detection model entity used in OTX."""

# type: ignore[override]

from __future__ import annotations

import logging as log
import types
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Callable, Iterator, Literal, Sequence

import torch
from torchmetrics import Metric, MetricCollection
from torchvision import tv_tensors

from otx.backend.native.models.base import DataInputParams, DefaultOptimizerCallable, DefaultSchedulerCallable, OTXModel
from otx.backend.native.models.utils.utils import InstanceData
from otx.backend.native.schedulers import LRSchedulerListCallable
from otx.backend.native.tools.explain.explain_algo import feature_vector_fn
from otx.backend.native.tools.tile_merge import DetectionTileMerge
from otx.config.data import TileConfig
from otx.data.entity.base import ImageInfo, OTXBatchLossEntity
from otx.data.entity.tile import OTXTileBatchDataEntity
from otx.data.entity.torch import OTXDataBatch, OTXPredBatch
from otx.data.entity.utils import stack_batch
from otx.metrics import MetricCallable, MetricInput
from otx.metrics.fmeasure import FMeasure, MeanAveragePrecisionFMeasureCallable
from otx.types.export import TaskLevelExportParameters
from otx.types.label import LabelInfoTypes
from otx.types.task import OTXTaskType

if TYPE_CHECKING:
    from lightning.pytorch.cli import LRSchedulerCallable, OptimizerCallable

    from otx.backend.native.models.detection.detectors import SingleStageDetector


class OTXDetectionModel(OTXModel):
    """Base class for the detection models used in OTX.

    Args:
        label_info (LabelInfoTypes | int | Sequence): Information about the labels used in the model.
            If `int` is given, label info will be constructed from number of classes,
            if `Sequence` is given, label info will be constructed from the sequence of label names.
        data_input_params (DataInputParams): Parameters for data input.
        model_name (str, optional): Name of the model. Defaults to "otx_detection_model".
        optimizer (OptimizerCallable, optional): Optimizer callable. Defaults to DefaultOptimizerCallable.
        scheduler (LRSchedulerCallable | LRSchedulerListCallable, optional): Scheduler callable.
        Defaults to DefaultSchedulerCallable.
        metric (MetricCallable, optional): Metric callable. Defaults to MeanAveragePrecisionFMeasureCallable.
        torch_compile (bool, optional): Whether to use torch compile. Defaults to False.
        tile_config (TileConfig, optional): Configuration for tiling. Defaults to TileConfig(enable_tiler=False).
        explain_mode (bool, optional): Whether to enable explain mode. Defaults to False.
    """

    def __init__(
        self,
        label_info: LabelInfoTypes | int | Sequence,
        data_input_params: DataInputParams,
        model_name: str = "otx_detection_model",
        optimizer: OptimizerCallable = DefaultOptimizerCallable,
        scheduler: LRSchedulerCallable | LRSchedulerListCallable = DefaultSchedulerCallable,
        metric: MetricCallable = MeanAveragePrecisionFMeasureCallable,
        torch_compile: bool = False,
        tile_config: TileConfig = TileConfig(enable_tiler=False),
    ) -> None:
        super().__init__(
            label_info=label_info,
            model_name=model_name,
            task=OTXTaskType.DETECTION,
            data_input_params=data_input_params,
            optimizer=optimizer,
            scheduler=scheduler,
            metric=metric,
            torch_compile=torch_compile,
            tile_config=tile_config,
        )

        self.model.feature_vector_fn = feature_vector_fn
        self.model.explain_fn = self.get_explain_fn()

    def test_step(self, batch: OTXDataBatch, batch_idx: int) -> OTXPredBatch:
        """Perform a single test step on a batch of data from the test set.

        :param batch: A batch of data (a tuple) containing the input tensor of images and target
            labels.
        :param batch_idx: The index of the current batch.
        """
        preds = self.forward(inputs=batch)

        if isinstance(preds, OTXBatchLossEntity):
            raise TypeError(preds)

        # 1. Filter outputs by threshold
        preds = self._filter_outputs_by_threshold(preds)
        metric_inputs = self._convert_pred_entity_to_compute_metric(preds, batch)

        # 2. Update metric
        if isinstance(metric_inputs, dict):
            self.metric.update(**metric_inputs)
            return preds

        if isinstance(metric_inputs, list) and all(isinstance(inp, dict) for inp in metric_inputs):
            for inp in metric_inputs:
                self.metric.update(**inp)
            return preds

        raise TypeError(metric_inputs)

    def predict_step(
        self,
        batch: OTXDataBatch | OTXTileBatchDataEntity,
        batch_idx: int,
        dataloader_idx: int = 0,
    ) -> OTXPredBatch:
        """Step function called during PyTorch Lightning Trainer's predict."""
        if self.explain_mode:
            return self._filter_outputs_by_threshold(self.forward_explain(inputs=batch))

        outputs = self._filter_outputs_by_threshold(self.forward(inputs=batch))  # type: ignore[arg-type]

        if isinstance(outputs, OTXBatchLossEntity):
            raise TypeError(outputs)

        return outputs

    def _filter_outputs_by_threshold(self, outputs: OTXPredBatch) -> OTXPredBatch:
        # NOTE: best_confidence_threshold comes from:
        # 1. During validation: FMeasure metric computes optimal threshold, stored in hparams via _log_metrics
        # 2. During test/predict: Uses the threshold computed during validation (from hparams)
        # 3. If no threshold available: defaults to 0.5
        scores = []
        bboxes = []
        labels = []
        if outputs.scores is not None and outputs.bboxes is not None and outputs.labels is not None:
            for score, bbox, label in zip(outputs.scores, outputs.bboxes, outputs.labels):
                filtered_idx = torch.where(score > self.best_confidence_threshold)
                scores.append(score[filtered_idx])
                bboxes.append(tv_tensors.wrap(bbox[filtered_idx], like=bbox))
                labels.append(label[filtered_idx])

        outputs.scores = scores
        outputs.bboxes = bboxes
        outputs.labels = labels
        return outputs

    def _customize_inputs(
        self,
        entity: OTXDataBatch,
        pad_size_divisor: int = 32,
        pad_value: int = 0,
    ) -> dict[str, Any]:
        if isinstance(entity.images, list):
            entity.images, entity.imgs_info = stack_batch(  # type: ignore[assignment]
                entity.images,
                entity.imgs_info,  # type: ignore[arg-type]
                pad_size_divisor=pad_size_divisor,
                pad_value=pad_value,
            )
        inputs: dict[str, Any] = {}

        inputs["entity"] = entity
        inputs["mode"] = "loss" if self.training else "predict"

        return inputs

    def _customize_outputs(
        self,
        outputs: list[InstanceData] | dict | None,
        inputs: OTXDataBatch,
    ) -> OTXPredBatch | OTXBatchLossEntity:
        if self.training:
            if not isinstance(outputs, dict):
                raise TypeError(outputs)

            losses = OTXBatchLossEntity()
            for k, v in outputs.items():
                if isinstance(v, list):
                    losses[k] = sum(v)
                elif isinstance(v, torch.Tensor):
                    losses[k] = v
                else:
                    msg = f"Loss output should be list or torch.tensor but got {type(v)}"
                    raise TypeError(msg)
            return losses

        scores = []
        bboxes = []
        labels = []
        predictions = outputs["predictions"] if isinstance(outputs, dict) else outputs
        for img_info, prediction in zip(inputs.imgs_info, predictions):  # type: ignore[union-attr,arg-type]
            if not isinstance(prediction, InstanceData):
                raise TypeError(prediction)

            scores.append(prediction.scores)  # type: ignore[attr-defined]
            bboxes.append(
                tv_tensors.BoundingBoxes(
                    prediction.bboxes,  # type: ignore[attr-defined]
                    format="XYXY",
                    canvas_size=img_info.ori_shape,  # type: ignore[union-attr]
                ),
            )
            labels.append(prediction.labels)  # type: ignore[attr-defined]

        if self.explain_mode:
            if not isinstance(outputs, dict):
                msg = f"Model output should be a dict, but got {type(outputs)}."
                raise ValueError(msg)

            if "feature_vector" not in outputs:
                msg = "No feature vector in the model output."
                raise ValueError(msg)

            if "saliency_map" not in outputs:
                msg = "No saliency maps in the model output."
                raise ValueError(msg)

            return OTXPredBatch(
                batch_size=len(predictions),
                images=inputs.images,
                imgs_info=inputs.imgs_info,
                scores=scores,
                bboxes=bboxes,
                labels=labels,
                saliency_map=outputs["saliency_map"],
                feature_vector=[
                    feature_vector.detach().unsqueeze(0).to(torch.float32)
                    for feature_vector in outputs["feature_vector"]
                ],
            )

        return OTXPredBatch(
            batch_size=len(predictions),
            images=inputs.images,
            imgs_info=inputs.imgs_info,
            scores=scores,
            bboxes=bboxes,
            labels=labels,
        )

    def forward_tiles(self, inputs: OTXTileBatchDataEntity) -> OTXPredBatch:
        """Unpack detection tiles.

        Args:
            inputs (TileBatchDetDataEntity): Tile batch data entity.

        Returns:
            DetBatchPredEntity: Merged detection prediction.
        """
        tile_preds: list[OTXPredBatch] = []
        tile_attrs: list[list[dict[str, int | str]]] = []
        merger = DetectionTileMerge(
            inputs.imgs_info,
            self.num_classes,
            self.tile_config,
            self.explain_mode,
        )
        for batch_tile_attrs, batch_tile_input in inputs.unbind():
            output = self.forward_explain(batch_tile_input) if self.explain_mode else self.forward(batch_tile_input)
            if isinstance(output, OTXBatchLossEntity):
                msg = "Loss output is not supported for tile merging"
                raise TypeError(msg)
            tile_preds.append(output)
            tile_attrs.append(batch_tile_attrs)
        pred_entities = merger.merge(tile_preds, tile_attrs)

        pred_entity = OTXPredBatch(
            batch_size=inputs.batch_size,
            images=[pred_entity.image for pred_entity in pred_entities],
            imgs_info=[pred_entity.img_info for pred_entity in pred_entities],
            scores=[pred_entity.scores for pred_entity in pred_entities],
            bboxes=[pred_entity.bboxes for pred_entity in pred_entities],
            labels=[pred_entity.label for pred_entity in pred_entities],
        )
        if self.explain_mode:
            pred_entity.saliency_map = [pred_entity.saliency_map for pred_entity in pred_entities]
            pred_entity.feature_vector = [pred_entity.feature_vector for pred_entity in pred_entities]

        return pred_entity

    def forward_for_tracing(self, inputs: torch.Tensor) -> list[InstanceData]:
        """Forward function for export."""
        shape = (int(inputs.shape[2]), int(inputs.shape[3]))
        meta_info = {
            "pad_shape": shape,
            "batch_input_shape": shape,
            "img_shape": shape,
            "scale_factor": (1.0, 1.0),
        }
        meta_info_list = [meta_info] * len(inputs)
        return self.model.export(inputs, meta_info_list, explain_mode=self.explain_mode)

    @property
    def _export_parameters(self) -> TaskLevelExportParameters:
        """Defines parameters required to export a particular model implementation."""
        return super()._export_parameters.wrap(
            model_type="ssd",
            task_type="detection",
            confidence_threshold=self.hparams.get("best_confidence_threshold", None),
            iou_threshold=0.5,
            tile_config=self.tile_config if self.tile_config.enable_tiler else None,
        )

    def _convert_pred_entity_to_compute_metric(
        self,
        preds: OTXPredBatch,  # type: ignore[override]
        inputs: OTXDataBatch,  # type: ignore[override]
    ) -> MetricInput:
        return {
            "preds": [
                {
                    "boxes": bboxes.data,
                    "scores": scores.type(torch.float32),
                    "labels": labels,
                }
                for bboxes, scores, labels in zip(preds.bboxes, preds.scores, preds.labels)  # type: ignore[arg-type]
            ],
            "target": [
                {
                    "boxes": bboxes.data,
                    "labels": labels,
                }
                for bboxes, labels in zip(inputs.bboxes, inputs.labels)  # type: ignore[arg-type]
            ],
        }

    def on_load_checkpoint(self, ckpt: dict[str, Any]) -> None:
        """Load state_dict from checkpoint.

        For detection, it is needed to update confidence threshold and F1 score information when
        the metric is FMeasure.
        """
        hyper_parameters = ckpt.get("hyper_parameters", {})

        # Load best confidence threshold (legacy and new format)
        if best_confidence_threshold := ckpt.get("confidence_threshold") or hyper_parameters.get(
            "best_confidence_threshold",
            None,
        ):
            self.hparams["best_confidence_threshold"] = best_confidence_threshold
        super().on_load_checkpoint(ckpt)

    def _log_metrics(self, meter: Metric, key: Literal["val", "test"], **compute_kwargs) -> None:
        """This function is called every epoch.

        Args:
            meter: Metric object
            key: "val" or "test"
            compute_kwargs: Additional keyword arguments for the metric computation

        """
        if key == "val":
            super()._log_metrics(meter, key)

            fmeasure = None
            if isinstance(meter, MetricCollection) and (fmeasure := getattr(meter, "FMeasure", None)):
                pass  # fmeasure is set
            elif isinstance(meter, FMeasure):
                fmeasure = meter

            if fmeasure is not None and hasattr(fmeasure, "best_confidence_threshold"):
                self.hparams["best_confidence_threshold"] = fmeasure.best_confidence_threshold

        if key == "test":
            # NOTE: Test metric logging should use `best_confidence_threshold` in the loaded checkpoint.
            best_confidence_threshold = self.hparams.get("best_confidence_threshold", None)
            compute_kwargs = (
                {"best_confidence_threshold": best_confidence_threshold} if best_confidence_threshold else {}
            )

            super()._log_metrics(meter, key, **compute_kwargs)

    @property
    def best_confidence_threshold(self) -> float:
        """Best confidence threshold to filter outputs.

        Always returns the current value from hparams, with 0.5 as fallback.
        This ensures the threshold is always up-to-date after validation updates it.
        """
        threshold = self.hparams.get("best_confidence_threshold", None)
        if threshold is None:
            # Only log warning once to avoid spam
            if not getattr(self, "_threshold_warning_logged", False):
                log.warning("There is no predefined best_confidence_threshold, 0.5 will be used as default.")
                self._threshold_warning_logged = True
            return 0.5
        return float(threshold)

    def get_dummy_input(self, batch_size: int = 1) -> OTXDataBatch:  # type: ignore[override]
        """Returns a dummy input for detection model."""
        images = [torch.rand(3, *self.data_input_params.input_size) for _ in range(batch_size)]
        infos = []
        for i, img in enumerate(images):
            infos.append(
                ImageInfo(
                    img_idx=i,
                    img_shape=img.shape,
                    ori_shape=img.shape,
                ),
            )
        return OTXDataBatch(batch_size, images, imgs_info=infos)  # type: ignore[arg-type]

    def forward_explain(self, inputs: OTXDataBatch | OTXTileBatchDataEntity) -> OTXPredBatch:
        """Model forward function."""
        from otx.backend.native.tools.explain.explain_algo import feature_vector_fn

        if isinstance(inputs, OTXTileBatchDataEntity):
            return self.forward_tiles(inputs)

        self.model.feature_vector_fn = feature_vector_fn
        self.model.explain_fn = self.get_explain_fn()

        # If customize_inputs is overridden
        outputs = (
            self._forward_explain_detection(self.model, **self._customize_inputs(inputs))
            if self._customize_inputs != OTXDetectionModel._customize_inputs
            else self._forward_explain_detection(self.model, inputs)
        )
        return (
            self._customize_outputs(outputs, inputs)
            if self._customize_outputs != OTXDetectionModel._customize_outputs
            else outputs["predictions"]
        )

    @staticmethod
    def _forward_explain_detection(
        self: SingleStageDetector,
        entity: OTXDataBatch,
        mode: str = "tensor",
    ) -> dict[str, torch.Tensor]:
        """Forward func of the BaseDetector instance, which located in is in OTXDetectionModel().model."""
        backbone_feat = self.extract_feat(entity.images)
        bbox_head_feat = self.bbox_head.forward(backbone_feat)

        # Process the first output form bbox detection head: classification scores
        feature_vector = self.feature_vector_fn(backbone_feat)
        saliency_map = self.explain_fn(bbox_head_feat[0])

        if mode == "predict":
            predictions = self.bbox_head.predict(backbone_feat, entity)

        elif mode == "tensor":
            predictions = bbox_head_feat
        else:
            msg = f'Invalid mode "{mode}".'
            raise RuntimeError(msg)

        return {
            "predictions": predictions,
            "feature_vector": feature_vector,
            "saliency_map": saliency_map,
        }

    def get_explain_fn(self) -> Callable:
        """Returns explain function."""
        from otx.backend.native.models.detection.heads.ssd_head import SSDHeadModule
        from otx.backend.native.tools.explain.explain_algo import DetClassProbabilityMap

        # SSD-like heads also have background class
        background_class = hasattr(self.model, "bbox_head") and isinstance(
            self.model.bbox_head,
            SSDHeadModule,
        )  # TODO (sungchul): revert module's name?
        tiling_mode = self.tile_config.enable_tiler if hasattr(self, "tile_config") else False
        explainer = DetClassProbabilityMap(
            num_classes=self.num_classes + background_class,
            num_anchors=self.get_num_anchors(),
            use_cls_softmax=not tiling_mode,
        )
        return explainer.func

    @contextmanager
    def export_model_forward_context(self) -> Iterator[None]:
        """A context manager for managing the model's forward function during model exportation.

        It temporarily modifies the model's forward function to generate output sinks
        for explain results during the model graph tracing.
        """
        try:
            self._reset_model_forward()
            yield
        finally:
            self._restore_model_forward()

    def _reset_model_forward(self) -> None:
        if not self.explain_mode:
            return

        self.model.explain_fn = self.get_explain_fn()
        forward_with_explain = self._forward_explain_detection

        self.original_model_forward = self.model.forward

        func_type = types.MethodType
        # Patch method
        self.model.forward = func_type(forward_with_explain, self.model)

    def _restore_model_forward(self) -> None:
        if not self.explain_mode:
            return

        if not self.original_model_forward:
            msg = "Original model forward was not saved."
            raise RuntimeError(msg)

        func_type = types.MethodType
        self.model.forward = func_type(self.original_model_forward, self.model)
        self.original_model_forward = None

    def get_num_anchors(self) -> list[int]:
        """Gets the anchor configuration from model."""
        if hasattr(self.model, "bbox_head") and (
            anchor_generator := getattr(self.model.bbox_head, "prior_generator", None)
        ):
            return (
                anchor_generator.num_base_anchors
                if hasattr(anchor_generator, "num_base_anchors")
                else anchor_generator.num_base_priors
            )

        return [1] * 10
