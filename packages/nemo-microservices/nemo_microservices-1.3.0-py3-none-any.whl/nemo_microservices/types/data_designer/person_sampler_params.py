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

from typing import List, Union, Optional

from ..._models import BaseModel

__all__ = ["PersonSamplerParams"]


class PersonSamplerParams(BaseModel):
    age_range: Optional[List[int]] = None
    """If specified, then only synthetic people within this age range will be sampled."""

    city: Union[str, List[str], None] = None
    """If specified, then only synthetic people from these cities will be sampled."""

    locale: Optional[str] = None
    """
    Locale string, determines the language and geographic locale that a synthetic
    person will be sampled from. E.g, en_US, en_GB, fr_FR, ...
    """

    sex: Optional[str] = None
    """If specified, then only synthetic people of the specified sex will be sampled."""

    state: Union[str, List[str], None] = None
    """Only supported for 'en_US' locale.

    If specified, then only synthetic people from these states will be sampled.
    States must be given as two-letter abbreviations.
    """

    with_synthetic_personas: Optional[bool] = None
    """If True, then append synthetic persona columns to each generated person."""
