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

from .base import NSSBaseModel

__all__ = ["SafeSynthesizerTiming", "SafeSynthesizerSummary"]


class SafeSynthesizerTiming(NSSBaseModel):
    """
    Output object for Safe Synthesizer
    """

    total_time_sec: float | None = None
    pii_replacer_time_sec: float | None = None
    training_time_sec: float | None = None
    generation_time_sec: float | None = None
    evaluation_time_sec: float | None = None


class SafeSynthesizerSummary(NSSBaseModel):
    """
    Output object for Safe Synthesizer
    """

    synthetic_data_quality_score: float | None = None
    column_correlation_stability_score: float | None = None
    deep_structure_stability_score: float | None = None
    column_distribution_stability_score: float | None = None
    text_semantic_similarity_score: float | None = None
    text_structure_similarity_score: float | None = None

    data_privacy_score: float | None = None
    membership_inference_protection_score: float | None = None
    attribute_inference_protection_score: float | None = None

    num_valid_records: int | None = None
    num_invalid_records: int | None = None
    num_prompts: int | None = None
    valid_record_fraction: float | None = None

    timing: SafeSynthesizerTiming
