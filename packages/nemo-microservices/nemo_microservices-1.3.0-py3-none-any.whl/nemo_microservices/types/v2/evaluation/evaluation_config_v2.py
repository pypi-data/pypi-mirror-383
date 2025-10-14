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

from typing import Dict, Optional

from ...._models import BaseModel
from ...task_config import TaskConfig
from ...group_config import GroupConfig
from ...evaluation_params import EvaluationParams

__all__ = ["EvaluationConfigV2"]


class EvaluationConfigV2(BaseModel):
    type: str
    """
    The type of the evaluation, e.g., 'mmlu', 'big_code'.For custom evaluations,
    this is set to `custom`.
    """

    groups: Optional[Dict[str, GroupConfig]] = None
    """Evaluation groups belonging to the evaluation."""

    params: Optional[EvaluationParams] = None
    """Global parameters for an evaluation."""

    tasks: Optional[Dict[str, TaskConfig]] = None
    """Evaluation tasks belonging to the evaluation."""
