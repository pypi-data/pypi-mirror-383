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

from typing import Dict, Union, Optional

from ...._models import BaseModel
from ...shared.model_spec import ModelSpec
from ...shared.prompt_data import PromptData
from ...shared.model_artifact import ModelArtifact
from ...shared.guardrail_config import GuardrailConfig
from ...shared.api_endpoint_data import APIEndpointData
from ...shared.parameter_efficient_finetuning_data import ParameterEfficientFinetuningData

__all__ = ["ModelV2"]


class ModelV2(BaseModel):
    api_endpoint: Optional[APIEndpointData] = None
    """Data about an API endpoint."""

    artifact: Optional[ModelArtifact] = None
    """
    Data about a model artifact (a set of checkpoint files, configs, and other
    auxiliary info).

    The `files_url` field can point to a DataStore location.

    Example:

    - nds://models/rdinu/my-lora-customization

    The `rdinu/my-lora-customization` part above is the actual repository.

    If a specific revision needs to be referred, the HuggingFace syntax is used.

    - nds://models/rdinu/my-lora-customization@v1
    - nds://models/rdinu/my-lora-customization@8df79a8
    """

    base_model: Union[str, Dict[str, object], None] = None
    """Link to another model which is used as a base for the current model."""

    guardrails: Optional[GuardrailConfig] = None
    """A guardrail configuration"""

    peft: Optional[ParameterEfficientFinetuningData] = None
    """Data about a parameter-efficient finetuning."""

    prompt: Optional[PromptData] = None
    """Prompt engineering data."""

    spec: Optional[ModelSpec] = None
    """Detailed specification about a model."""
