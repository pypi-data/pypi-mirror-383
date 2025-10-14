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

from ..shared import ownership
from ..._models import BaseModel
from ..rag_target import RagTarget
from ..target_type import TargetType
from ..retriever_target import RetrieverTarget
from ..shared.date_range import DateRange
from ..cached_outputs_data import CachedOutputsData

__all__ = ["EvaluationTargetSearch", "CachedOutputs", "Ownership", "Rag", "Retriever"]

CachedOutputs: TypeAlias = Union[CachedOutputsData, List[CachedOutputsData]]

Ownership: TypeAlias = Union[ownership.Ownership, List[ownership.Ownership]]

Rag: TypeAlias = Union[RagTarget, List[RagTarget]]

Retriever: TypeAlias = Union[RetrieverTarget, List[RetrieverTarget]]


class EvaluationTargetSearch(BaseModel):
    cached_outputs: Optional[CachedOutputs] = None
    """An evaluation target which contains cached outputs."""

    created_at: Optional[DateRange] = None

    custom_fields: Union[Dict[str, object], List[Dict[str, object]], None] = None

    dataset: Union[str, List[str], None] = None

    description: Union[str, List[str], None] = None

    model: Union[str, List[str], None] = None

    name: Union[str, List[str], None] = None

    namespace: Union[str, List[str], None] = None

    ownership: Optional[Ownership] = None
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: Union[str, List[str], None] = None

    rag: Optional[Rag] = None

    retriever: Optional[Retriever] = None

    rows: Union[List[Dict[str, object]], List[List[Dict[str, object]]], None] = None

    type: Union[TargetType, List[TargetType], None] = None

    updated_at: Optional[DateRange] = None
