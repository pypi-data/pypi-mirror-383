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

from typing import Union, Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["DataParameters"]


class DataParameters(BaseModel):
    group_training_examples_by: Optional[str] = None
    """Column(s) to group training examples by.

    This is useful when you want the model to learn inter-record correlations for a
    given grouping of records.
    """

    holdout: Optional[float] = None
    """Amount of records to holdout.

    If this is a float between 0 and 1, that ratio of records is held out. If an
    integer greater than 1, that number of records is held out.If the value is equal
    to zero, no holdout will be performed.
    """

    max_holdout: Optional[int] = None
    """Maximum number of records to hold out.

    Overrides any behavior set by holdout parameter.
    """

    max_sequences_per_example: Union[Literal["auto"], int, None] = None
    """
    If specified, adds at most this number of sequences per example; otherwise,
    fills up context. Supports 'auto' where a value of 1 is chosen if differential
    privacy is enabled, and None otherwise. Required for DP to limit contribution of
    each example.
    """

    order_training_examples_by: Optional[str] = None
    """Column to order training examples by.

    This is useful when you want the model to learn sequential relationships for a
    given ordering of records. If you provide this parameter, you must also provide
    `group_training_examples_by`.
    """

    random_state: Optional[int] = None
    """Use this random state for holdout split to ensure reproducibility."""
