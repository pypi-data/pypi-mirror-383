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

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict

__all__ = ["NSSBaseModel", "LRScheduler", "pydantic_model_config"]

pydantic_model_config = ConfigDict(
    arbitrary_types_allowed=True,
    validation_error_cause=True,
    from_attributes=True,
    validate_default=True,
    protected_namespaces=(),
)


class NSSBaseModel(BaseModel):
    """
    Base model for all NeMo Safe Synthesizer configuration and result models that do not use Parameters.
    """

    model_config = pydantic_model_config

    def dict(self) -> dict[str, Any]:
        return self.model_dump()


class LRScheduler(str, Enum):
    COSINE = "cosine"
    LINEAR = "linear"
    COSINE_WITH_RESTARTS = "cosine_with_restarts"
    POLYNOMIAL = "polynomial"
    CONSTANT = "constant"
    CONSTANT_WITH_WARMUP = "constant_with_warmup"
