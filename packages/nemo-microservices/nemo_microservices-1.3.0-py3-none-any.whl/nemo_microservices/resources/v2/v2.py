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

from .models import (
    ModelsResource,
    AsyncModelsResource,
    ModelsResourceWithRawResponse,
    AsyncModelsResourceWithRawResponse,
    ModelsResourceWithStreamingResponse,
    AsyncModelsResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .inference.inference import (
    InferenceResource,
    AsyncInferenceResource,
    InferenceResourceWithRawResponse,
    AsyncInferenceResourceWithRawResponse,
    InferenceResourceWithStreamingResponse,
    AsyncInferenceResourceWithStreamingResponse,
)
from .evaluation.evaluation import (
    EvaluationResource,
    AsyncEvaluationResource,
    EvaluationResourceWithRawResponse,
    AsyncEvaluationResourceWithRawResponse,
    EvaluationResourceWithStreamingResponse,
    AsyncEvaluationResourceWithStreamingResponse,
)

__all__ = ["V2Resource", "AsyncV2Resource"]


class V2Resource(SyncAPIResource):
    @cached_property
    def evaluation(self) -> EvaluationResource:
        return EvaluationResource(self._client)

    @cached_property
    def models(self) -> ModelsResource:
        return ModelsResource(self._client)

    @cached_property
    def inference(self) -> InferenceResource:
        return InferenceResource(self._client)

    @cached_property
    def with_raw_response(self) -> V2ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return V2ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> V2ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return V2ResourceWithStreamingResponse(self)


class AsyncV2Resource(AsyncAPIResource):
    @cached_property
    def evaluation(self) -> AsyncEvaluationResource:
        return AsyncEvaluationResource(self._client)

    @cached_property
    def models(self) -> AsyncModelsResource:
        return AsyncModelsResource(self._client)

    @cached_property
    def inference(self) -> AsyncInferenceResource:
        return AsyncInferenceResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncV2ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncV2ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncV2ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncV2ResourceWithStreamingResponse(self)


class V2ResourceWithRawResponse:
    def __init__(self, v2: V2Resource) -> None:
        self._v2 = v2

    @cached_property
    def evaluation(self) -> EvaluationResourceWithRawResponse:
        return EvaluationResourceWithRawResponse(self._v2.evaluation)

    @cached_property
    def models(self) -> ModelsResourceWithRawResponse:
        return ModelsResourceWithRawResponse(self._v2.models)

    @cached_property
    def inference(self) -> InferenceResourceWithRawResponse:
        return InferenceResourceWithRawResponse(self._v2.inference)


class AsyncV2ResourceWithRawResponse:
    def __init__(self, v2: AsyncV2Resource) -> None:
        self._v2 = v2

    @cached_property
    def evaluation(self) -> AsyncEvaluationResourceWithRawResponse:
        return AsyncEvaluationResourceWithRawResponse(self._v2.evaluation)

    @cached_property
    def models(self) -> AsyncModelsResourceWithRawResponse:
        return AsyncModelsResourceWithRawResponse(self._v2.models)

    @cached_property
    def inference(self) -> AsyncInferenceResourceWithRawResponse:
        return AsyncInferenceResourceWithRawResponse(self._v2.inference)


class V2ResourceWithStreamingResponse:
    def __init__(self, v2: V2Resource) -> None:
        self._v2 = v2

    @cached_property
    def evaluation(self) -> EvaluationResourceWithStreamingResponse:
        return EvaluationResourceWithStreamingResponse(self._v2.evaluation)

    @cached_property
    def models(self) -> ModelsResourceWithStreamingResponse:
        return ModelsResourceWithStreamingResponse(self._v2.models)

    @cached_property
    def inference(self) -> InferenceResourceWithStreamingResponse:
        return InferenceResourceWithStreamingResponse(self._v2.inference)


class AsyncV2ResourceWithStreamingResponse:
    def __init__(self, v2: AsyncV2Resource) -> None:
        self._v2 = v2

    @cached_property
    def evaluation(self) -> AsyncEvaluationResourceWithStreamingResponse:
        return AsyncEvaluationResourceWithStreamingResponse(self._v2.evaluation)

    @cached_property
    def models(self) -> AsyncModelsResourceWithStreamingResponse:
        return AsyncModelsResourceWithStreamingResponse(self._v2.models)

    @cached_property
    def inference(self) -> AsyncInferenceResourceWithStreamingResponse:
        return AsyncInferenceResourceWithStreamingResponse(self._v2.inference)
