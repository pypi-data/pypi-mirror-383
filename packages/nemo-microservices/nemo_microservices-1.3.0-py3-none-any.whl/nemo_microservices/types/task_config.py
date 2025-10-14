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

from typing import Dict, Union, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel
from .dataset_ev import DatasetEv
from .metric_config import MetricConfig

__all__ = ["TaskConfig", "Dataset"]

Dataset: TypeAlias = Union[str, DatasetEv]


class TaskConfig(BaseModel):
    type: str
    """The type of the task."""

    dataset: Optional[Dataset] = None
    """
    Optional dataset reference.Typically, if not specified, means that the type of
    task has an implicit dataset.
    """

    metrics: Optional[Dict[str, MetricConfig]] = None
    """Metrics to be computed for the task."""

    params: Optional[Dict[str, object]] = None
    """Additional parameters related to the task."""
