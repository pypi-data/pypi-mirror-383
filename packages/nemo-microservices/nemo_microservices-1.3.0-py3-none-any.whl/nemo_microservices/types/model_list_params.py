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

from typing_extensions import TypedDict

from .model_sort_field import ModelSortField
from .model_filter_param import ModelFilterParam
from .model_search_param import ModelSearchParam

__all__ = ["ModelListParams"]


class ModelListParams(TypedDict, total=False):
    filter: ModelFilterParam
    """Filter models on various criteria.

    Where it makes sense, you can also filter on the existence of a property. For
    example:

    - `?filter[peft]=true`: would filter all models with `peft` attribute set.
    """

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    search: ModelSearchParam
    """Search models using substring matching.

    You can combine multiple search fields and filters.

    For example:

    - `?search[name]=llama`: searches all models with 'llama' in the name.
    - `?search[base_model]=mistral`: searches all models with 'mistral' in the
      base_model.
    - `?search[peft]=lora`: searches all models with 'lora' in the peft field.
    - `?search[custom_property][item]=adapter`: searches all models where the
      custom_property's item contains 'adapter'.
    - `?search[name]=llama&search[peft]=lora`: searches all models with 'llama' in
      the name AND 'lora' in the peft field.
    - `?search[name]=llama&search[name]=gpt`: searches all models with 'llama' OR
      'gpt' in the name.
    - `?search[updated_at][start]=2024-01-01T00:00:00` finds all models updated on
      or after the start date
    - `?search[created_at][start]=2022-01-01&search[updated_at][end]=2024-01-01`
      finds all models created from start date up to and including end date
    """

    sort: ModelSortField
    """The field to sort by.

    To sort in decreasing order, use `-` in front of the field name.
    """
