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

from typing import Dict, List, Union, Optional
from typing_extensions import TypeAlias

from .model_v2 import ModelV2
from ...._models import BaseModel
from ...dataset_ev import DatasetEv
from ...rag_target import RagTarget
from ...target_type import TargetType
from ...retriever_target import RetrieverTarget
from ...cached_outputs_data import CachedOutputsData

__all__ = ["EvaluationTargetV2", "Dataset", "Model"]

Dataset: TypeAlias = Union[str, DatasetEv]

Model: TypeAlias = Union[str, ModelV2]


class EvaluationTargetV2(BaseModel):
    type: TargetType
    """The type of the evaluation target, e.g., 'model', 'retriever', 'rag'."""

    cached_outputs: Optional[CachedOutputsData] = None
    """An evaluation target which contains cached outputs."""

    dataset: Optional[Dataset] = None
    """Dataset to be evaluated."""

    model: Optional[Model] = None
    """The model to be evaluated."""

    rag: Optional[RagTarget] = None
    """RAG to be evaluated."""

    retriever: Optional[RetrieverTarget] = None
    """Retriever to be evaluated."""

    rows: Optional[List[Dict[str, object]]] = None
    """Rows to be evaluated."""
