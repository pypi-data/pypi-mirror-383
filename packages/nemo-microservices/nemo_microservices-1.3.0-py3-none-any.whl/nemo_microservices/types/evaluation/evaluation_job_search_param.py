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

from typing import Dict, List, Union, Iterable
from typing_extensions import TypeAlias, TypedDict

from ..._types import SequenceNotStr
from ..shared_params import ownership
from ..shared.job_status import JobStatus
from ..evaluation_config_param import EvaluationConfigParam
from ..evaluation_target_param import EvaluationTargetParam
from ..shared_params.date_range import DateRange
from ..evaluation_status_details_param import EvaluationStatusDetailsParam

__all__ = ["EvaluationJobSearchParam", "Config", "Ownership", "StatusDetails", "Target"]

Config: TypeAlias = Union[EvaluationConfigParam, Iterable[EvaluationConfigParam]]

Ownership: TypeAlias = Union[ownership.Ownership, Iterable[ownership.Ownership]]

StatusDetails: TypeAlias = Union[EvaluationStatusDetailsParam, Iterable[EvaluationStatusDetailsParam]]

Target: TypeAlias = Union[EvaluationTargetParam, Iterable[EvaluationTargetParam]]


class EvaluationJobSearchParam(TypedDict, total=False):
    config: Config
    """An evaluation configuration."""

    created_at: DateRange

    custom_fields: Union[Dict[str, object], Iterable[Dict[str, object]]]

    description: Union[str, SequenceNotStr[str]]

    namespace: Union[str, SequenceNotStr[str]]

    output_files_url: Union[str, SequenceNotStr[str]]

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: Union[str, SequenceNotStr[str]]

    result: Union[str, SequenceNotStr[str]]

    status: Union[JobStatus, List[JobStatus]]
    """Normalized statuses for all jobs.

    - **CREATED**: The job is created, but not yet scheduled.
    - **PENDING**: The job is waiting for resource allocation.
    - **RUNNING**: The job is currently running.
    - **CANCELLING**: The job is being cancelled at the user's request.
    - **CANCELLED**: The job has been cancelled by the user.
    - **CANCELLING**: The job is being cancelled at the user's request.
    - **FAILED**: The job failed to execute and terminated.
    - **COMPLETED**: The job has completed successfully.
    - **READY**: The job is ready to be used.
    - **UNKNOWN**: The job status is unknown.
    """

    status_details: StatusDetails
    """Details about the status of the evaluation."""

    target: Target
    """An entity representing the target of the evaluation."""

    updated_at: DateRange
