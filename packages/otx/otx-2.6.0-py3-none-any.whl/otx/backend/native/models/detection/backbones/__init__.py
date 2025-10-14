# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Custom backbone implementations for detection task."""

from .csp_darknet import CSPDarknet
from .cspnext import CSPNeXt
from .presnet import PResNet

__all__ = ["CSPDarknet", "PResNet", "CSPNeXt"]
