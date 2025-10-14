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

from ...._models import BaseModel
from .safe_synthesizer_parameters import SafeSynthesizerParameters

__all__ = ["SafeSynthesizerJobConfig"]


class SafeSynthesizerJobConfig(BaseModel):
    config: SafeSynthesizerParameters
    """Main configuration class for the Safe Synthesizer pipeline.

    This is the top-level configuration class that orchestrates all aspects of
    synthetic data generation including training, generation, privacy, evaluation,
    and data handling. It provides validation to ensure parameter compatibility.

    Attributes: data: Data parameters. replace_pii: PII replacement parameters.
    training: Training parameters. generation: Generation parameters. privacy:
    Privacy parameters. evaluation: Evaluation parameters. enable_synthesis: Enable
    synthesizing new data by training a model. enable_replace_pii: Enable replacing
    PII in the data.
    """

    data_source: str
