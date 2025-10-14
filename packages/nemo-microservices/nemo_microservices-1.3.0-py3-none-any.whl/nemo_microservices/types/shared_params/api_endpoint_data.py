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

from ..shared.api_endpoint_format import APIEndpointFormat

__all__ = ["APIEndpointData"]


class APIEndpointData(TypedDict, total=False):
    model_id: Required[str]
    """The id of the model. How this is used depends on the API endpoint format."""

    url: Required[str]
    """The API endpoint URL."""

    api_key: str
    """The API key that should be used to access the endpoint."""

    format: APIEndpointFormat
    """API endpoint format.

    The format dictates the structure of the request and response.

    ## Values

    - `"nim"` - NVIDIA NIM format
    - `"openai"` - OpenAI format
    - `"lama_stack"` - Llama Stack format
    """
