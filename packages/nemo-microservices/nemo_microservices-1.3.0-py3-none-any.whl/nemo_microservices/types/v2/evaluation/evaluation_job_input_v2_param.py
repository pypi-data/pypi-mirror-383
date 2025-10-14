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

from typing import Union
from typing_extensions import Required, TypeAlias, TypedDict

from .evaluation_config_v2_param import EvaluationConfigV2Param
from .evaluation_target_v2_param import EvaluationTargetV2Param

__all__ = ["EvaluationJobInputV2Param", "Config", "Target"]

Config: TypeAlias = Union[str, EvaluationConfigV2Param]

Target: TypeAlias = Union[str, EvaluationTargetV2Param]


class EvaluationJobInputV2Param(TypedDict, total=False):
    config: Required[Config]
    """The evaluation configuration."""

    target: Required[Target]
    """The evaluation target."""
