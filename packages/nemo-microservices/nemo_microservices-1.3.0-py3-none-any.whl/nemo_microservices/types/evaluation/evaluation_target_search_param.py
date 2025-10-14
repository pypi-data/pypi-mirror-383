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

from typing import Dict, List, Union, Iterable
from typing_extensions import TypeAlias, TypedDict

from ..._types import SequenceNotStr
from ..target_type import TargetType
from ..shared_params import ownership
from ..rag_target_param import RagTargetParam
from ..retriever_target_param import RetrieverTargetParam
from ..shared_params.date_range import DateRange
from ..cached_outputs_data_param import CachedOutputsDataParam

__all__ = ["EvaluationTargetSearchParam", "CachedOutputs", "Ownership", "Rag", "Retriever"]

CachedOutputs: TypeAlias = Union[CachedOutputsDataParam, Iterable[CachedOutputsDataParam]]

Ownership: TypeAlias = Union[ownership.Ownership, Iterable[ownership.Ownership]]

Rag: TypeAlias = Union[RagTargetParam, Iterable[RagTargetParam]]

Retriever: TypeAlias = Union[RetrieverTargetParam, Iterable[RetrieverTargetParam]]


class EvaluationTargetSearchParam(TypedDict, total=False):
    cached_outputs: CachedOutputs
    """An evaluation target which contains cached outputs."""

    created_at: DateRange

    custom_fields: Union[Dict[str, object], Iterable[Dict[str, object]]]

    dataset: Union[str, SequenceNotStr[str]]

    description: Union[str, SequenceNotStr[str]]

    model: Union[str, SequenceNotStr[str]]

    name: Union[str, SequenceNotStr[str]]

    namespace: Union[str, SequenceNotStr[str]]

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: Union[str, SequenceNotStr[str]]

    rag: Rag

    retriever: Retriever

    rows: Union[Iterable[Dict[str, object]], Iterable[Iterable[Dict[str, object]]]]

    type: Union[TargetType, List[TargetType]]

    updated_at: DateRange
