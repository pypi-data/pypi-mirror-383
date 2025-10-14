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

import builtins
from typing import List, Optional

from ..._models import BaseModel
from ..shared.pagination_data import PaginationData
from ..shared.guardrail_config import GuardrailConfig

__all__ = ["GuardrailConfigsPage"]


class GuardrailConfigsPage(BaseModel):
    data: List[GuardrailConfig]

    filter: Optional[object] = None
    """Filtering information."""

    object: Optional[str] = None

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    search: Optional[builtins.object] = None
    """Search information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
