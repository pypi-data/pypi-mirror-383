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

from typing import Dict, Union, Optional
from typing_extensions import TypeAlias

from ..._models import BaseModel
from .sampler_type import SamplerType
from .uuid_sampler_params import UuidSamplerParams
from .scipy_sampler_params import ScipySamplerParams
from .person_sampler_params import PersonSamplerParams
from .poisson_sampler_params import PoissonSamplerParams
from .uniform_sampler_params import UniformSamplerParams
from .binomial_sampler_params import BinomialSamplerParams
from .category_sampler_params import CategorySamplerParams
from .datetime_sampler_params import DatetimeSamplerParams
from .gaussian_sampler_params import GaussianSamplerParams
from .bernoulli_sampler_params import BernoulliSamplerParams
from .time_delta_sampler_params import TimeDeltaSamplerParams
from .subcategory_sampler_params import SubcategorySamplerParams
from .bernoulli_mixture_sampler_params import BernoulliMixtureSamplerParams

__all__ = ["SamplerColumnConfig", "Params", "ConditionalParams"]

Params: TypeAlias = Union[
    SubcategorySamplerParams,
    CategorySamplerParams,
    DatetimeSamplerParams,
    PersonSamplerParams,
    TimeDeltaSamplerParams,
    UuidSamplerParams,
    BernoulliSamplerParams,
    BernoulliMixtureSamplerParams,
    BinomialSamplerParams,
    GaussianSamplerParams,
    PoissonSamplerParams,
    UniformSamplerParams,
    ScipySamplerParams,
]

ConditionalParams: TypeAlias = Union[
    SubcategorySamplerParams,
    CategorySamplerParams,
    DatetimeSamplerParams,
    PersonSamplerParams,
    TimeDeltaSamplerParams,
    UuidSamplerParams,
    BernoulliSamplerParams,
    BernoulliMixtureSamplerParams,
    BinomialSamplerParams,
    GaussianSamplerParams,
    PoissonSamplerParams,
    UniformSamplerParams,
    ScipySamplerParams,
]


class SamplerColumnConfig(BaseModel):
    name: str

    params: Params

    sampler_type: SamplerType

    conditional_params: Optional[Dict[str, ConditionalParams]] = None

    convert_to: Optional[str] = None

    drop: Optional[bool] = None
