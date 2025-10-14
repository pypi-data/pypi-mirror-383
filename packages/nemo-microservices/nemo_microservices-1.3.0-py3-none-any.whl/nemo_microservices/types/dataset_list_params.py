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

from .dataset_sort_field import DatasetSortField
from .dataset_filter_param import DatasetFilterParam
from .dataset_search_param import DatasetSearchParam

__all__ = ["DatasetListParams"]


class DatasetListParams(TypedDict, total=False):
    filter: DatasetFilterParam
    """Filter configs on various criteria."""

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    search: DatasetSearchParam
    """Search datasets using substring matching.

    You can combine multiple search fields and filters.

    For example:

    - `?search[name]=imagenet`: searches all datasets with 'imagenet' in the name.
    - `?search[format]=csv`: searches all datasets with 'csv' in the format.
    - `?search[split]=train`: searches all datasets with 'train' in the split.
    - `?search[namespace]=research`: searches all datasets with 'research' in the
      namespace.
    - `?search[name]=imagenet&search[split]=validation`: searches all datasets with
      'imagenet' in the name AND 'validation' in the split.
    - `?search[name]=imagenet&search[name]=coco`: searches all datasets with
      'imagenet' OR 'coco' in the name.
    - `?search[updated_at][start]=2024-01-01T00:00:00` finds all datasets updated on
      or after the start date
    - `?search[created_at][start]=2022-01-01&search[updated_at][end]=2024-01-01`
      finds all datasets created from start date up to and including end date
    """

    sort: DatasetSortField
    """The field to sort by.

    To sort in decreasing order, use `-` in front of the field name.
    """
