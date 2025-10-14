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

from .project_sort_field import ProjectSortField
from .project_filter_param import ProjectFilterParam
from .project_search_param import ProjectSearchParam

__all__ = ["ProjectListParams"]


class ProjectListParams(TypedDict, total=False):
    filter: ProjectFilterParam
    """Filter projects on various criteria."""

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    search: ProjectSearchParam
    """Search projects using substring matching.

    You can combine multiple search fields and filters.

    For example:

    - `?search[name]=vision`: searches all projects with 'vision' in the name.
    - `?search[description]=classification`: searches all projects with
      'classification' in the description.
    - `?search[namespace]=research`: searches all projects with 'research' in the
      namespace.
    - `?search[name]=vision&search[namespace]=research`: searches all projects with
      'vision' in the name AND 'research' in the namespace.
    - `?search[name]=vision&search[name]=nlp`: searches all projects with 'vision'
      OR 'nlp' in the name.
    - `?search[updated_at][start]=2024-01-01T00:00:00` finds all projects updated on
      or after the start date
    - `?search[created_at][start]=2022-01-01&search[updated_at][end]=2024-01-01`
      finds all projects created from start date up to and including end date
    """

    sort: ProjectSortField
    """The field to sort by.

    To sort in decreasing order, use `-` in front of the field name.
    """
