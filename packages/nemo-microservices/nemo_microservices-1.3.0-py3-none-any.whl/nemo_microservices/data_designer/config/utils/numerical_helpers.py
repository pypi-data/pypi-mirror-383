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

import numbers
from numbers import Number
from typing import Any, Type

from .constants import REPORTING_PRECISION


def is_int(val: Any) -> bool:
    return isinstance(val, numbers.Integral)


def is_float(val: Any) -> bool:
    return isinstance(val, numbers.Real) and not isinstance(val, numbers.Integral)


def prepare_number_for_reporting(
    value: Number,
    target_type: Type[Number],
    precision: int = REPORTING_PRECISION,
) -> Number:
    """Ensure native python types and round to `precision` decimal digits."""
    value = target_type(value)
    if is_float(value):
        return round(value, precision)
    return value
