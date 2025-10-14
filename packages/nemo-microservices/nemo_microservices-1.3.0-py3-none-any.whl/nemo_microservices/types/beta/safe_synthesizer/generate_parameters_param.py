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

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["GenerateParametersParam"]


class GenerateParametersParam(TypedDict, total=False):
    guided_decoding_backend: str
    """The backend used for guided decoding when use_structured_generation=True.

    Supported backends (from vllm) are 'outlines', 'guidance', 'xgrammar', and
    'auto'.
    """

    invalid_fraction_threshold: float
    """
    The fraction of invalid records that will stop generation after the `patience`
    limit is reached.
    """

    num_records: int
    """Number of records to generate."""

    patience: int
    """
    Number of consecutive generations where the `invalid_fraction_threshold` is
    reached before stopping generation.
    """

    repetition_penalty: float
    """The value used to control the likelihood of the model repeating the same token."""

    temperature: float
    """Sampling temperature."""

    top_p: float
    """Nucleus sampling probability."""

    use_structured_generation: bool
    """Use structured generation."""
