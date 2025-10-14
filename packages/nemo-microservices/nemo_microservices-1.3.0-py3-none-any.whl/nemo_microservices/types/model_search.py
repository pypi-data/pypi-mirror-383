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

from typing import Dict, List, Union, Optional
from typing_extensions import TypeAlias

from .shared import ownership
from .._models import BaseModel
from .shared.date_range import DateRange
from .shared.model_spec import ModelSpec
from .shared.prompt_data import PromptData
from .shared.model_artifact import ModelArtifact
from .shared.guardrail_config import GuardrailConfig
from .shared.api_endpoint_data import APIEndpointData
from .shared.parameter_efficient_finetuning_data import ParameterEfficientFinetuningData

__all__ = ["ModelSearch", "APIEndpoint", "Artifact", "Guardrails", "Ownership", "Peft", "Prompt", "Spec"]

APIEndpoint: TypeAlias = Union[APIEndpointData, List[APIEndpointData]]

Artifact: TypeAlias = Union[ModelArtifact, List[ModelArtifact]]

Guardrails: TypeAlias = Union[GuardrailConfig, List[GuardrailConfig]]

Ownership: TypeAlias = Union[ownership.Ownership, List[ownership.Ownership]]

Peft: TypeAlias = Union[ParameterEfficientFinetuningData, List[ParameterEfficientFinetuningData]]

Prompt: TypeAlias = Union[PromptData, List[PromptData]]

Spec: TypeAlias = Union[ModelSpec, List[ModelSpec]]


class ModelSearch(BaseModel):
    api_endpoint: Optional[APIEndpoint] = None
    """Data about an API endpoint."""

    artifact: Optional[Artifact] = None
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

    base_model: Union[str, List[str], None] = None

    created_at: Optional[DateRange] = None

    custom_fields: Union[Dict[str, object], List[Dict[str, object]], None] = None

    description: Union[str, List[str], None] = None

    guardrails: Optional[Guardrails] = None
    """A guardrail configuration"""

    name: Union[str, List[str], None] = None

    namespace: Union[str, List[str], None] = None

    ownership: Optional[Ownership] = None
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    peft: Optional[Peft] = None
    """Data about a parameter-efficient finetuning."""

    project: Union[str, List[str], None] = None

    prompt: Optional[Prompt] = None
    """Prompt engineering data."""

    spec: Optional[Spec] = None
    """Detailed specification about a model."""

    updated_at: Optional[DateRange] = None
