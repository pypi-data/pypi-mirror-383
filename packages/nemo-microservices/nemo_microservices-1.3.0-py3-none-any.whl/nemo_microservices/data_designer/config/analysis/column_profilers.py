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

from abc import ABC
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field
from rich.panel import Panel
from rich.table import Column, Table
from typing_extensions import TypeAlias

from ..base import ConfigBase
from ..utils.visualization import ColorPalette
from .column_statistics import (
    CategoricalDistribution,
    CategoricalHistogramData,
    ColumnDistributionType,
    MissingValue,
    NumericalDistribution,
)
from .utils.reporting import TITLE_STYLE, create_judge_score_summary_table


class ColumnProfilerType(str, Enum):
    JUDGE_SCORE = "judge-score"


class ColumnProfilerResults(BaseModel, ABC):
    def create_report_section(self) -> Panel:
        return Panel(
            f"Report section generation not implemented for '{self.__class__.__name__}'.",
            title="Not Implemented",
            border_style=f"bold {ColorPalette.YELLOW.value}",
            padding=(1, 2),
        )


class JudgeScoreProfilerConfig(ConfigBase):
    model_alias: str
    summary_score_sample_size: Optional[int] = Field(default=20, ge=1)


class JudgeScoreSample(BaseModel):
    score: Union[int, str]
    reasoning: str


class JudgeScoreDistributions(BaseModel):
    scores: dict[str, list[Union[int, str]]]
    reasoning: dict[str, list[str]]
    distribution_types: dict[str, ColumnDistributionType]
    distributions: dict[str, Union[CategoricalDistribution, NumericalDistribution, MissingValue]]
    histograms: dict[str, Union[CategoricalHistogramData, MissingValue]]


class JudgeScoreSummary(BaseModel):
    score_name: str
    summary: str
    score_samples: list[JudgeScoreSample]


class JudgeScoreProfilerResults(ColumnProfilerResults):
    column_name: str
    summaries: dict[str, JudgeScoreSummary]
    score_distributions: JudgeScoreDistributions

    def create_report_section(self) -> Panel:
        layout = Table.grid(Column(), expand=True, padding=(2, 0))

        for score_name in self.summaries.keys():
            layout.add_row(
                create_judge_score_summary_table(
                    score_name=score_name,
                    histogram=self.score_distributions.histograms[score_name],
                    summary=self.summaries[score_name].summary,
                )
            )

        return Panel(
            layout,
            title=f"[{TITLE_STYLE}]LLM-as-a-Judge Score Profile: '{self.column_name}'[/{TITLE_STYLE}]",
            padding=(1, 2),
        )


ColumnProfilerConfigT: TypeAlias = JudgeScoreProfilerConfig

ColumnProfilerResultsT: TypeAlias = JudgeScoreProfilerResults
