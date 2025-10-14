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

from typing_extensions import Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["ProviderUpdateParams"]


class ProviderUpdateParams(TypedDict, total=False):
    namespace: Required[str]

    host_url: Required[str]
    """The network endpoint URL for the model provider"""

    api_key: str
    """The API key value itself.

    Will be stored in Secrets service. Mutually exclusive with api_key_id.
    """

    api_key_id: str
    """Reference to the API key stored in Secrets service.

    Mutually exclusive with api_key.
    """

    description: str
    """Optional description of the model provider"""

    enabled_models: SequenceNotStr[str]
    """Optional list of specific models to enable from this provider"""
