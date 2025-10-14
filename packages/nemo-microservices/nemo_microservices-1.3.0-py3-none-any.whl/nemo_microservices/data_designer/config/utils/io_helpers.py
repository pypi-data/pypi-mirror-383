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

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def read_parquet_dataset(path: Path) -> pd.DataFrame:
    """Read a parquet dataset from a path.

    Args:
        path: The path to the parquet dataset, can be either a file or a directory.

    Returns:
        The parquet dataset as a pandas DataFrame.
    """
    try:
        return pd.read_parquet(path, dtype_backend="pyarrow")
    except Exception as e:
        if path.is_dir() and "Unsupported cast" in str(e):
            logger.warning("Failed to read parquets as folder, falling back to individual files")
            return pd.concat(
                [pd.read_parquet(file, dtype_backend="pyarrow") for file in sorted(path.glob("*.parquet"))],
                ignore_index=True,
            )
        else:
            raise e
