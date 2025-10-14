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

import builtins
from typing import Dict, List, Optional

from ..._models import BaseModel
from .job_event import JobEvent

__all__ = ["JobEntry"]


class JobEntry(BaseModel):
    events: Optional[List[JobEvent]] = None
    """The events that occurred"""

    logs: Optional[Dict[str, object]] = None
    """The logs from any pods that existed"""

    object: Optional[str] = None
    """The object where the informaiton is being pulled"""

    status: Optional[Dict[str, builtins.object]] = None
    """The status of the pod"""
