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
Configurator: A mini-library for Pydantic-based configuration systems with strong typing support.

This package provides a comprehensive set of tools for building type-safe, validated
configuration systems using Pydantic v2. It's designed for developers who need
sophisticated parameter management with excellent static analysis support.

Key Components:

Parameter Wrappers (parameter.py):
    - Parameter: Generic wrapper for configuration values with Pydantic integration
    - AutoParam: Parameter with automatic type-safe update capabilities
    - UnsetParam: For handling unset/default parameter states
    - ValidNoneParam: For parameters where None is a valid value

Validation & Collections (parameters.py):
    - Parameters: Abstract base class for organizing parameter collections
    - DependsOnValidator: Conditional field validation based on other fields
    - ValueValidator: Custom validation functions for parameter values
    - YAML serialization support for configuration persistence

Usage Examples:

Basic Parameter Usage:
    >>> from nemo_safe_synthesizer.configurator.parameter import Parameter, AutoParam
    >>>
    >>> # Simple parameter
    >>> max_size = Parameter(name="max_size", value=1000)
    >>>
    >>> # Auto-updating parameter
    >>> batch_size = AutoParam(name="batch_size", value=32)
    >>> batch_size.autoupdate(64)  # Safe type-checked update

Parameter Collections:
    >>> from nemo_safe_synthesizer.configurator.parameters import Parameters
    >>> from nemo_safe_synthesizer.configurator.parameter import AutoParam
    >>> from typing import Annotated
    >>> from pydantic import Field
    >>> class DatabaseConfig(Parameters):
    ...     host: Annotated[AutoParam[str], Field(default=AutoParam(name="host", value="localhost")]
    ...     port: Annotated[AutoParam[int], Field(default=AutoParam(name="port", value=5432)]
    >>>
    >>> config = DatabaseConfig()
    >>> config.host
    AutoParam(name='host', value='localhost')

Conditional Validation:
    >>> from nemo_safe_synthesizer.configurator.parameters import Parameters
    >>> from nemo_safe_synthesizer.configurator.validators import DependsOnValidator
    >>> from nemo_safe_synthesizer.configurator.parameter import AutoParam
    >>> from typing import Annotated
    >>>
    >>> class AdvancedConfig(Parameters):
    ...     debug_mode: bool = False
    ...     verbose_logging: Annotated[
    ...         Parameter[bool],
    ...         DependsOnValidator(
    ...             depends_on="debug_mode",
    ...             depends_on_func=lambda x: x is True
    ...         ),
    ...         Field(default=Parameter(name="verbose_logging", value=False))
    ...     ]
"""
