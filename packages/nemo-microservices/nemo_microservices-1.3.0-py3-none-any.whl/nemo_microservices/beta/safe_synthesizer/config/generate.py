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

from typing import (
    Annotated,
)

from pydantic import (
    BaseModel,
    Field,
)

from ..configurator.parameters import (
    Parameters,
)
from ..configurator.validators import (
    ValueValidator,
    range_validator,
)

__all__ = ["GenerateParameters"]


class GenerateParameters(Parameters, BaseModel):
    """Configuration parameters for synthetic data generation.

    These parameters control how synthetic data is generated after the model is trained.
    They affect the quality, diversity, and validity of the generated synthetic records.

    Attributes:
        num_records: Number of synthetic records to generate. Maximum is 130,000 records.
        temperature: Sampling temperature for controlling randomness (higher = more random).
        repetition_penalty: Penalty for token repetition (≥1.0, higher = less repetition).
        top_p: Nucleus sampling probability for token selection (0 < value ≤ 1).
        patience: Number of invalid records fraction before stopping.
        invalid_fraction_threshold: "The fraction of invalid records that will stop generation after the `patience` limit is reached."
        use_structured_generation: Whether to use structured generation for better format control.

    """

    num_records: Annotated[
        int,
        Field(
            title="num_records",
            description=("Number of records to generate."),
        ),
    ] = 1000

    temperature: Annotated[
        float,
        Field(
            title="temperature",
            description="Sampling temperature.",
        ),
    ] = 0.9

    repetition_penalty: Annotated[
        float,
        ValueValidator(value_func=lambda v: v > 0),
        Field(
            title="repetition_penalty",
            description="The value used to control the likelihood of the model repeating the same token.",
        ),
    ] = 1.0

    top_p: Annotated[
        float,
        ValueValidator(value_func=lambda v: 0 < v <= 1),
        Field(
            title="top_p",
            description="Nucleus sampling probability.",
        ),
    ] = 1.0

    patience: Annotated[
        int,
        ValueValidator(value_func=lambda v: v >= 1),
        Field(
            title="patience",
            description=(
                "Number of consecutive generations where the `invalid_fraction_threshold` "
                "is reached before stopping generation."
            ),
        ),
    ] = 3

    invalid_fraction_threshold: Annotated[
        float,
        ValueValidator(lambda p: range_validator(p, lambda v: 0 <= v <= 1)),
        Field(
            title="invalid_fraction_threshold",
            description=(
                "The fraction of invalid records that will stop generation after the `patience` limit is reached."
            ),
        ),
    ] = 0.8

    use_structured_generation: Annotated[
        bool,
        Field(
            title="use_structured_generation",
            description="Use structured generation.",
        ),
    ] = False

    guided_decoding_backend: Annotated[
        str,
        Field(
            title="guided_decoding_backend",
            description=(
                "The backend used for guided decoding when use_structured_generation=True. "
                "Supported backends (from vllm) are 'outlines', 'guidance', 'xgrammar', and 'auto'."
            ),
        ),
    ] = "outlines"
