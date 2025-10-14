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

from typing import Union, Iterable
from typing_extensions import Required, TypeAlias, TypedDict

from .seed_config_param import SeedConfigParam
from .model_config_param import ModelConfigParam
from .sampler_column_config_param import SamplerColumnConfigParam
from .llm_code_column_config_param import LlmCodeColumnConfigParam
from .llm_text_column_config_param import LlmTextColumnConfigParam
from .llm_judge_column_config_param import LlmJudgeColumnConfigParam
from .expression_column_config_param import ExpressionColumnConfigParam
from .validation_column_config_param import ValidationColumnConfigParam
from .seed_dataset_column_config_param import SeedDatasetColumnConfigParam
from .judge_score_profiler_config_param import JudgeScoreProfilerConfigParam
from .column_inequality_constraint_param import ColumnInequalityConstraintParam
from .llm_structured_column_config_param import LlmStructuredColumnConfigParam
from .scalar_inequality_constraint_param import ScalarInequalityConstraintParam

__all__ = ["DataDesignerConfigParam", "Column", "Constraint"]

Column: TypeAlias = Union[
    ExpressionColumnConfigParam,
    LlmCodeColumnConfigParam,
    LlmJudgeColumnConfigParam,
    LlmStructuredColumnConfigParam,
    LlmTextColumnConfigParam,
    SamplerColumnConfigParam,
    SeedDatasetColumnConfigParam,
    ValidationColumnConfigParam,
]

Constraint: TypeAlias = Union[ScalarInequalityConstraintParam, ColumnInequalityConstraintParam]


class DataDesignerConfigParam(TypedDict, total=False):
    columns: Required[Iterable[Column]]

    constraints: Iterable[Constraint]

    model_configs: Iterable[ModelConfigParam]

    profilers: Iterable[JudgeScoreProfilerConfigParam]

    seed_config: SeedConfigParam
