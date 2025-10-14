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

__all__ = ["DifferentialPrivacyHyperparams"]


class DifferentialPrivacyHyperparams(BaseModel):
    delta: Union[Literal["auto"], float, None] = None
    """Probability of accidentally leaking information.

    Setting to 'auto' usesdelta of 1/n^1.2, where n is the number of training
    records
    """

    dp_enabled: Optional[bool] = None
    """Enable differentially-private training with DP-SGD."""

    epsilon: Optional[float] = None
    """Target for epsilon when training completes."""

    per_sample_max_grad_norm: Optional[float] = None
    """Maximum L2 norm of per sample gradients."""
