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

from ...._models import BaseModel
from .ner_config import NERConfig
from .classify_config import ClassifyConfig

__all__ = ["Globals"]


class Globals(BaseModel):
    classify: Optional[ClassifyConfig] = None
    """Column classification configuration"""

    locales: Optional[List[str]] = None
    """list of locales."""

    lock_columns: Optional[List[str]] = None
    """List of columns to preserve as immutable across all transformations."""

    ner: Optional[NERConfig] = None
    """Named Entity Recognition configuration"""

    seed: Optional[int] = None
    """Optional random seed."""
