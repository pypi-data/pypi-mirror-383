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

from typing import List, Union, Optional
from typing_extensions import TypeAlias

from ..._compat import PYDANTIC_V1, ConfigDict
from ..._models import BaseModel
from .seed_config import SeedConfig
from .model_config import ModelConfig
from .sampler_column_config import SamplerColumnConfig
from .llm_code_column_config import LlmCodeColumnConfig
from .llm_text_column_config import LlmTextColumnConfig
from .llm_judge_column_config import LlmJudgeColumnConfig
from .expression_column_config import ExpressionColumnConfig
from .validation_column_config import ValidationColumnConfig
from .seed_dataset_column_config import SeedDatasetColumnConfig
from .judge_score_profiler_config import JudgeScoreProfilerConfig
from .column_inequality_constraint import ColumnInequalityConstraint
from .llm_structured_column_config import LlmStructuredColumnConfig
from .scalar_inequality_constraint import ScalarInequalityConstraint

__all__ = ["DataDesignerConfig", "Column", "Constraint"]

Column: TypeAlias = Union[
    ExpressionColumnConfig,
    LlmCodeColumnConfig,
    LlmJudgeColumnConfig,
    LlmStructuredColumnConfig,
    LlmTextColumnConfig,
    SamplerColumnConfig,
    SeedDatasetColumnConfig,
    ValidationColumnConfig,
]

Constraint: TypeAlias = Union[ScalarInequalityConstraint, ColumnInequalityConstraint]


class DataDesignerConfig(BaseModel):
    columns: List[Column]

    constraints: Optional[List[Constraint]] = None

    model_configs: Optional[List[ModelConfig]] = None

    profilers: Optional[List[JudgeScoreProfilerConfig]] = None

    seed_config: Optional[SeedConfig] = None

    if not PYDANTIC_V1:
        # allow fields with a `model_` prefix
        model_config = ConfigDict(protected_namespaces=tuple())
