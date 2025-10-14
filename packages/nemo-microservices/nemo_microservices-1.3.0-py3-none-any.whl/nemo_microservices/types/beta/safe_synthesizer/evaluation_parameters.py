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

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["EvaluationParameters"]


class EvaluationParameters(BaseModel):
    aia_enabled: Optional[bool] = None
    """Enable attribute inference attack evaluation."""

    enabled: Optional[bool] = None
    """Enable evaluation."""

    mandatory_columns: Optional[int] = None

    mia_enabled: Optional[bool] = None
    """Enable membership inference attack evaluation."""

    pii_replay_columns: Optional[List[str]] = None
    """List of columns for PII Replay. If not provided, only entities will be used."""

    pii_replay_enabled: Optional[bool] = None
    """Enable PII Replay detection."""

    pii_replay_entities: Optional[List[str]] = None
    """List of entities for PII Replay.

    If not provided, default entities will be used.
    """

    quasi_identifier_count: Optional[int] = None
    """Number of quasi-identifiers to sample."""

    sqs_report_columns: Optional[int] = None

    sqs_report_rows: Optional[int] = None
