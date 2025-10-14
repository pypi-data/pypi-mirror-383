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

from typing import Union, Iterable
from typing_extensions import Required, TypedDict

from ..._types import SequenceNotStr

__all__ = ["CategorySamplerParamsParam"]


class CategorySamplerParamsParam(TypedDict, total=False):
    values: Required[SequenceNotStr[Union[str, float]]]
    """List of possible categorical values that can be sampled from."""

    weights: Iterable[float]
    """List of unnormalized probability weights to assigned to each value, in order.

    Larger values will be sampled with higher probability.
    """
