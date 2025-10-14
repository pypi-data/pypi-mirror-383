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
from collections import OrderedDict
from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

import numpy as np
import pandas as pd
from rich.console import Console, Group
from rich.padding import Padding
from rich.panel import Panel
from rich.pretty import Pretty
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from ..base import ConfigBase
from ..columns import DataDesignerColumnType
from ..sampler_params import SamplerType
from .code_lang import code_lang_to_syntax_lexer

if TYPE_CHECKING:
    from ..config_builder import DataDesignerConfigBuilder


console = Console()


class ColorPalette(str, Enum):
    NVIDIA_GREEN = "#76b900"
    PURPLE = "#9525c6"
    YELLOW = "#f9c500"
    BLUE = "#0074df"
    RED = "#e52020"
    ORANGE = "#ef9100"
    MAGENTA = "#d2308e"
    TEAL = "#1dbba4"


def create_rich_histogram_table(
    data: dict[str, Union[int, float]],
    column_names: tuple[int, int],
    name_style: str = ColorPalette.BLUE.value,
    value_style: str = ColorPalette.TEAL.value,
    title: Optional[str] = None,
    **kwargs,
) -> Table:
    table = Table(title=title, **kwargs)
    table.add_column(column_names[0], justify="right", style=name_style)
    table.add_column(column_names[1], justify="left", style=value_style)

    max_count = max(data.values())
    for name, value in data.items():
        bar = "" if max_count <= 0 else "█" * int((value / max_count) * 20)
        table.add_row(str(name), f"{bar} {value:.1f}")

    return table


def display_sample_record(
    record: Union[dict, pd.Series, pd.DataFrame],
    config_builder: DataDesignerConfigBuilder,
    background_color: Optional[str] = None,
    syntax_highlighting_theme: str = "dracula",
    record_index: Optional[int] = None,
    hide_seed_columns: bool = False,
):
    if isinstance(record, (dict, pd.Series)):
        record = pd.DataFrame([record]).iloc[0]
    elif isinstance(record, pd.DataFrame):
        if record.shape[0] > 1:
            raise ValueError(
                f"The record must be a single record. You provided a DataFrame with {record.shape[0]} records."
            )
        record = record.iloc[0]
    else:
        raise ValueError(
            "The record must be a single record in a dictionary, pandas Series, "
            f"or pandas DataFrame. You provided: {type(record)}."
        )

    render_list = []
    table_kws = dict(show_lines=True, expand=True)

    seed_columns = config_builder.get_columns_of_type(DataDesignerColumnType.SEED_DATASET)
    if not hide_seed_columns and len(seed_columns) > 0:
        table = Table(title="Seed Columns", **table_kws)
        table.add_column("Name")
        table.add_column("Value")
        for col in seed_columns:
            if not col.drop:
                table.add_row(col.name, convert_to_row_element(record[col.name]))
        render_list.append(pad_console_element(table))

    non_code_columns = (
        config_builder.get_columns_of_type(DataDesignerColumnType.SAMPLER)
        + config_builder.get_columns_of_type(DataDesignerColumnType.EXPRESSION)
        + config_builder.get_columns_of_type(DataDesignerColumnType.LLM_TEXT)
        + config_builder.get_columns_of_type(DataDesignerColumnType.LLM_STRUCTURED)
    )
    if len(non_code_columns) > 0:
        table = Table(title="Generated Columns", **table_kws)
        table.add_column("Name")
        table.add_column("Value")
        for col in non_code_columns:
            if not col.drop:
                table.add_row(col.name, convert_to_row_element(record[col.name]))
        render_list.append(pad_console_element(table))

    for col in config_builder.get_columns_of_type(DataDesignerColumnType.LLM_CODE):
        panel = Panel(
            Syntax(
                record[col.name],
                lexer=code_lang_to_syntax_lexer(col.code_lang),
                theme=syntax_highlighting_theme,
                word_wrap=True,
                background_color=background_color,
            ),
            title=col.name,
            expand=True,
        )
        render_list.append(pad_console_element(panel))

    validation_columns = config_builder.get_columns_of_type(DataDesignerColumnType.VALIDATION)
    if len(validation_columns) > 0:
        table = Table(title="Validation", **table_kws)
        table.add_column("Name")
        table.add_column("Value", ratio=1)
        for col in validation_columns:
            if not col.drop:
                # Add is_valid before other fields
                if "is_valid" in record[col.name]:
                    value_to_display = {"is_valid": record[col.name].get("is_valid")} | record[col.name]
                else:  # if columns treated separately
                    value_to_display = {}
                    for col_name, validation_output in record[col.name].items():
                        value_to_display[col_name] = {
                            "is_valid": validation_output.get("is_valid", None)
                        } | validation_output

                table.add_row(col.name, convert_to_row_element(value_to_display))
        render_list.append(pad_console_element(table, (1, 0, 1, 0)))

    llm_judge_columns = config_builder.get_columns_of_type(DataDesignerColumnType.LLM_JUDGE)
    if len(llm_judge_columns) > 0:
        for col in llm_judge_columns:
            if col.drop:
                continue
            table = Table(title=f"LLM-as-a-Judge: {col.name}", **table_kws)
            row = []
            judge = record[col.name]

            for measure, results in judge.items():
                table.add_column(measure)
                row.append(f"score: {results['score']}\nreasoning: {results['reasoning']}")
            table.add_row(*row)
            render_list.append(pad_console_element(table, (1, 0, 1, 0)))

    if record_index is not None:
        index_label = Text(f"[index: {record_index}]", justify="center")
        render_list.append(index_label)

    console.print(Group(*render_list), markup=False)


