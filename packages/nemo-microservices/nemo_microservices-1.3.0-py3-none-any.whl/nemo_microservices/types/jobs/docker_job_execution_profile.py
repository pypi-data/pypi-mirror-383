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

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .docker_job_execution_profile_config import DockerJobExecutionProfileConfig

__all__ = ["DockerJobExecutionProfile"]


class DockerJobExecutionProfile(BaseModel):
    config: DockerJobExecutionProfileConfig
    """Additional configuration for the docker executor"""

    backend: Optional[Literal["docker"]] = None

    profile: Optional[str] = None
    """The profile name for the executor, e.g., high_priority_a100, low_priority, etc."""

    provider: Optional[str] = None
    """The compute provider for the executor, e.g., cpu, gpu"""
