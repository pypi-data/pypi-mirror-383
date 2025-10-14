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

from .shared import ownership
from .._models import BaseModel
from .shared.date_range import DateRange

__all__ = ["DatasetSearch", "Ownership"]

Ownership: TypeAlias = Union[ownership.Ownership, List[ownership.Ownership]]


class DatasetSearch(BaseModel):
    created_at: Optional[DateRange] = None

    custom_fields: Union[Dict[str, object], List[Dict[str, object]], None] = None

    description: Union[str, List[str], None] = None

    files_url: Union[str, List[str], None] = None

    format: Union[str, List[str], None] = None

    hf_endpoint: Union[str, List[str], None] = None

    limit: Union[int, List[int], None] = None

    name: Union[str, List[str], None] = None

    namespace: Union[str, List[str], None] = None

    ownership: Optional[Ownership] = None
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: Union[str, List[str], None] = None

    split: Union[str, List[str], None] = None

    updated_at: Optional[DateRange] = None
