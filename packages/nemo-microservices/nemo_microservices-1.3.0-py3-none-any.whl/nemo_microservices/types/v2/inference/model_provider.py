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
from datetime import datetime

from ...._models import BaseModel
from .model_provider_status import ModelProviderStatus

__all__ = ["ModelProvider"]


class ModelProvider(BaseModel):
    host_url: str
    """The network endpoint URL for the model provider"""

    name: str
    """Name of the entity. Name/namespace combo must be unique across all entities."""

    id: Optional[str] = None
    """Unique identifier for the model provider"""

    api_key_id: Optional[str] = None
    """Reference to the API key stored in Secrets service"""

    created_at: Optional[datetime] = None

    description: Optional[str] = None
    """Optional description of the model provider"""

    enabled_models: Optional[List[str]] = None
    """Optional list of specific models to enable from this provider.

    If not set, all discovered models are enabled.
    """

    models: Optional[List[str]] = None
    """List of Model Entity namespace/name resource names that this provider serves"""

    namespace: Optional[str] = None
    """The namespace of the entity."""

    project: Optional[str] = None
    """The URN of the project associated with this entity."""

    status: Optional[ModelProviderStatus] = None
    """Status enum for ModelProvider objects."""

    status_message: Optional[str] = None
    """Detailed status message, populated by models service"""

    updated_at: Optional[datetime] = None
