# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
"""Class definition for classification model entity used in OTX."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import torch

from otx.backend.openvino.models.base import OVModel
from otx.data.entity.torch import OTXDataBatch, OTXPredBatch
from otx.metrics import MetricInput
from otx.metrics.accuracy import (
    MultiLabelClsMetricCallable,
)
from otx.types.task import OTXTaskType

if TYPE_CHECKING:
    from model_api.models.result import ClassificationResult

    from otx.metrics import MetricCallable
    from otx.types import PathLike


class OVMultilabelClassificationModel(OVModel):
    """Multilabel classification model compatible for OpenVINO IR inference.

    It can consume OpenVINO IR model path or model name from Intel OMZ repository
    and create the OTX classification model compatible for OTX testing pipeline.
    """

    def __init__(
        self,
        model_path: PathLike,
        model_type: str = "Classification",
        async_inference: bool = True,
        max_num_requests: int | None = None,
        use_throughput_mode: bool = True,
        model_api_configuration: dict[str, Any] | None = None,
        metric: MetricCallable = MultiLabelClsMetricCallable,
        **kwargs,
    ) -> None:
        """Initialize the multilabel classification model.

        Args:
            model_path (PathLike): Path to the OpenVINO IR model or model name from Intel OMZ.
            model_type (str): Type of the model. Defaults to "Classification".
            async_inference (bool): Whether to use asynchronous inference. Defaults to True.
            max_num_requests (int | None): Maximum number of inference requests. Defaults to None.
            use_throughput_mode (bool): Whether to use throughput mode. Defaults to True.
            model_api_configuration (dict[str, Any] | None): Configuration for the model API. Defaults to None.
            metric (MetricCallable): Metric callable for evaluation. Defaults to MultiLabelClsMetricCallable.
            **kwargs: Additional keyword arguments.
        """
        model_api_configuration = model_api_configuration if model_api_configuration else {}
        model_api_configuration.update({"multilabel": True, "confidence_threshold": 0.0})
        super().__init__(
            model_path=model_path,
            model_type=model_type,
            async_inference=async_inference,
            max_num_requests=max_num_requests,
            use_throughput_mode=use_throughput_mode,
            model_api_configuration=model_api_configuration,
            metric=metric,
        )
        self._task = OTXTaskType.MULTI_LABEL_CLS

    def _customize_outputs(
        self,
        outputs: list[ClassificationResult],
        inputs: OTXDataBatch,
    ) -> OTXPredBatch:
        """Customize the outputs of the model for OTX compatibility.

        Args:
            outputs (list[ClassificationResult]): List of classification results from the model.
            inputs (OTXDataBatch): Input batch containing images and metadata.

        Returns:
            OTXPredBatch: Customized prediction batch containing scores, saliency maps, and feature vectors.
        """
        pred_scores = [torch.tensor([top_label.confidence for top_label in out.top_labels]) for out in outputs]

        if outputs and outputs[0].saliency_map.size != 0:
            # Squeeze dim 4D => 3D, (1, num_classes, H, W) => (num_classes, H, W)
            predicted_s_maps = [out.saliency_map[0] for out in outputs]

            # Squeeze dim 2D => 1D, (1, internal_dim) => (internal_dim)
            predicted_f_vectors = [out.feature_vector[0] for out in outputs]
            return OTXPredBatch(
                batch_size=len(outputs),
                images=inputs.images,
                imgs_info=inputs.imgs_info,
                scores=pred_scores,
                labels=[],
                saliency_map=predicted_s_maps,
                feature_vector=predicted_f_vectors,
            )

        return OTXPredBatch(
            batch_size=len(outputs),
            images=inputs.images,
            imgs_info=inputs.imgs_info,
            scores=pred_scores,
            labels=[],
        )

    def prepare_metric_inputs(
        self,
        preds: OTXPredBatch,
        inputs: OTXDataBatch,
    ) -> MetricInput:
        """Prepare inputs for metric computation.

        Converts prediction and input entities to a format suitable for metric evaluation.

        Args:
            preds (OTXPredBatch): The predicted batch entity containing predicted labels and scores.
            inputs (OTXDataBatch): The input batch entity containing ground truth labels.

        Returns:
            MetricInput: A dictionary containing 'preds' and 'target' keys
            corresponding to the predicted and target labels for metric evaluation.
        """
        return {
            "preds": torch.stack(preds.scores),
            "target": torch.stack(inputs.labels),
        }
