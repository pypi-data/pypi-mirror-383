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

from typing import (
    Annotated,
)

from pydantic import (
    Field,
)

from ..configurator.parameters import (
    Parameters,
)
from ..configurator.validators import (
    ValueValidator,
    range_validator,
)
from .base import LRScheduler
from .types import (
    AUTO_STR,
    AutoBoolParam,
    AutoIntParam,
    OptionalAutoInt,
)

__all__ = [
    "TrainingHyperparams",
]

ValueGTZero = ValueValidator(lambda p: range_validator(p, lambda v: v >= 0))


class TrainingHyperparams(Parameters):
    """Hyperparameters that control the training process behavior.

    This class contains all the fine-tuning hyperparameters that control how the model
    learns, including learning rates, batch sizes, LoRA configuration, and optimization
    settings. These parameters directly affect training performance and quality.

    Attributes:
        num_input_records_to_sample: Number of records the model will see during training.
            This parameter is a proxy for training time. For example, if its value is the same
            size as the input dataset, this is like training for a single epoch. If its value
            is larger, this is like training for multiple (possibly fractional) epochs. If its
            value is smaller, this is like training for a fraction of an epoch. Supports 'auto'
            where a reasonable value is chosen based on other config params and data.
        batch_size: The batch size per device for training.
        gradient_accumulation_steps: Number of update steps to accumulate the gradients for,
            before performing a backward/update pass. This technique increases the effective
            batch size that will fit into GPU memory.
        weight_decay: The weight decay to apply (if not zero) to all layers except all
            bias and LayerNorm weights in the AdamW optimizer.
        warmup_ratio: Ratio of total training steps used for a linear warmup from 0
            to the learning rate.
        lr_scheduler: The scheduler type to use. See the HuggingFace documentation of
            `SchedulerType` for all possible values.
        learning_rate: The initial learning rate for `AdamW` optimizer.
        lora_r: The rank of the LoRA update matrices, expressed in int. Lower
            rank results in smaller update matrices with fewer trainable parameters.
        lora_alpha_over_r: The ratio of the LoRA scaling factor (alpha) to
            the LoRA rank. Empirically, this parameter works well when set to 0.5, 1, or 2.
        lora_target_modules: The list of transformer modules to apply LoRA to.
            Possible modules: 'q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'
        use_unsloth: Whether to use unsloth.
        rope_scaling_factor: Scale the base LLM's context length by this factor using RoPE scaling.
        validation_ratio: The fraction of the training data that will be used for validation.
            The range should be 0 to 1. If set to 0, no validation will be performed.
            If set larger than 0, validation loss will be computed and reported throughout training.
        validation_steps: The number of steps between validation checks for the HF Trainer arguments.
        pretrained_model: Pretrained model to use for fine-tuning. Uses default of TinyLlama.


    """

    num_input_records_to_sample: Annotated[
        AutoIntParam,
        ValueGTZero,
        Field(
            title="num_input_records_to_sample",
            description=(
                "Number of records the model will see during training. This parameter is a "
                "proxy for training time. For example, if its value is the same size as the "
                "input dataset, this is like training for a single epoch. If its value "
                "is larger, this is like training for multiple (possibly fractional) epochs. "
                "If its value is smaller, this is like training for a fraction of an epoch. "
                "Supports 'auto' where a reasonable value is chosen based on other config "
                "params and data."
            ),
        ),
    ] = AUTO_STR

    batch_size: Annotated[
        int,
        ValueValidator(value_func=lambda v: v >= 1),
        Field(
            title="batch_size",
            description="The batch size per device for training",
        ),
    ] = 1

    gradient_accumulation_steps: Annotated[
        int,
        ValueValidator(value_func=lambda v: v >= 1),
        Field(
            title="gradient_accumulation_steps",
            description=(
                "Number of update steps to accumulate the gradients for, before "
                "performing a backward/update pass. This technique increases "
                "the effective batch size that will fit into GPU memory."
            ),
        ),
    ] = 8

    weight_decay: Annotated[
        float,
        ValueValidator(value_func=lambda v: 0 < v < 1),
        Field(
            title="weight_decay",
            description=(
                "The weight decay to apply (if not zero) to all layers except all bias and "
                "LayerNorm weights in the AdamW optimizer."
            ),
        ),
    ] = 0.01

    warmup_ratio: Annotated[
        float,
        ValueValidator(value_func=lambda v: v > 0),
        Field(
            title="warmup_ratio",
            description="Ratio of total training steps used for a linear warmup from 0 to the learning rate.",
        ),
    ] = 0.05

    lr_scheduler: Annotated[
        str,
        Field(
            title="lr_scheduler",
            description=(
                "The scheduler type to use. See the HuggingFace documentation of `SchedulerType` for all possible values."
            ),
        ),
    ] = LRScheduler.COSINE.value

    learning_rate: Annotated[
        float,
        ValueValidator(value_func=lambda v: 0 < v < 1),
        Field(
            title="learning_rate",
            description="The initial learning rate for `AdamW` optimizer.",
        ),
    ] = 0.0005

    lora_r: Annotated[
        int,
        ValueValidator(value_func=lambda v: v > 0),
        Field(
            title="lora_r",
            description=(
                "The rank of the LoRA update matrices, expressed in int. "
                "Lower rank results in smaller update matrices with fewer trainable parameters."
            ),
        ),
    ] = 32

    lora_alpha_over_r: Annotated[
        float,
        ValueValidator(value_func=lambda v: (v >= 0.5) and (v <= 3)),
        Field(
            title="lora_alpha_over_r",
            description=(
                "The ratio of the LoRA scaling factor (alpha) to the LoRA rank. "
                "Empirically, this parameter works well when set to 0.5, 1, or 2."
            ),
        ),
    ] = 1.0

    lora_target_modules: Annotated[
        list[str],
        Field(
            title="lora_target_modules",
            description=(
                "The list of transformer modules to apply LoRA to. Possible modules: "
                "'q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'"
            ),
        ),
    ] = ["q_proj", "k_proj", "v_proj", "o_proj"]

    use_unsloth: Annotated[
        AutoBoolParam,
        ValueValidator(value_func=lambda v: v is not None),
        Field(
            title="use_unsloth",
            description="Whether to use unsloth.",
        ),
    ] = AUTO_STR

    rope_scaling_factor: Annotated[
        OptionalAutoInt,
        ValueValidator(lambda p: range_validator(p, lambda v: v >= 1)),
        Field(
            title="rope_scaling_factor",
            description="Scale the base LLM's context length by this factor using RoPE scaling.",
        ),
    ] = AUTO_STR

    validation_ratio: Annotated[
        float,
        ValueValidator(value_func=lambda v: 0 <= v <= 1),
        Field(
            title="validation_ratio",
            description=(
                "The fraction of the training data that will be used for validation."
                "The range should be 0 to 1. If set to 0, no validation will be performed."
                "If set larger than 0, validation loss will be computed and reported "
                "throughout training."
            ),
        ),
    ] = 0.0

    validation_steps: Annotated[
        int,
        ValueValidator(value_func=lambda v: v > 0),
        Field(
            title="validation_steps",
            description="The number of steps between validation checks for the HF Trainer arguments.",
        ),
    ] = 15

    pretrained_model: Annotated[
        str,
        Field(
            title="pretrained_model",
            description="Pretrained model to use for fine tuning. Uses default of TinyLlama.",
        ),
    ] = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
