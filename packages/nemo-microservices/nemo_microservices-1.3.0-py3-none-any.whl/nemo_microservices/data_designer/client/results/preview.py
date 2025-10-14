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

import logging
from enum import Enum
from typing import Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict

from ...config.config_builder import DataDesignerConfigBuilder
from ...config.utils.visualization import display_sample_record
from .errors import DataDesignerPreviewError

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    ANALYSIS = "analysis"
    DATASET = "dataset"
    HEARTBEAT = "heartbeat"
    LOG = "log"


class PreviewMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    message: str
    message_type: MessageType
    extra: Optional[dict[str, str]] = None


class PreviewResults:
    def __init__(
        self,
        *,
        config_builder: DataDesignerConfigBuilder,
        dataset: Optional[pd.DataFrame] = None,
        analysis: Optional[dict] = None,
    ):
        """Creates a new instance with results from a Data Designer preview run.

        Args:
            config_builder: Data Designer configuration builder.
            dataset: Dataset of the preview run.
            analysis: Analysis of the preview run.
        """
        self.config_builder = config_builder
        self.dataset = dataset
        self.analysis = analysis
        self._display_cycle_index = 0

    def display_sample_record(
        self,
        index: Optional[int] = None,
        *,
        hide_seed_columns: bool = False,
        syntax_highlighting_theme: str = "dracula",
        background_color: Optional[str] = None,
    ) -> None:
        """Display a sample record from the Data Designer dataset preview.

        Args:
            index: Index of the record to display. If None, the next record will be displayed.
                This is useful for running the cell in a notebook multiple times.
            hide_seed_columns: If True, the columns from the seed dataset (if any) will not be displayed.
            syntax_highlighting_theme: Theme to use for syntax highlighting. See the `Syntax`
                documentation from `rich` for information about available themes.
            background_color: Background color to use for the record. See the `Syntax`
                documentation from `rich` for information about available background colors.
        """
        if self.dataset is None:
            raise DataDesignerPreviewError("No dataset found in the preview results.")
        i = index or self._display_cycle_index
        display_sample_record(
            record=self.dataset.iloc[i],
            config_builder=self.config_builder,
            background_color=background_color,
            syntax_highlighting_theme=syntax_highlighting_theme,
            hide_seed_columns=hide_seed_columns,
            record_index=i,
        )
        if index is None:
            self._display_cycle_index = (self._display_cycle_index + 1) % len(self.dataset)
