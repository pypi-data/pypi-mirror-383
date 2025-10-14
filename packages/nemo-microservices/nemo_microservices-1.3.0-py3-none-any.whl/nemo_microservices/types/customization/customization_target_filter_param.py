# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ..target_status import TargetStatus

__all__ = ["CustomizationTargetFilterParam"]


class CustomizationTargetFilterParam(TypedDict, total=False):
    base_model: str
    """Filter by name of the base model."""

    enabled: bool
    """Filter by enabled state of models"""

    name: str
    """Filter by the name of the customization target"""

    namespace: str
    """The namespace of the customization target"""

    status: TargetStatus
    """Normalized statuses for targets.

    - **CREATED**: The target is created, but not yet scheduled.
    - **PENDING**: The target is waiting for resource allocation.
    - **DOWNLOADING**: The target is downloading.
    - **FAILED**: The target failed to execute and terminated.
    - **READY**: The target is ready to be used.
    - **CANCELLED**: The target download was cancelled.
    - **UNKNOWN**: The target status is unknown.
    - **DELETED**: The target is deleted.
    - **DELETING**: The target is currently being deleted.
    - **DELETE_FAILED**: Failed to delete the target.
    """
