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

from .namespace_filter_param import NamespaceFilterParam
from .namespace_search_param import NamespaceSearchParam
from .shared.generic_sort_field import GenericSortField

__all__ = ["NamespaceListParams"]


class NamespaceListParams(TypedDict, total=False):
    filter: NamespaceFilterParam
    """Filter namespaces on various criteria."""

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    search: NamespaceSearchParam
    """Search namespaces using substring matching.

    You can combine multiple search fields and filters.

    For example:

    - `?search[id]=research`: searches all namespaces with 'research' in the id.
    - `?search[name]=vision`: searches all namespaces with 'vision' in the name.
    - `?search[id]=research&search[name]=vision`: searches all namespaces with
      'research' in the id AND 'vision' in the name.
    - `?search[id]=research&search[id]=production`: searches all namespaces with
      'research' OR 'production' in the id.
    - `?search[updated_at][start]=2024-01-01T00:00:00` finds all namespaces updated
      on or after the start date
    - `?search[created_at][start]=2022-01-01&search[updated_at][end]=2024-01-01`
      finds all namespaces created from start date up to and including end date
    """

    sort: GenericSortField
    """The field to sort by.

    To sort in decreasing order, use `-` in front of the field name.
    """
