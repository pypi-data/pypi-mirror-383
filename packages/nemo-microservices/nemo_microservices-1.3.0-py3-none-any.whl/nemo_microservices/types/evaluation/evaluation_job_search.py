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

from ..shared import ownership
from ..._models import BaseModel
from ..evaluation_config import EvaluationConfig
from ..evaluation_target import EvaluationTarget
from ..shared.date_range import DateRange
from ..shared.job_status import JobStatus
from ..evaluation_status_details import EvaluationStatusDetails

__all__ = ["EvaluationJobSearch", "Config", "Ownership", "StatusDetails", "Target"]

Config: TypeAlias = Union[EvaluationConfig, List[EvaluationConfig]]

Ownership: TypeAlias = Union[ownership.Ownership, List[ownership.Ownership]]

StatusDetails: TypeAlias = Union[EvaluationStatusDetails, List[EvaluationStatusDetails]]

Target: TypeAlias = Union[EvaluationTarget, List[EvaluationTarget]]


class EvaluationJobSearch(BaseModel):
    config: Optional[Config] = None
    """An evaluation configuration."""

    created_at: Optional[DateRange] = None

    custom_fields: Union[Dict[str, object], List[Dict[str, object]], None] = None

    description: Union[str, List[str], None] = None

    namespace: Union[str, List[str], None] = None

    output_files_url: Union[str, List[str], None] = None

    ownership: Optional[Ownership] = None
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: Union[str, List[str], None] = None

    result: Union[str, List[str], None] = None

    status: Union[JobStatus, List[JobStatus], None] = None
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

    status_details: Optional[StatusDetails] = None
    """Details about the status of the evaluation."""

    target: Optional[Target] = None
    """An entity representing the target of the evaluation."""

    updated_at: Optional[DateRange] = None
