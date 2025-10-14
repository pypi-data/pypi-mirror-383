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

from typing import Iterable
from typing_extensions import Required, TypedDict

from .code_lang import CodeLang
from .image_context_param import ImageContextParam

__all__ = ["LlmCodeColumnConfigParam"]


class LlmCodeColumnConfigParam(TypedDict, total=False):
    code_lang: Required[CodeLang]

    model_alias: Required[str]

    name: Required[str]

    prompt: Required[str]

    drop: bool

    multi_modal_context: Iterable[ImageContextParam]

    system_prompt: str
