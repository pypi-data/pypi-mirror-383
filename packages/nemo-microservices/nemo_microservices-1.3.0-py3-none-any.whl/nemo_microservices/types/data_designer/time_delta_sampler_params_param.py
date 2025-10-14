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

from typing_extensions import Literal, Required, TypedDict

__all__ = ["TimeDeltaSamplerParamsParam"]


class TimeDeltaSamplerParamsParam(TypedDict, total=False):
    dt_max: Required[int]
    """Maximum possible time-delta for sampling range, exclusive.

    Must be greater than `dt_min`.
    """

    dt_min: Required[int]
    """Minimum possible time-delta for sampling range, inclusive.

    Must be less than `dt_max`.
    """

    reference_column_name: Required[str]
    """Name of an existing datetime column to condition time-delta sampling on."""

    unit: Literal["D", "h", "m", "s"]
    """Sampling units, e.g. the smallest possible time interval between samples."""
