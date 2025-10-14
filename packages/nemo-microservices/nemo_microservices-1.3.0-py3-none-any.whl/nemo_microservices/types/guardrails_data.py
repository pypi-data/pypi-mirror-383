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

from typing import Dict, List, Optional

from .._models import BaseModel
from .generation_log import GenerationLog

__all__ = ["GuardrailsData"]


class GuardrailsData(BaseModel):
    config_ids: Optional[List[str]] = None
    """The list of configuration ids that were used."""

    llm_output: Optional[Dict[str, object]] = None
    """Contains any additional output coming from the LLM."""

    log: Optional[GenerationLog] = None
    """Contains additional logging information associated with a generation call."""

    output_data: Optional[Dict[str, object]] = None
    """The output data, i.e.

    a dict with the values corresponding to the `output_vars`.
    """
