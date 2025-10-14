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

from typing import Dict, Optional
from datetime import datetime

from ..._models import BaseModel
from .platform_job_status import PlatformJobStatus

__all__ = ["PlatformJobTask"]


class PlatformJobTask(BaseModel):
    id: str

    step_id: str

    created_at: Optional[datetime] = None

    error_details: Optional[Dict[str, object]] = None
    """Details about the job step errors."""

    error_stack: Optional[str] = None

    namespace: Optional[str] = None
    """The namespace of the entity."""

    project: Optional[str] = None
    """The URN of the project associated with this entity."""

    status: Optional[PlatformJobStatus] = None
    """Enumeration of possible job statuses.

    This enum represents the various states a job can be in during its lifecycle,
    from creation to a terminal state.
    """

    status_details: Optional[Dict[str, object]] = None
    """Details about the job step status."""

    updated_at: Optional[datetime] = None
