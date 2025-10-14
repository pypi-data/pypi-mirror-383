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

from typing import Union
from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["RowParam"]


class RowParam(TypedDict, total=False):
    condition: str
    """Row condition match."""

    description: str
    """Rule description for human consumption."""

    entity: Union[str, SequenceNotStr[str]]
    """Row entity match."""

    fallback_value: str
    """Row fallback value."""

    foreach: str
    """Foreach expression."""

    name: Union[str, SequenceNotStr[str]]
    """Row name."""

    type: Union[str, SequenceNotStr[str]]
    """Row type match."""

    value: str
    """Row value definition."""
