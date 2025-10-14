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

from typing import Dict, Union
from typing_extensions import TypedDict

from .model_spec_de_param import ModelSpecDeParam
from .prompt_data_de_param import PromptDataDeParam
from .model_artifact_de_param import ModelArtifactDeParam
from .shared_params.ownership import Ownership
from .guardrail_config_de_param import GuardrailConfigDeParam
from .shared_params.api_endpoint_data import APIEndpointData
from .parameter_efficient_finetuning_data_de_param import ParameterEfficientFinetuningDataDeParam

__all__ = ["ModelDeParam"]


class ModelDeParam(TypedDict, total=False):
    api_endpoint: APIEndpointData
    """Data about an API endpoint."""

    artifact: ModelArtifactDeParam
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

    base_model: Union[str, Dict[str, object]]
    """Link to another model which is used as a base for the current model.

    Used in conjunction with `peft`, `prompt` and `guardrails`.
    """

    custom_fields: Dict[str, object]
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    guardrails: GuardrailConfigDeParam
    """A guardrail configuration"""

    name: str
    """The name of the identity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: str
    """The if of the namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    peft: ParameterEfficientFinetuningDataDeParam
    """Data about a parameter-efficient finetuning."""

    project: str
    """The id of project associated with this entity."""

    prompt: PromptDataDeParam
    """Prompt engineering data."""

    spec: ModelSpecDeParam
    """Detailed spec about a model."""
