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

from typing import Union, Optional
from typing_extensions import TypeAlias

from ..._models import BaseModel
from .manual_distribution import ManualDistribution
from .uniform_distribution import UniformDistribution

__all__ = ["InferenceParameters", "Temperature", "TopP"]

Temperature: TypeAlias = Union[float, UniformDistribution, ManualDistribution, None]

TopP: TypeAlias = Union[float, UniformDistribution, ManualDistribution, None]


class InferenceParameters(BaseModel):
    max_parallel_requests: Optional[int] = None

    max_tokens: Optional[int] = None

    temperature: Optional[Temperature] = None

    timeout: Optional[int] = None

    top_p: Optional[TopP] = None
