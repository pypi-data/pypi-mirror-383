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

"""
parameter validation and collection utilities for Pydantic-based configuration systems.

This module provides validators for field dependencies, custom value validation, and abstract
base classes for organizing collections of parameters. It extends the basic parameter
functionality with sophisticated validation logic and YAML serialization support.

"""

from __future__ import annotations

import json
import typing
from abc import ABCMeta
from os import PathLike
from typing import Any, Generator, Iterable, Mapping, get_args

import yaml
from pydantic import (
    BaseModel,
)
from typing_extensions import Self

from ..config.base import (
    pydantic_model_config,
)
from ..logging_utils import get_logger
from .parameter import (
    DataT,
)

__all__ = ["Parameters"]

logger = get_logger(__name__)


class Parameters(BaseModel, metaclass=ABCMeta):
    """
    Abstract base class for organizing collections of configuration/api parameters.

    This class provides a structured way to define and manage groups of parameters
    and adds small utilities like iteration, parameter lookup, nested parameter group lookup, etc.

    Features:
        - Iteration over parameters and nested parameter groups
        - Parameter lookup by name
    """

    model_config = pydantic_model_config

    def _isparams(self):
        """
        Marker method for identifying Parameters subclasses. More like a protocol than anything.
        """
        return True

    @classmethod
    def __subclasshook__(cls, c):
        """
        Enable isinstance() checks for Parameters derived classes.

        This allows checking if a class behaves like Parameters by looking for
        the _isparams marker method, enabling duck typing.
        """
        if cls is Parameters:
            mro = c.__mro__
            for B in mro:
                if "_isparams" in B.__dict__:
                    if B.__dict__["_isparams"] is None:
                        return NotImplemented
                    break
            else:
                return NotImplemented
            return True
        return NotImplemented

    def _iter_subparamgroups(self) -> "Generator[Self, None, None]":
        """
        Iterate over nested Parameters instances within this collection.

        Yields:
            Parameters instances that are attributes of this object
        """
        only_params_ = [(x, info) for x, info in self.model_fields.items()]

        for field in only_params_:
            name = field[0]
            info = field[1]
            anno = getattr(info, "annotation", None)
            anno_type = type(anno)
            if getattr(anno_type, "__origin__", None) is typing.Union:
                args = get_args(anno)
                for arg in args:
                    for subtype in get_args(arg):
                        if isinstance(subtype, type) and issubclass(subtype, Parameters):
                            yield getattr(self, name)

            elif isinstance(anno, type) and issubclass(anno, Parameters):
                yield getattr(self, name)

            elif isinstance(getattr(self, name), Parameters):
                yield getattr(self, name)
            else:
                pass

    def _iter_parameters(self, recursive: bool = True) -> Generator[Mapping[str, DataT | Parameters], None, None]:
        """
        Iterate over all Parameter instances in this collection.

        Args:
            recursive: If True, also iterate over parameters in nested groups

        Yields:
            Parameter instances found in this collection and optionally nested groups
        """
        parameters = [{k: v} for k, v in self.model_dump().items()]
        param_groups = self._iter_subparamgroups()
        yield from parameters
        if recursive:
            for pg in param_groups:
                yield from pg._iter_parameters(recursive=True)

    def __iter__(self) -> Iterable[DataT]:
        """
        Make Parameters iterable, yielding all contained Parameter instances.

        Returns:
            Iterator over all parameters including those in nested groups
        """
        return self._iter_parameters(recursive=True)

    def get(self, name: str, default: Any = None) -> DataT | Any | None:
        """
        Retrieve a parameter or parameter group by name.

        Args:
            name: Name of the parameter or group to find
            default: Value to return if not found

        Returns:
            The parameter/group if found, otherwise the default value
        """
        if (group := getattr(self, name, None)) is not None:
            return group
        for param in self._iter_parameters(recursive=True):
            if name in param:
                # return param
                return param.get(name)
        return default

    def has(self, name: str) -> bool:
        """
        Check if a parameter or parameter group exists by name. If you check for a parameter
        with `if group.get("val")` and the value is falsy (0, "", False, None), the check will fail.
        This method avoids that problem.

        Args:
            name: Name of the parameter or group to check

        Returns:
            True if the parameter/group exists, False otherwise
        """
        if getattr(self, name, None) is not None:
            return True
        for param in self._iter_parameters(recursive=True):
            if name in param:
                return True
        return False

    @classmethod
    def from_yaml_str(cls, raw: str) -> Self:
        """
        Load a Parameters instance from a YAML file.

        Args:
            raw: the string

        Returns:
            A new Parameters instance with values from the YAML file
        """
        data = yaml.safe_load(raw)
        return cls.model_validate(data)

    @classmethod
    def from_yaml(cls, path: str | PathLike) -> Self:
        """
        Load a Parameters instance from a YAML file.

        Args:
            path: Path to the YAML file to load

        Returns:
            A new Parameters instance with values from the YAML file
        """
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)

    def to_yaml(self, path: str | PathLike, exclude_unset: bool = True) -> None:
        """
        Save this Parameters instance to a YAML file.

        Args:
            path: Path where the YAML file should be written
            exclude_unset: If True, only include fields that have been explicitly set
        """
        with open(path, "w") as f:
            j = json.loads(self.model_dump_json(exclude_unset=exclude_unset))
            yaml.safe_dump(j, f)

    def get_auto_params(self) -> Iterable[Any]:
        """
        Get all AutoParam instances that can be updated.

        Yields:
            Tuples of (field_name, AutoParam) for updatable parameters
        """
        for param in self:
            if param == "auto":
                yield param

    @classmethod
    def from_params(cls, **kwargs) -> Self:
        """
        Create a Parameters instance from keyword arguments.
        small convenience method.

        Args:
            **kwargs: Parameter values to set

        Returns:
            A new Parameters instance with the provided values
        """
        return cls.model_validate(kwargs)
