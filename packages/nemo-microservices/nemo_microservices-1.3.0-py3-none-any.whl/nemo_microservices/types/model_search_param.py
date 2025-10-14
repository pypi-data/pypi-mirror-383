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

from typing import Dict, Union, Iterable
from typing_extensions import TypeAlias, TypedDict

from .._types import SequenceNotStr
from .shared_params import ownership
from .shared_params.date_range import DateRange
from .shared_params.model_spec import ModelSpec
from .shared_params.prompt_data import PromptData
from .shared_params.model_artifact import ModelArtifact
from .shared_params.guardrail_config import GuardrailConfig
from .shared_params.api_endpoint_data import APIEndpointData
from .shared_params.parameter_efficient_finetuning_data import ParameterEfficientFinetuningData

__all__ = ["ModelSearchParam", "APIEndpoint", "Artifact", "Guardrails", "Ownership", "Peft", "Prompt", "Spec"]

APIEndpoint: TypeAlias = Union[APIEndpointData, Iterable[APIEndpointData]]

Artifact: TypeAlias = Union[ModelArtifact, Iterable[ModelArtifact]]

Guardrails: TypeAlias = Union[GuardrailConfig, Iterable[GuardrailConfig]]

Ownership: TypeAlias = Union[ownership.Ownership, Iterable[ownership.Ownership]]

Peft: TypeAlias = Union[ParameterEfficientFinetuningData, Iterable[ParameterEfficientFinetuningData]]

Prompt: TypeAlias = Union[PromptData, Iterable[PromptData]]

Spec: TypeAlias = Union[ModelSpec, Iterable[ModelSpec]]


class ModelSearchParam(TypedDict, total=False):
    api_endpoint: APIEndpoint
    """Data about an API endpoint."""

    artifact: Artifact
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

    base_model: Union[str, SequenceNotStr[str]]

    created_at: DateRange

    custom_fields: Union[Dict[str, object], Iterable[Dict[str, object]]]

    description: Union[str, SequenceNotStr[str]]

    guardrails: Guardrails
    """A guardrail configuration"""

    name: Union[str, SequenceNotStr[str]]

    namespace: Union[str, SequenceNotStr[str]]

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    peft: Peft
    """Data about a parameter-efficient finetuning."""

    project: Union[str, SequenceNotStr[str]]

    prompt: Prompt
    """Prompt engineering data."""

    spec: Spec
    """Detailed specification about a model."""

    updated_at: DateRange
