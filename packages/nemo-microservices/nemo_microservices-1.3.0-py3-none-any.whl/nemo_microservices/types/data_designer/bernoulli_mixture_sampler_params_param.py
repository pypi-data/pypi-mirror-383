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

from typing import Dict
from typing_extensions import Required, TypedDict

__all__ = ["BernoulliMixtureSamplerParamsParam"]


class BernoulliMixtureSamplerParamsParam(TypedDict, total=False):
    dist_name: Required[str]
    """Mixture distribution name.

    Samples will be equal to the distribution sample with probability `p`, otherwise
    equal to 0. Must be a valid scipy.stats distribution name.
    """

    dist_params: Required[Dict[str, object]]
    """Parameters of the scipy.stats distribution given in `dist_name`."""

    p: Required[float]
    """Bernoulli distribution probability of success."""
