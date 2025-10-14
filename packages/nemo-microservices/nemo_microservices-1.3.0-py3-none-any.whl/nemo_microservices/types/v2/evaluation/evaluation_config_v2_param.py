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

from typing import Dict
from typing_extensions import Required, TypedDict

from ...task_config_param import TaskConfigParam
from ...group_config_param import GroupConfigParam
from ...evaluation_params_param import EvaluationParamsParam

__all__ = ["EvaluationConfigV2Param"]


class EvaluationConfigV2Param(TypedDict, total=False):
    type: Required[str]
    """
    The type of the evaluation, e.g., 'mmlu', 'big_code'.For custom evaluations,
    this is set to `custom`.
    """

    groups: Dict[str, GroupConfigParam]
    """Evaluation groups belonging to the evaluation."""

    params: EvaluationParamsParam
    """Global parameters for an evaluation."""

    tasks: Dict[str, TaskConfigParam]
    """Evaluation tasks belonging to the evaluation."""
