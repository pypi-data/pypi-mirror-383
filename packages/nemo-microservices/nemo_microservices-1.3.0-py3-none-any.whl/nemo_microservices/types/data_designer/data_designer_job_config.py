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

from ..._models import BaseModel
from .data_designer_config import DataDesignerConfig

__all__ = ["DataDesignerJobConfig"]


class DataDesignerJobConfig(BaseModel):
    config: DataDesignerConfig
    """Configuration for NeMo Data Designer.

    This class defines the main configuration structure for NeMo Data Designer,
    which orchestrates the generation of synthetic data.

    Attributes: columns: Required list of column configurations defining how each
    column should be generated. Must contain at least one column. model_configs:
    Optional list of model configurations for LLM-based generation. Each model
    config defines the model, provider, and inference parameters. seed_config:
    Optional seed dataset settings to use for generation. constraints: Optional list
    of column constraints. profilers: Optional list of column profilers for
    analyzing generated data characteristics.
    """

    num_records: int
