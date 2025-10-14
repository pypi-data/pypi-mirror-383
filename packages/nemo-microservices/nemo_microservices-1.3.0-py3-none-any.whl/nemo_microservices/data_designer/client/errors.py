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

from ..errors import DataDesignerError


class DataDesignerClientError(DataDesignerError):
    """Base exception for Data Designer client errors."""


class DataDesignerConfigValidationError(DataDesignerClientError):
    """Exception raised when the Data Designer configuration is invalid."""


def handle_api_exceptions(e: Exception) -> None:
    if hasattr(e, "status_code") and e.status_code == 422:
        raise DataDesignerConfigValidationError(f"‼️ Config validation failed!\n{e}") from None
    else:
        raise DataDesignerClientError(f"‼️ Something went wrong!\n{e}") from None
