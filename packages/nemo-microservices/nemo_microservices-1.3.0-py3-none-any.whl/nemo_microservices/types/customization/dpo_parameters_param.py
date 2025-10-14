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

__all__ = ["DpoParametersParam"]


class DpoParametersParam(TypedDict, total=False):
    preference_average_log_probs: bool
    """
    If set to true, the preference loss uses average log-probabilities, making the
    loss less sensitive to sequence length. Setting it to false (default) uses total
    log-probabilities, giving more influence to longer sequences.
    """

    preference_loss_weight: float
    """Scales the contribution of the preference loss to the overall training
    objective.

    Increasing this value emphasizes learning from preference comparisons more
    strongly.
    """

    ref_policy_kl_penalty: float
    """
    Controls how strongly the trained policy is penalized for deviating from the
    reference policy. Increasing this value encourages the policy to stay closer to
    the reference (more conservative learning), while decreasing it allows more
    freedom to explore user-preferred behavior. Parameter is called `beta` in the
    original paper
    """

    sft_average_log_probs: bool
    """
    If set to true, the supervised fine-tuning (SFT) loss normalizes by sequence
    length, treating all examples equally regardless of length. If false (default),
    longer examples contribute more to the loss.
    """

    sft_loss_weight: float
    """Scales the contribution of the supervised fine-tuning loss.

    Setting this to 0 disables SFT entirely, allowing training to focus exclusively
    on preference-based optimization.
    """
