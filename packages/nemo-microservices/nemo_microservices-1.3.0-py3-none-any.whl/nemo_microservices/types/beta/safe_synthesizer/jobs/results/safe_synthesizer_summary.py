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

from typing import Optional

from ......_models import BaseModel
from .safe_synthesizer_timing import SafeSynthesizerTiming

__all__ = ["SafeSynthesizerSummary"]


class SafeSynthesizerSummary(BaseModel):
    timing: SafeSynthesizerTiming
    """Output object for Safe Synthesizer"""

    attribute_inference_protection_score: Optional[float] = None

    column_correlation_stability_score: Optional[float] = None

    column_distribution_stability_score: Optional[float] = None

    data_privacy_score: Optional[float] = None

    deep_structure_stability_score: Optional[float] = None

    membership_inference_protection_score: Optional[float] = None

    num_invalid_records: Optional[int] = None

    num_prompts: Optional[int] = None

    num_valid_records: Optional[int] = None

    synthetic_data_quality_score: Optional[float] = None

    text_semantic_similarity_score: Optional[float] = None

    text_structure_similarity_score: Optional[float] = None

    valid_record_fraction: Optional[float] = None
