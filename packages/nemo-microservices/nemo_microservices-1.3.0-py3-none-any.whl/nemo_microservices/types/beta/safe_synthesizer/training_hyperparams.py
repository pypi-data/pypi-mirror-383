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

from typing import List, Union, Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["TrainingHyperparams"]


class TrainingHyperparams(BaseModel):
    batch_size: Optional[int] = None
    """The batch size per device for training"""

    gradient_accumulation_steps: Optional[int] = None
    """
    Number of update steps to accumulate the gradients for, before performing a
    backward/update pass. This technique increases the effective batch size that
    will fit into GPU memory.
    """

    learning_rate: Optional[float] = None
    """The initial learning rate for `AdamW` optimizer."""

    lora_alpha_over_r: Optional[float] = None
    """The ratio of the LoRA scaling factor (alpha) to the LoRA rank.

    Empirically, this parameter works well when set to 0.5, 1, or 2.
    """

    lora_r: Optional[int] = None
    """The rank of the LoRA update matrices, expressed in int.

    Lower rank results in smaller update matrices with fewer trainable parameters.
    """

    lora_target_modules: Optional[List[str]] = None
    """The list of transformer modules to apply LoRA to.

    Possible modules: 'q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj',
    'up_proj', 'down_proj'
    """

    lr_scheduler: Optional[str] = None
    """The scheduler type to use.

    See the HuggingFace documentation of `SchedulerType` for all possible values.
    """

    num_input_records_to_sample: Union[Literal["auto"], int, None] = None
    """Number of records the model will see during training.

    This parameter is a proxy for training time. For example, if its value is the
    same size as the input dataset, this is like training for a single epoch. If its
    value is larger, this is like training for multiple (possibly fractional)
    epochs. If its value is smaller, this is like training for a fraction of an
    epoch. Supports 'auto' where a reasonable value is chosen based on other config
    params and data.
    """

    pretrained_model: Optional[str] = None
    """Pretrained model to use for fine tuning. Uses default of TinyLlama."""

    rope_scaling_factor: Union[Literal["auto"], int, None] = None
    """Scale the base LLM's context length by this factor using RoPE scaling."""

    use_unsloth: Union[Literal["auto"], bool, None] = None
    """Whether to use unsloth."""

    validation_ratio: Optional[float] = None
    """
    The fraction of the training data that will be used for validation.The range
    should be 0 to 1. If set to 0, no validation will be performed.If set larger
    than 0, validation loss will be computed and reported throughout training.
    """

    validation_steps: Optional[int] = None
    """The number of steps between validation checks for the HF Trainer arguments."""

    warmup_ratio: Optional[float] = None
    """
    Ratio of total training steps used for a linear warmup from 0 to the learning
    rate.
    """

    weight_decay: Optional[float] = None
    """
    The weight decay to apply (if not zero) to all layers except all bias and
    LayerNorm weights in the AdamW optimizer.
    """
