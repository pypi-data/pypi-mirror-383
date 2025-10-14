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

import json
import os
import re
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd
import yaml
from jinja2 import TemplateSyntaxError, meta
from jinja2.sandbox import ImmutableSandboxedEnvironment

from .errors import UserJinjaTemplateSyntaxError

REPR_LIST_LENGTH_USE_JSON = 4


def _split_camel_case(s: str, sep: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", sep, s).lower()


def camel_to_kebab(s: str) -> str:
    return _split_camel_case(s, "-")


def camel_to_snake(s: str) -> str:
    return _split_camel_case(s, "_")


def kebab_to_snake(s: str) -> str:
    return s.replace("-", "_")


@contextmanager
def template_error_handler():
    try:
        yield
    except TemplateSyntaxError as exception:
        exception_string = (
            f"Encountered a syntax error in the provided Jinja2 template:\n{str(exception)}\n"
            "For more information on writing Jinja2 templates, "
            "refer to https://jinja.palletsprojects.com/en/stable/templates"
        )
        raise UserJinjaTemplateSyntaxError(exception_string)
    except Exception:
        raise


def assert_valid_jinja2_template(template: str) -> None:
    """Raises an error if the template cannot be parsed."""
    with template_error_handler():
        meta.find_undeclared_variables(ImmutableSandboxedEnvironment().parse(template))


def get_prompt_template_keywords(template: str) -> set[str]:
    """Extract all keywords from a valid string template."""
    with template_error_handler():
        ast = ImmutableSandboxedEnvironment().parse(template)
        keywords = set(meta.find_undeclared_variables(ast))

    return keywords


def make_date_obj_serializable(obj: dict) -> dict:
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj: Any) -> Any:
            if isinstance(obj, date):
                return obj.isoformat()
            return super().default(obj)

    return json.loads(json.dumps(obj, cls=DateTimeEncoder))


def json_indent_list_of_strings(
    column_names: list[str], *, indent: Optional[Union[int, str]] = None
) -> Optional[Union[list[str], str]]:
    """Convert a list of column names to a JSON string if the list is long.

    This function helps keep Data Designer's __repr__ output clean and readable.

    Args:
        column_names: List of column names.
        indent: Indentation for the JSON string.

    Returns:
        A list of column names or a JSON string if the list is long.
    """
    return (
        None
        if len(column_names) == 0
        else (
            column_names if len(column_names) < REPR_LIST_LENGTH_USE_JSON else json.dumps(column_names, indent=indent)
        )
    )


def smart_load_dataframe(dataframe: Union[str, Path, pd.DataFrame]) -> pd.DataFrame:
    """Load a dataframe from file if a path is given, otherwise return the dataframe.

    Args:
        dataframe: A path to a file or a pandas DataFrame object.

    Returns:
        A pandas DataFrame object.
    """
    if isinstance(dataframe, pd.DataFrame):
        return dataframe

    # Get the file extension.
    if isinstance(dataframe, str) and dataframe.startswith("http"):
        ext = dataframe.split(".")[-1].lower()
    else:
        dataframe = Path(dataframe)
        ext = dataframe.suffix.lower()
        if not dataframe.exists():
            raise FileNotFoundError(f"File not found: {dataframe}")

    # Load the dataframe based on the file extension.
    if ext == "csv":
        return pd.read_csv(dataframe)
    elif ext == "json":
        return pd.read_json(dataframe, lines=True)
    elif ext == "parquet":
        return pd.read_parquet(dataframe)
    else:
        raise ValueError(f"Unsupported file format: {dataframe}")


def smart_load_yaml(yaml_in: Union[str, Path, dict]) -> dict:
    """Return the yaml config as a dict given flexible input types.

    Args:
        config: The config as a dict, yaml string, or yaml file path.

    Returns:
        The config as a dict.
    """
    if isinstance(yaml_in, dict):
        yaml_out = yaml_in
    elif isinstance(yaml_in, Path) or (isinstance(yaml_in, str) and os.path.isfile(yaml_in)):
        with open(yaml_in) as file:
            yaml_out = yaml.safe_load(file)
    elif isinstance(yaml_in, str):
        if yaml_in.endswith((".yaml", ".yml")) and not os.path.isfile(yaml_in):
            raise FileNotFoundError(f"File not found: {yaml_in}")
        else:
            yaml_out = yaml.safe_load(yaml_in)
    else:
        raise ValueError(
            f"'{yaml_in}' is an invalid yaml config format. Valid options are: dict, yaml string, or yaml file path."
        )

    if not isinstance(yaml_out, dict):
        raise ValueError(f"Loaded yaml must be a dict. Got {yaml_out}, which is of type {type(yaml_out)}.")

    return yaml_out
