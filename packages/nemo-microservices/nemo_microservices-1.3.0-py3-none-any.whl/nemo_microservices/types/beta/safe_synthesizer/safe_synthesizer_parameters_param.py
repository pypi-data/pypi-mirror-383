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

from .data_parameters_param import DataParametersParam
from .generate_parameters_param import GenerateParametersParam
from .pii_replacer_config_param import PIIReplacerConfigParam
from .training_hyperparams_param import TrainingHyperparamsParam
from .evaluation_parameters_param import EvaluationParametersParam
from .differential_privacy_hyperparams_param import DifferentialPrivacyHyperparamsParam

__all__ = ["SafeSynthesizerParametersParam"]


class SafeSynthesizerParametersParam(TypedDict, total=False):
    data: DataParametersParam
    """
    Configuration for parameters related to how to shape or use the data being
    passed in.

    Attributes: group_training_examples_by: Column(s) to group training examples by.
    order_training_examples_by: Column to order training examples by.
    max_sequences_per_example: Maximum number of sequences per example for training.
    holdout: Amount of records to holdout for evaluation. max_holdout: Maximum
    number of records to hold out. Overrides any behavior set by holdout parameter.
    random_state: Random state for holdout split to ensure reproducibility.
    """

    enable_replace_pii: bool
    """Enable replacing PII in the data."""

    enable_synthesis: bool
    """Enable synthesizing new data by training a model."""

    evaluation: EvaluationParametersParam
    """Configuration for evaluating synthetic data quality and privacy.

    This class controls which evaluation metrics are computed and how they are
    configured. It includes privacy attack evaluations, statistical quality metrics,
    and downstream machine learning performance assessments.

    Attributes: enabled: Enable or disable evaluation. quasi_identifier_count:
    Number of quasi-identifiers to sample for privacy attacks. pii_replay_enabled:
    Enable PII Replay detection. pii_replay_entities: List of entities for PII
    Replay. If not provided, default entities will be used. pii_replay_columns: List
    of columns for PII Replay. If not provided, only entities will be used.
    mia_enabled: Enable membership inference attack evaluation for privacy
    assessment. aia_enabled: Enable attribute inference attack evaluation for
    privacy assessment. sqs_report_columns: Number of columns to include in
    statistical quality reports. sqs_report_rows: Number of rows to include in
    statistical quality reports. mandatory_columns: Columns that must be present in
    generated data.
    """

    generation: GenerateParametersParam
    """Configuration parameters for synthetic data generation.

    These parameters control how synthetic data is generated after the model is
    trained. They affect the quality, diversity, and validity of the generated
    synthetic records.

    Attributes: num_records: Number of synthetic records to generate. Maximum is
    130,000 records. temperature: Sampling temperature for controlling randomness
    (higher = more random). repetition_penalty: Penalty for token repetition (≥1.0,
    higher = less repetition). top_p: Nucleus sampling probability for token
    selection (0 < value ≤ 1). patience: Number of invalid records fraction before
    stopping. invalid_fraction_threshold: "The fraction of invalid records that will
    stop generation after the `patience` limit is reached."
    use_structured_generation: Whether to use structured generation for better
    format control.
    """

    privacy: DifferentialPrivacyHyperparamsParam
    """Hyperparameters for differential privacy during training.

    These parameters configure differential privacy (DP) training using DP-SGD
    algorithm. When enabled, they provide formal privacy guarantees by adding
    calibrated noise during training.

    Attributes: dp_enabled: Enable differential privacy training with DP-SGD
    algorithm. epsilon: Target privacy budget (ε) - lower values provide stronger
    privacy. delta: Probability of privacy failure (δ) - should be much smaller than
    1/n where n is the number of training records. per_sample_max_grad_norm: Maximum
    L2 norm for gradient clipping per sample.
    """

    replace_pii: PIIReplacerConfigParam
    """
    Configuration for PII replacer. Used to define how PII data should be detected
    and replaced in a dataset.

    Attributes: globals Global configuration options. steps: List of transformation
    steps to perform on input data.

    Methods: get_default_config: Returns a default configuration instance.
    """

    training: TrainingHyperparamsParam
    """Hyperparameters that control the training process behavior.

    This class contains all the fine-tuning hyperparameters that control how the
    model learns, including learning rates, batch sizes, LoRA configuration, and
    optimization settings. These parameters directly affect training performance and
    quality.

    Attributes: num_input_records_to_sample: Number of records the model will see
    during training. This parameter is a proxy for training time. For example, if
    its value is the same size as the input dataset, this is like training for a
    single epoch. If its value is larger, this is like training for multiple
    (possibly fractional) epochs. If its value is smaller, this is like training for
    a fraction of an epoch. Supports 'auto' where a reasonable value is chosen based
    on other config params and data. batch_size: The batch size per device for
    training. gradient_accumulation_steps: Number of update steps to accumulate the
    gradients for, before performing a backward/update pass. This technique
    increases the effective batch size that will fit into GPU memory. weight_decay:
    The weight decay to apply (if not zero) to all layers except all bias and
    LayerNorm weights in the AdamW optimizer. warmup_ratio: Ratio of total training
    steps used for a linear warmup from 0 to the learning rate. lr_scheduler: The
    scheduler type to use. See the HuggingFace documentation of `SchedulerType` for
    all possible values. learning_rate: The initial learning rate for `AdamW`
    optimizer. lora_r: The rank of the LoRA update matrices, expressed in int. Lower
    rank results in smaller update matrices with fewer trainable parameters.
    lora_alpha_over_r: The ratio of the LoRA scaling factor (alpha) to the LoRA
    rank. Empirically, this parameter works well when set to 0.5, 1, or 2.
    lora_target_modules: The list of transformer modules to apply LoRA to. Possible
    modules: 'q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj',
    'down_proj' use_unsloth: Whether to use unsloth. rope_scaling_factor: Scale the
    base LLM's context length by this factor using RoPE scaling. validation_ratio:
    The fraction of the training data that will be used for validation. The range
    should be 0 to 1. If set to 0, no validation will be performed. If set larger
    than 0, validation loss will be computed and reported throughout training.
    validation_steps: The number of steps between validation checks for the HF
    Trainer arguments. pretrained_model: Pretrained model to use for fine-tuning.
    Uses default of TinyLlama.
    """
