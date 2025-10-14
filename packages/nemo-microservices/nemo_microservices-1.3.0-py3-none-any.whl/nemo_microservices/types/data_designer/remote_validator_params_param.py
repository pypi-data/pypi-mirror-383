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

from typing import Dict
from typing_extensions import Required, TypedDict

__all__ = ["RemoteValidatorParamsParam"]


class RemoteValidatorParamsParam(TypedDict, total=False):
    endpoint_url: Required[str]
    """The URL of the remote endpoint"""

    max_parallel_requests: int
    """The maximum number of parallel requests to make"""

    max_retries: int
    """The maximum number of retry attempts"""

    output_schema: Dict[str, object]
    """Expected schema for remote endpoint's output"""

    retry_backoff: float
    """The backoff factor for the retry delay"""

    timeout: float
    """The timeout for the HTTP request"""
