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

from typing import Union
from typing_extensions import Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["EmbeddingCreateParams"]


class EmbeddingCreateParams(TypedDict, total=False):
    input: Required[Union[str, SequenceNotStr[str]]]
    """Input text to embed, encoded as a string or array of tokens."""

    model: Required[str]
    """The model to use. Must be one of the available models."""

    dimensions: int
    """The dimensionality of the embedding vector."""

    encoding_format: str
    """The encoding format of the input."""

    input_type: str
    """The type of the input."""

    truncate: str
    """Truncate the input text."""

    user: str
    """Not Supported. A unique identifier representing your end-user."""
