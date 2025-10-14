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
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .task_config_param import TaskConfigParam
from .group_config_param import GroupConfigParam
from .evaluation_params_param import EvaluationParamsParam
from .shared_params.ownership import Ownership

__all__ = ["EvaluationConfigParam"]


class EvaluationConfigParam(TypedDict, total=False):
    type: Required[str]
    """
    The type of the evaluation, e.g., 'mmlu', 'big_code'.For custom evaluations,
    this is set to `custom`.
    """

    id: str
    """The ID of the entity.

    With the exception of namespaces, this is always a semantically-prefixed
    base58-encoded uuid4 [<prefix>-base58(uuid4())].
    """

    created_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Timestamp for when the entity was created."""

    custom_fields: Dict[str, object]
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    groups: Dict[str, GroupConfigParam]
    """Evaluation tasks belonging to the evaluation."""

    name: str
    """The name of the entity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: str
    """The namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    params: EvaluationParamsParam
    """Global parameters for an evaluation."""

    project: str
    """The URN of the project associated with this entity."""

    schema_version: str
    """The version of the schema for the object. Internal use only."""

    tasks: Dict[str, TaskConfigParam]
    """Evaluation tasks belonging to the evaluation."""

    type_prefix: str

    updated_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Timestamp for when the entity was last updated."""
