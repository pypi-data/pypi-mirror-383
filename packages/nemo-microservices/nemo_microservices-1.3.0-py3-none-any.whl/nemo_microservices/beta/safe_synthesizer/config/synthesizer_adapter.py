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

from itertools import chain
from pathlib import Path
from typing import Optional, Type, TypeVar, Union

import yaml
from pydantic import Field

from ..configurator.parameters import Parameters
from ..logging_utils import get_logger
from .legacy.evaluate import (
    EvaluateModelHyperparams,
    ExtendedEvaluateModelHyperparams,
)
from .legacy.generation import (
    TabularFTGenerateParams,
    TabularFTPrivacyParams,
    TabularFTTrainingParams,
)
from .legacy.modelspec_definition import (
    GretelModelDefinition,
    ModelConfigurationWithDataSource,
)
from .legacy.pii import (
    PIIReplayParams,
    PrivacyMetricsMIAParams,
    PrivacyMetricsParams,
)
from .legacy.record_handlers import RecordHandlerConfiguration
from .legacy.training import (
    TabularFTTrainingConfig,
)
from .parameters import SafeSynthesizerParameters

__all__ = [
    "NavigatorFTModelConfig",
    "NavigatorFTRecordHandlerConfig",
    "convert_nss_to_navft",
    "convert_nss_to_navft_config",
    "load_navigator_ft_config",
]


logger = get_logger(__name__)


class NavigatorFTRecordHandlerConfig(RecordHandlerConfiguration):
    """
    Config that user provides when the model is run (record handler is executed).
    """

    params: TabularFTGenerateParams = Field(default_factory=TabularFTGenerateParams)

    def archive_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)


class NavigatorFTModelConfig(ModelConfigurationWithDataSource, TabularFTTrainingConfig):
    """
    Configuration for a NavigatorFT model run. Keeping here for ease of use.
    We can reshape this to look more like the other configs later.
    """

    generate: Optional[TabularFTGenerateParams] = Field(default_factory=TabularFTGenerateParams)
    evaluate: Optional[ExtendedEvaluateModelHyperparams] = Field(default_factory=ExtendedEvaluateModelHyperparams)
    privacy_metrics: Optional[PrivacyMetricsParams] = Field(default_factory=PrivacyMetricsParams)

    def archive_dict(self, exclude_unset: bool = True) -> dict:
        return super().archive_dict(exclude_unset)

    @property
    def model_definition(self) -> GretelModelDefinition:
        raise NotImplementedError("Not implemented")
        # return NavigatorFTDefinition()

    @classmethod
    def from_dict(cls, config: dict) -> "NavigatorFTModelConfig":
        print(config)
        return cls(**config["models"][0]["navigator_ft"])

    @classmethod
    def from_yaml(cls, file_path: Union[str, Path]) -> "NavigatorFTModelConfig":
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
        return cls.from_dict(config)


NavftConfigs = Union[
    NavigatorFTModelConfig
    | NavigatorFTRecordHandlerConfig
    | TabularFTTrainingConfig
    | TabularFTGenerateParams
    | PrivacyMetricsParams
    | TabularFTTrainingParams
    | TabularFTPrivacyParams
    | ExtendedEvaluateModelHyperparams
    | PrivacyMetricsMIAParams
    | PIIReplayParams
]
NavftType = Type[NavftConfigs]
NavftConfigT = TypeVar(
    "NavftConfigT",
    NavigatorFTModelConfig,
    NavigatorFTRecordHandlerConfig,
    TabularFTTrainingConfig,
    TabularFTGenerateParams,
    PrivacyMetricsParams,
    TabularFTTrainingParams,
    TabularFTPrivacyParams,
    ExtendedEvaluateModelHyperparams,
    PrivacyMetricsMIAParams,
    PIIReplayParams,
)


