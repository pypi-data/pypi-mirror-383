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

from typing import Dict, List, Optional

from ..._models import BaseModel
from .compute_resources import ComputeResources
from .kubernetes_logging_sidecar import KubernetesLoggingSidecar
from .kubernetes_object_metadata import KubernetesObjectMetadata
from .kubernetes_job_storage_config import KubernetesJobStorageConfig
from .kubernetes_job_image_pull_secret import KubernetesJobImagePullSecret

__all__ = ["KubernetesJobExecutionProfileConfig"]


class KubernetesJobExecutionProfileConfig(BaseModel):
    storage: KubernetesJobStorageConfig
    """Configuration for persistent storage in Kubernetes jobs."""

    active_deadline_seconds: Optional[int] = None

    affinity: Optional[Dict[str, object]] = None

    image_pull_secrets: Optional[List[KubernetesJobImagePullSecret]] = None

    job_metadata: Optional[KubernetesObjectMetadata] = None

    logging: Optional[KubernetesLoggingSidecar] = None
    """Configuration for Kubernetes Logging Sidecar"""

    namespace: Optional[str] = None

    node_selector: Optional[Dict[str, str]] = None

    num_gpus: Optional[int] = None

    pod_metadata: Optional[KubernetesObjectMetadata] = None

    resources: Optional[ComputeResources] = None
    """Resource requirements matching k8s ResourceRequirements format."""

    tolerations: Optional[List[Dict[str, object]]] = None

    ttl_seconds_after_finished: Optional[int] = None
