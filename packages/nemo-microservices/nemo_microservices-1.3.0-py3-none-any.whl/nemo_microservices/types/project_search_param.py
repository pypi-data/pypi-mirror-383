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

from typing import Dict, Union, Iterable
from typing_extensions import TypeAlias, TypedDict

from .._types import SequenceNotStr
from .shared_params import ownership
from .shared_params.date_range import DateRange

__all__ = ["ProjectSearchParam", "Ownership"]

Ownership: TypeAlias = Union[ownership.Ownership, Iterable[ownership.Ownership]]


class ProjectSearchParam(TypedDict, total=False):
    created_at: DateRange

    custom_fields: Union[Dict[str, object], Iterable[Dict[str, object]]]

    description: Union[str, SequenceNotStr[str]]

    name: Union[str, SequenceNotStr[str]]

    namespace: Union[str, SequenceNotStr[str]]

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: Union[str, SequenceNotStr[str]]

    updated_at: DateRange
