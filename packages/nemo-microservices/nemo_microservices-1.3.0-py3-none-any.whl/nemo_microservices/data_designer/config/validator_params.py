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

from enum import Enum
from typing import Any, Optional, Union

from pydantic import Field, model_validator
from typing_extensions import Self, TypeAlias

from .base import ConfigBase
from .utils.code_lang import SQL_DIALECTS, CodeLang

SUPPORTED_CODE_LANGUAGES = {CodeLang.PYTHON, *SQL_DIALECTS}


class ValidatorType(str, Enum):
    CODE = "code"
    REMOTE = "remote"


class CodeValidatorParams(ConfigBase):
    code_lang: CodeLang = Field(description="The language of the code to validate")

    @model_validator(mode="after")
    def validate_code_lang(self) -> Self:
        if self.code_lang not in SUPPORTED_CODE_LANGUAGES:
            raise ValueError(
                f"Unsupported code language, supported languages are: {[lang.value for lang in SUPPORTED_CODE_LANGUAGES]}"
            )
        return self


class RemoteValidatorParams(ConfigBase):
    endpoint_url: str = Field(description="The URL of the remote endpoint")
    output_schema: Optional[dict[str, Any]] = Field(
        default=None, description="Expected schema for remote endpoint's output"
    )
    timeout: float = Field(default=30.0, gt=0, description="The timeout for the HTTP request")
    max_retries: int = Field(default=3, ge=0, description="The maximum number of retry attempts")
    retry_backoff: float = Field(default=2.0, gt=1, description="The backoff factor for the retry delay")
    max_parallel_requests: int = Field(default=4, ge=1, description="The maximum number of parallel requests to make")


ValidatorParamsT: TypeAlias = Union[
    CodeValidatorParams,
    RemoteValidatorParams,
]
