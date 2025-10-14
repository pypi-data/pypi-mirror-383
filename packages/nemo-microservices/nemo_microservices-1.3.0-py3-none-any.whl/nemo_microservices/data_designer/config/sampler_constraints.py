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

from abc import ABC, abstractmethod
from enum import Enum
from typing import Union

from typing_extensions import TypeAlias

from .base import ConfigBase


class ConstraintType(str, Enum):
    SCALAR_INEQUALITY = "scalar_inequality"
    COLUMN_INEQUALITY = "column_inequality"


class InequalityOperator(str, Enum):
    LT = "lt"
    LE = "le"
    GT = "gt"
    GE = "ge"


class Constraint(ConfigBase, ABC):
    target_column: str

    @property
    @abstractmethod
    def constraint_type(self) -> ConstraintType: ...


class ScalarInequalityConstraint(Constraint):
    rhs: float
    operator: InequalityOperator

    @property
    def constraint_type(self) -> ConstraintType:
        return ConstraintType.SCALAR_INEQUALITY


class ColumnInequalityConstraint(Constraint):
    rhs: str
    operator: InequalityOperator

    @property
    def constraint_type(self) -> ConstraintType:
        return ConstraintType.COLUMN_INEQUALITY


ColumnConstraintT: TypeAlias = Union[ScalarInequalityConstraint, ColumnInequalityConstraint]