def display_sampler_table(
    sampler_params: dict[SamplerType, ConfigBase],
    title: Optional[str] = None,
) -> None:
    table = Table(expand=True)
    table.add_column("Type")
    table.add_column("Parameter")
    table.add_column("Data Type")
    table.add_column("Required", justify="center")
    table.add_column("Constraints")

    for sampler_type, params in sampler_params.items():
        num = 0
        schema = params.model_json_schema()
        for param_name, field_info in schema["properties"].items():
            is_required = param_name in schema.get("required", [])
            table.add_row(
                sampler_type if num == 0 else "",
                param_name,
                _get_field_type(field_info),
                "✓" if is_required else "",
                _get_field_constraints(field_info, schema),
            )
            num += 1
        table.add_section()

    title = title or "NeMo Data Designer Samplers"

    group = Group(Rule(title, end="\n\n"), table)
    console.print(group)


def convert_to_row_element(elem):
    try:
        elem = Pretty(json.loads(elem))
    except (TypeError, json.JSONDecodeError):
        pass
    if isinstance(elem, (np.integer, np.floating, np.ndarray)):
        elem = str(elem)
    elif isinstance(elem, (list, dict)):
        elem = Pretty(elem)
    return elem


def pad_console_element(elem, padding=(1, 0, 1, 0)):
    return Padding(elem, padding)


def _get_field_type(field: dict) -> str:
    """Extract human-readable type information from a JSON Schema field."""

    # single type
    if "type" in field:
        if field["type"] == "array":
            return " | ".join([f"{f.strip()}[]" for f in _get_field_type(field["items"]).split("|")])
        if field["type"] == "object":
            return "dict"
        return field["type"]

    # union type
    elif "anyOf" in field:
        types = []
        for f in field["anyOf"]:
            if "$ref" in f:
                types.append("enum")
            elif f.get("type") == "array":
                if "items" in f and "$ref" in f["items"]:
                    types.append("enum[]")
                else:
                    types.append(f"{f['items']['type']}[]")
            else:
                types.append(f.get("type", ""))
        return " | ".join(t for t in types if t)

    return ""


def _get_field_constraints(field: dict, schema: dict) -> str:
    """Extract human-readable constraints from a JSON Schema field."""
    constraints = []

    # numeric constraints
    if "minimum" in field:
        constraints.append(f">= {field['minimum']}")
    if "exclusiveMinimum" in field:
        constraints.append(f"> {field['exclusiveMinimum']}")
    if "maximum" in field:
        constraints.append(f"<= {field['maximum']}")
    if "exclusiveMaximum" in field:
        constraints.append(f"< {field['exclusiveMaximum']}")

    # string constraints
    if "minLength" in field:
        constraints.append(f"len > {field['minLength']}")
    if "maxLength" in field:
        constraints.append(f"len < {field['maxLength']}")

    # array constraints
    if "minItems" in field:
        constraints.append(f"len > {field['minItems']}")
    if "maxItems" in field:
        constraints.append(f"len < {field['maxItems']}")

    # enum constraints
    if "enum" in _get_field_type(field) and "$defs" in schema:
        enum_values = []
        for defs in schema["$defs"].values():
            if "enum" in defs:
                enum_values.extend(defs["enum"])
        if len(enum_values) > 0:
            enum_values = OrderedDict.fromkeys(enum_values)
            constraints.append(f"allowed: {', '.join(enum_values.keys())}")

    return ", ".join(constraints)
