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

from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .audit.audit import (
    AuditResource,
    AsyncAuditResource,
    AuditResourceWithRawResponse,
    AsyncAuditResourceWithRawResponse,
    AuditResourceWithStreamingResponse,
    AsyncAuditResourceWithStreamingResponse,
)
from .safe_synthesizer.safe_synthesizer import (
    SafeSynthesizerResource,
    AsyncSafeSynthesizerResource,
    SafeSynthesizerResourceWithRawResponse,
    AsyncSafeSynthesizerResourceWithRawResponse,
    SafeSynthesizerResourceWithStreamingResponse,
    AsyncSafeSynthesizerResourceWithStreamingResponse,
)

__all__ = ["BetaResource", "AsyncBetaResource"]


class BetaResource(SyncAPIResource):
    @cached_property
    def audit(self) -> AuditResource:
        return AuditResource(self._client)

    @cached_property
    def safe_synthesizer(self) -> SafeSynthesizerResource:
        return SafeSynthesizerResource(self._client)

    @cached_property
    def with_raw_response(self) -> BetaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return BetaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BetaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return BetaResourceWithStreamingResponse(self)


class AsyncBetaResource(AsyncAPIResource):
    @cached_property
    def audit(self) -> AsyncAuditResource:
        return AsyncAuditResource(self._client)

    @cached_property
    def safe_synthesizer(self) -> AsyncSafeSynthesizerResource:
        return AsyncSafeSynthesizerResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncBetaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncBetaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBetaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncBetaResourceWithStreamingResponse(self)


class BetaResourceWithRawResponse:
    def __init__(self, beta: BetaResource) -> None:
        self._beta = beta

    @cached_property
    def audit(self) -> AuditResourceWithRawResponse:
        return AuditResourceWithRawResponse(self._beta.audit)

    @cached_property
    def safe_synthesizer(self) -> SafeSynthesizerResourceWithRawResponse:
        return SafeSynthesizerResourceWithRawResponse(self._beta.safe_synthesizer)


class AsyncBetaResourceWithRawResponse:
    def __init__(self, beta: AsyncBetaResource) -> None:
        self._beta = beta

    @cached_property
    def audit(self) -> AsyncAuditResourceWithRawResponse:
        return AsyncAuditResourceWithRawResponse(self._beta.audit)

    @cached_property
    def safe_synthesizer(self) -> AsyncSafeSynthesizerResourceWithRawResponse:
        return AsyncSafeSynthesizerResourceWithRawResponse(self._beta.safe_synthesizer)


class BetaResourceWithStreamingResponse:
    def __init__(self, beta: BetaResource) -> None:
        self._beta = beta

    @cached_property
    def audit(self) -> AuditResourceWithStreamingResponse:
        return AuditResourceWithStreamingResponse(self._beta.audit)

    @cached_property
    def safe_synthesizer(self) -> SafeSynthesizerResourceWithStreamingResponse:
        return SafeSynthesizerResourceWithStreamingResponse(self._beta.safe_synthesizer)


class AsyncBetaResourceWithStreamingResponse:
    def __init__(self, beta: AsyncBetaResource) -> None:
        self._beta = beta

    @cached_property
    def audit(self) -> AsyncAuditResourceWithStreamingResponse:
        return AsyncAuditResourceWithStreamingResponse(self._beta.audit)

    @cached_property
    def safe_synthesizer(self) -> AsyncSafeSynthesizerResourceWithStreamingResponse:
        return AsyncSafeSynthesizerResourceWithStreamingResponse(self._beta.safe_synthesizer)
