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

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Union

import yaml
from pydantic import Field

from .analysis.column_profilers import ColumnProfilerConfigT
from .base import ConfigBase
from .columns import ColumnConfigT
from .models import ModelConfig
from .sampler_constraints import ColumnConstraintT
from .seed import SeedConfig


class DataDesignerConfig(ConfigBase):
    """Configuration for NeMo Data Designer.

    This class defines the main configuration structure for NeMo Data Designer,
    which orchestrates the generation of synthetic data.

    Attributes:
        columns: Required list of column configurations defining how each column
            should be generated. Must contain at least one column.
        model_configs: Optional list of model configurations for LLM-based generation.
            Each model config defines the model, provider, and inference parameters.
        seed_config: Optional seed dataset settings to use for generation.
        constraints: Optional list of column constraints.
        profilers: Optional list of column profilers for analyzing generated data characteristics.
    """

    columns: list[ColumnConfigT] = Field(min_length=1)
    model_configs: Optional[list[ModelConfig]] = None
    seed_config: Optional[SeedConfig] = None
    constraints: Optional[list[ColumnConstraintT]] = None
    profilers: Optional[list[ColumnProfilerConfigT]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the Data Designer config to a dictionary.

        Returns:
            A dictionary representation of the configuration using JSON-compatible
            serialization.
        """
        return self.model_dump(mode="json")

    def to_yaml(self, path: Optional[Union[str, Path]] = None, *, indent: Optional[int] = 2, **kwargs) -> Optional[str]:
        """Convert the Data Designer config to a YAML string or file.

        Args:
            path: Optional file path to write the YAML to. If None, returns the
                YAML string instead of writing to file.
            indent: Number of spaces for YAML indentation. Defaults to 2.
            **kwargs: Additional keyword arguments passed to yaml.dump().

        Returns:
            The YAML string if path is None, otherwise None (file is written).
        """
        yaml_str = yaml.dump(self.to_dict(), indent=indent, **kwargs)
        if path is None:
            return yaml_str
        with open(path, "w") as f:
            f.write(yaml_str)

    def to_json(self, path: Optional[Union[str, Path]] = None, *, indent: Optional[int] = 2, **kwargs) -> Optional[str]:
        """Convert the Data Designer config to a JSON string or file.

        Args:
            path: Optional file path to write the JSON to. If None, returns the
                JSON string instead of writing to file.
            indent: Number of spaces for JSON indentation. Defaults to 2.
            **kwargs: Additional keyword arguments passed to json.dumps().

        Returns:
            The JSON string if path is None, otherwise None (file is written).
        """
        json_str = json.dumps(self.to_dict(), indent=indent, **kwargs)
        if path is None:
            return json_str
        with open(path, "w") as f:
            f.write(json_str)
