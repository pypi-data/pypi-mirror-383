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

from typing import List, Optional

from ..._models import BaseModel
from .image_spec import ImageSpec

__all__ = ["KubernetesLoggingSidecar"]


class KubernetesLoggingSidecar(BaseModel):
    command: Optional[List[str]] = None
    """Command to run for logging sidecar"""

    config_mount_path: Optional[str] = None
    """
    Path inside the container where the logging sidecar configuration file is
    mounted
    """

    config_volume_name: Optional[str] = None
    """Name of the volume that contains the logging sidecar configuration"""

    configmap: Optional[str] = None
    """Name of the ConfigMap containing the logging sidecar configuration"""

    configmap_key: Optional[str] = None
    """Key in the ConfigMap that contains the logging sidecar configuration file"""

    health_check_path: Optional[str] = None
    """Path for logging sidecar health check"""

    health_check_port: Optional[int] = None
    """Port for logging sidecar health check"""

    image: Optional[ImageSpec] = None
