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
from .tool_schema import ToolSchema

__all__ = ["DatasetParameters"]


class DatasetParameters(BaseModel):
    in_batch_negatives: Optional[bool] = None
    """
    In-batch negatives treats every other example in a training batch as a negative
    sample during contrastive learning. When enabled, the model learns to
    distinguish the correct positive pair not just from explicitly provided hard
    negatives, but from all other examples in the same batch. This can improve
    training without adding extra labeled negative data.
    """

    negative_sample_strategy: Optional[str] = None
    """
    How to select negatives when more are available than needed - Embedding Only.
    'first' picks the first N; 'random' samples N negatives randomly.
    """

    num_hard_negatives: Optional[int] = None
    """Number of negative documents to include per query for contrastive training.

    - Embedding Only
    """

    tools: Optional[List[ToolSchema]] = None
    """A list of tools that are available for training with tool calling"""
