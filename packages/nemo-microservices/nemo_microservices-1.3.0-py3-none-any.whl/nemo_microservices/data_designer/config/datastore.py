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

import logging
from pathlib import Path
from typing import Optional, Union

import pandas as pd
import pyarrow.parquet as pq
from huggingface_hub import HfApi, HfFileSystem
from pydantic import BaseModel, Field

from .errors import InvalidConfigError, InvalidFileFormatError, InvalidFilePathError

logger = logging.getLogger(__name__)


class DatastoreSettings(BaseModel):
    """Configuration for interacting with a datastore."""

    endpoint: str = Field(
        ...,
        description="Datastore endpoint. Use 'https://huggingface.co' for the Hugging Face Hub.",
    )
    token: Optional[str] = Field(default=None, description="If needed, token to use for authentication.")


def get_file_column_names(file_path: Union[str, Path], file_type: str) -> list[str]:
    """Extract column names based on file type."""
    if file_type == "parquet":
        try:
            schema = pq.read_schema(file_path)
            if hasattr(schema, "names"):
                return schema.names
            else:
                return [field.name for field in schema]
        except Exception as e:
            logger.warning(f"Failed to process parquet file {file_path}: {e}")
            return []
    elif file_type in ["json", "jsonl"]:
        return pd.read_json(file_path, orient="records", lines=True, nrows=1).columns.tolist()
    elif file_type == "csv":
        try:
            df = pd.read_csv(file_path, nrows=1)
            return df.columns.tolist()
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            logger.warning(f"Failed to process CSV file {file_path}: {e}")
            return []
    else:
        raise InvalidFilePathError(f"🛑 Unsupported file type: {file_type!r}")


def fetch_seed_dataset_column_names(
    repo_id: str,
    filename: str,
    dataset_path: Optional[Union[str, Path]] = None,
    datastore_settings: Optional[Union[DatastoreSettings, dict]] = None,
) -> list[str]:
    # Determine file type
    file_type = filename.split(".")[-1]
    if file_type not in {"parquet", "json", "jsonl", "csv"}:
        raise InvalidFileFormatError(f"🛑 Unsupported file type: {filename!r}")

    # Try local file first
    if dataset_path is not None:
        return get_file_column_names(dataset_path, file_type)

    # Fall back to remote file - resolve datastore only when needed
    datastore_settings = resolve_datastore_settings(datastore_settings)
    fs = HfFileSystem(endpoint=datastore_settings.endpoint, token=datastore_settings.token)

    with fs.open(f"datasets/{repo_id}/{filename}") as f:
        return get_file_column_names(f, file_type)


def resolve_datastore_settings(datastore_settings: DatastoreSettings | dict | None) -> DatastoreSettings:
    if datastore_settings is None:
        raise InvalidConfigError("🛑 Datastore settings are required in order to upload datasets to the datastore.")
    if isinstance(datastore_settings, DatastoreSettings):
        return datastore_settings
    elif isinstance(datastore_settings, dict):
        return DatastoreSettings.model_validate(datastore_settings)
    else:
        raise InvalidConfigError(
            "🛑 Invalid datastore settings format. Must be DatastoreSettings object or dictionary."
        )


def upload_to_hf_hub(
    dataset_path: Union[str, Path],
    filename: str,
    repo_id: str,
    datastore_settings: DatastoreSettings,
    **kwargs,
) -> str:
    datastore_settings = resolve_datastore_settings(datastore_settings)
    dataset_path = _validate_dataset_path(dataset_path)
    filename_ext = filename.split(".")[-1].lower()
    if dataset_path.suffix.lower()[1:] != filename_ext:
        raise InvalidFileFormatError(
            f"🛑 Dataset file extension {dataset_path.suffix!r} does not match `filename` extension .{filename_ext!r}"
        )

    hfapi = HfApi(endpoint=datastore_settings.endpoint, token=datastore_settings.token)
    hfapi.create_repo(repo_id, exist_ok=True, repo_type="dataset")
    hfapi.upload_file(
        path_or_fileobj=dataset_path,
        path_in_repo=filename,
        repo_id=repo_id,
        repo_type="dataset",
        **kwargs,
    )
    return f"{repo_id}/{filename}"


def _validate_dataset_path(dataset_path: Union[str, Path]) -> Path:
    if not Path(dataset_path).is_file():
        raise InvalidFilePathError("🛑 To upload a dataset to the datastore, you must provide a valid file path.")
    if not Path(dataset_path).name.endswith((".parquet", ".csv", ".json", ".jsonl")):
        raise InvalidFileFormatError(
            "🛑 Dataset files must be in `parquet`, `csv`, or `json` (orient='records', lines=True) format."
        )
    return Path(dataset_path)
