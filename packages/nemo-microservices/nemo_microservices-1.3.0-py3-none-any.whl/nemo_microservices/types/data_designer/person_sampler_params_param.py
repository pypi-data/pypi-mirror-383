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
from typing_extensions import TypedDict

from ..._types import SequenceNotStr

__all__ = ["PersonSamplerParamsParam"]


class PersonSamplerParamsParam(TypedDict, total=False):
    age_range: Iterable[int]
    """If specified, then only synthetic people within this age range will be sampled."""

    city: Union[str, SequenceNotStr[str]]
    """If specified, then only synthetic people from these cities will be sampled."""

    locale: str
    """
    Locale string, determines the language and geographic locale that a synthetic
    person will be sampled from. E.g, en_US, en_GB, fr_FR, ...
    """

    sex: str
    """If specified, then only synthetic people of the specified sex will be sampled."""

    state: Union[str, SequenceNotStr[str]]
    """Only supported for 'en_US' locale.

    If specified, then only synthetic people from these states will be sampled.
    States must be given as two-letter abbreviations.
    """

    with_synthetic_personas: bool
    """If True, then append synthetic persona columns to each generated person."""
