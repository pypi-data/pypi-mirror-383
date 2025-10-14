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

from typing import List, Optional

from ..._models import BaseModel
from ..evaluation_target import EvaluationTarget
from ..shared.pagination_data import PaginationData
from .evaluation_target_search import EvaluationTargetSearch
from ..evaluation_target_filter import EvaluationTargetFilter

__all__ = ["EvaluationTargetsPage"]


class EvaluationTargetsPage(BaseModel):
    data: List[EvaluationTarget]

    filter: Optional[EvaluationTargetFilter] = None
    """Filtering information."""

    object: Optional[str] = None

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    search: Optional[EvaluationTargetSearch] = None
    """Search information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
