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

from typing import List, Optional

from ..._models import BaseModel
from .output_rails_streaming_config import OutputRailsStreamingConfig

__all__ = ["OutputRails"]


class OutputRails(BaseModel):
    apply_to_reasoning_traces: Optional[bool] = None
    """
    If True, output rails will apply guardrails to both reasoning traces and output
    response. If False, output rails will only apply guardrails to the output
    response excluding the reasoning traces, thus keeping reasoning traces
    unaltered.
    """

    flows: Optional[List[str]] = None
    """The names of all the flows that implement output rails."""

    parallel: Optional[bool] = None
    """If True, the output rails are executed in parallel."""

    streaming: Optional[OutputRailsStreamingConfig] = None
    """Configuration for managing streaming output of LLM tokens."""