def convert_nss_to_navft(
    nss: SafeSynthesizerParameters,
    navft_types: list[NavftType],
    output_type: NavftType,
) -> NavftConfigT:
    """Convert NSSParameters to a specific NavigatorFT config type by mapping shared fields."""
    navft_fields = (getattr(t, "__pydantic_fields__").keys() for t in navft_types if hasattr(t, "__pydantic_fields__"))
    navft_fields = list(chain.from_iterable(navft_fields))
    navft_valid = [f for f in navft_fields if nss.has(f)]
    navft_none = [f for f in navft_fields if nss.get(f) is None]
    none_vals = {f: None for f in navft_none}

    nss_fields_ = [(field, nss.get(field)) for field in navft_valid]
    logger.debug(f"nss fields for {output_type.__name__}: {nss_fields_}")
    nss_vals = {}
    for name, value in nss_fields_:
        match value:
            case "auto":
                nss_vals[name] = value
            case None:
                pass
            case _:
                nss_vals[name] = value

    nss_vals = {**none_vals, **nss_vals}
    logger.debug(f"converting NSS to {output_type.__name__} with fields: {nss_vals}")
    navft = output_type(**nss_vals)
    return navft


def convert_nss_to_navft_config(nss: SafeSynthesizerParameters) -> NavigatorFTModelConfig:
    """
    Convert a SafeSynthesizerParameters object to a NavigatorFTModelConfig object by mapping shared fields.
    This function assumes that the input `nss` object contains all necessary fields to populate the
    NavigatorFTModelConfig and its nested configurations.

    The Parameters enable a `.get()` method to retrieve _nested_ values by key, which is useful for this.
    """
    ds = ["dummy"]
    mapper = {
        "group_training_examples_by": "group_training_examples_by",
        "order_training_examples_by": "order_training_examples_by",
        "max_sequences_per_example": "max_sequences_per_example",
        "pretrained_model": "pretrained_model",
        "params": convert_nss_to_navft(nss, [TabularFTTrainingParams], TabularFTTrainingParams),
        "data_config": nss.data.model_dump(),
        "data_source": ds,
        "ref_data": None,
        "generate": convert_nss_to_navft(nss, [TabularFTGenerateParams], TabularFTGenerateParams),
        "evaluate": convert_nss_to_navft(nss, [ExtendedEvaluateModelHyperparams], ExtendedEvaluateModelHyperparams),
        # these are the now DifferentialPrivacyHyperparams
        "privacy_params": convert_nss_to_navft(nss, [TabularFTPrivacyParams], TabularFTPrivacyParams),
        # these are for evals
        "privacy_metrics": convert_nss_to_navft(nss, [PrivacyMetricsParams], PrivacyMetricsParams),
        "privacy_mia": convert_nss_to_navft(nss, [PrivacyMetricsMIAParams], PrivacyMetricsMIAParams),
        "privacy_replay": convert_nss_to_navft(nss, [PIIReplayParams], PIIReplayParams),
    }

    out = {}
    for navft_param, getter in mapper.items():
        match getter:
            case str() as key:
                out[navft_param] = nss.get(key)
            case (
                TabularFTGenerateParams()
                | PrivacyMetricsParams()
                | PrivacyMetricsMIAParams()
                | PIIReplayParams()
                | EvaluateModelHyperparams()
                | ExtendedEvaluateModelHyperparams()
                | TabularFTTrainingParams()
                | TabularFTPrivacyParams()
                | TabularFTTrainingConfig()
            ):
                out[navft_param] = getter.model_dump()
            case Parameters():
                out[navft_param] = getter.model_dump()
            case None:
                out[navft_param] = None
            case list() | dict():
                out[navft_param] = getter
            case _:
                raise ValueError(f"Unknown getter type: {type(getter)}")

    return NavigatorFTModelConfig(**out)


def load_navigator_ft_config(
    config: str | dict | Path | TabularFTTrainingConfig | NavigatorFTRecordHandlerConfig,
) -> TabularFTTrainingConfig | NavigatorFTRecordHandlerConfig:
    """Load the model configuration based on a flexible input format.

    Also apply auto param updates here for local NavFT while we work on a better
    solution.

    Args:
        config: The config as a yaml path, dict, or object.

    Returns:
        The model configuration object.
    """
    if isinstance(config, (TabularFTTrainingConfig, NavigatorFTRecordHandlerConfig)):
        config = config
    elif isinstance(config, dict):
        config = NavigatorFTModelConfig.from_dict(config)
    elif isinstance(config, (str, Path)):
        config = NavigatorFTModelConfig.from_yaml(config)
    else:
        raise ValueError("A valid config must be provided.")

    return config
