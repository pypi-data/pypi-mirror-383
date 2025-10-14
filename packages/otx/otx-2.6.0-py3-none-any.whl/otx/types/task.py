# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""OTX task type definition."""

from __future__ import annotations

from enum import Enum


class OTXTaskType(str, Enum):
    """OTX task type definition."""

    # Anomaly Detection
    ANOMALY = "ANOMALY"
    # TODO(ashwinvaidya17): Remove rest after greenlight from backend.
    ANOMALY_CLASSIFICATION = "ANOMALY_CLASSIFICATION"
    ANOMALY_DETECTION = "ANOMALY_DETECTION"
    ANOMALY_SEGMENTATION = "ANOMALY_SEGMENTATION"

    # Classification
    MULTI_CLASS_CLS = "MULTI_CLASS_CLS"
    MULTI_LABEL_CLS = "MULTI_LABEL_CLS"
    H_LABEL_CLS = "H_LABEL_CLS"

    # Detection
    DETECTION = "DETECTION"
    ROTATED_DETECTION = "ROTATED_DETECTION"
    KEYPOINT_DETECTION = "KEYPOINT_DETECTION"

    # Segmentation
    INSTANCE_SEGMENTATION = "INSTANCE_SEGMENTATION"
    SEMANTIC_SEGMENTATION = "SEMANTIC_SEGMENTATION"
