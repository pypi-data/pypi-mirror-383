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
from typing_extensions import Required, TypeAlias, TypedDict

from ..._types import SequenceNotStr
from .validator_type import ValidatorType
from .code_validator_params_param import CodeValidatorParamsParam
from .remote_validator_params_param import RemoteValidatorParamsParam

__all__ = ["ValidationColumnConfigParam", "ValidatorParams"]

ValidatorParams: TypeAlias = Union[CodeValidatorParamsParam, RemoteValidatorParamsParam]


class ValidationColumnConfigParam(TypedDict, total=False):
    name: Required[str]

    target_columns: Required[SequenceNotStr[str]]

    validator_params: Required[ValidatorParams]

    validator_type: Required[ValidatorType]

    batch_size: int
    """Number of records to process in each batch"""

    drop: bool
