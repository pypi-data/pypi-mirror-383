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

from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["EvaluationParametersParam"]


class EvaluationParametersParam(TypedDict, total=False):
    aia_enabled: bool
    """Enable attribute inference attack evaluation."""

    enabled: bool
    """Enable evaluation."""

    mandatory_columns: int

    mia_enabled: bool
    """Enable membership inference attack evaluation."""

    pii_replay_columns: SequenceNotStr[str]
    """List of columns for PII Replay. If not provided, only entities will be used."""

    pii_replay_enabled: bool
    """Enable PII Replay detection."""

    pii_replay_entities: SequenceNotStr[str]
    """List of entities for PII Replay.

    If not provided, default entities will be used.
    """

    quasi_identifier_count: int
    """Number of quasi-identifiers to sample."""

    sqs_report_columns: int

    sqs_report_rows: int
