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

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .chat_completion_content_part_text_param import ChatCompletionContentPartTextParam
from .chat_completion_content_part_image_param import ChatCompletionContentPartImageParam

__all__ = ["ChatCompletionUserMessageParam", "ContentUnionMember1"]

ContentUnionMember1: TypeAlias = Union[ChatCompletionContentPartTextParam, ChatCompletionContentPartImageParam]


class ChatCompletionUserMessageParam(BaseModel):
    content: Union[str, List[ContentUnionMember1]]
    """The contents of the user message."""

    role: Literal["user"]
    """The role of the messages author, in this case `user`."""

    name: Optional[str] = None
    """An optional name for the participant."""
