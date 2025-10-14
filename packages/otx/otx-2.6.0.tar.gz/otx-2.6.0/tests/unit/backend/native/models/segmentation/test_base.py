# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
"""Unit tests for segmentation model entity."""

from __future__ import annotations

import pytest
import torch

from otx.backend.native.models.base import DataInputParams, DefaultOptimizerCallable, DefaultSchedulerCallable
from otx.backend.native.models.segmentation.base import OTXSegmentationModel
from otx.data.entity.base import OTXBatchLossEntity
from otx.data.entity.torch import OTXDataBatch, OTXPredBatch
from otx.metrics.dice import SegmCallable
from otx.types.label import SegLabelInfo


class TestOTXSegmentationModel:
    @pytest.fixture()
    def model(self, label_info, optimizer, scheduler, metric, torch_compile):
        return OTXSegmentationModel(
            label_info,
            DataInputParams((224, 224), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
            "segm_model",
            optimizer,
            scheduler,
            metric,
            torch_compile,
        )

    @pytest.fixture()
    def batch_data_entity(self):
        return OTXDataBatch(
            batch_size=2,
            images=torch.randn(2, 3, 224, 224),
            imgs_info=[],
            masks=[torch.randn(1, 224, 224), torch.randn(1, 224, 224)],
        )

    @pytest.fixture()
    def label_info(self):
        return SegLabelInfo(
            label_names=["Background", "label_0", "label_1"],
            label_groups=[["Background", "label_0", "label_1"]],
            label_ids=["0", "1", "2"],
        )

    @pytest.fixture()
    def optimizer(self):
        return DefaultOptimizerCallable

    @pytest.fixture()
    def scheduler(self):
        return DefaultSchedulerCallable

    @pytest.fixture()
    def metric(self):
        return SegmCallable

    @pytest.fixture()
    def torch_compile(self):
        return False

    def test_export_parameters(self, model):
        params = model._export_parameters
        assert params.model_type == "Segmentation"
        assert params.task_type == "segmentation"
        assert params.return_soft_prediction is True
        assert params.soft_threshold == 0.5
        assert params.blur_strength == -1

    @pytest.mark.parametrize(
        ("label_info", "expected_label_info"),
        [
            (
                SegLabelInfo(
                    label_names=["label1", "label2", "label3"],
                    label_groups=[["label1", "label2", "label3"]],
                    label_ids=["0", "1", "2"],
                ),
                SegLabelInfo(
                    label_names=["label1", "label2", "label3"],
                    label_groups=[["label1", "label2", "label3"]],
                    label_ids=["0", "1", "2"],
                ),
            ),
            (SegLabelInfo.from_num_classes(num_classes=5), SegLabelInfo.from_num_classes(num_classes=5)),
        ],
    )
    def test_dispatch_label_info(self, model, label_info, expected_label_info):
        result = model._dispatch_label_info(label_info)
        assert result == expected_label_info

    def test_init(self, model):
        assert model.num_classes == 3
        assert model.model_name == "segm_model"
        assert model.data_input_params.input_size == (224, 224)

    def test_customize_inputs(self, model, batch_data_entity):
        customized_inputs = model._customize_inputs(batch_data_entity)
        assert customized_inputs["inputs"].shape == (2, 3, 224, 224)
        assert customized_inputs["img_metas"] == []
        assert customized_inputs["masks"].shape == (2, 224, 224)

    def test_customize_outputs_training(self, model, batch_data_entity):
        outputs = {"loss": torch.tensor(0.5)}
        customized_outputs = model._customize_outputs(outputs, batch_data_entity)
        assert isinstance(customized_outputs, OTXBatchLossEntity)
        assert customized_outputs["loss"] == torch.tensor(0.5)

    def test_customize_outputs_predict(self, model, batch_data_entity):
        model.training = False
        outputs = torch.randn(2, 10, 224, 224)
        customized_outputs = model._customize_outputs(outputs, batch_data_entity)
        assert isinstance(customized_outputs, OTXPredBatch)
        assert len(customized_outputs.scores) == 0
        assert customized_outputs.images.shape == (2, 3, 224, 224)
        assert customized_outputs.imgs_info == []

    def test_dummy_input(self, model: OTXSegmentationModel):
        batch_size = 2
        batch = model.get_dummy_input(batch_size)
        assert batch.batch_size == batch_size
