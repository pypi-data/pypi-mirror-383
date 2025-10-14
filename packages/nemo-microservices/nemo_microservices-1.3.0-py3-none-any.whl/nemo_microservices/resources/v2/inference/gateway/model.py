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

import httpx

from ....._types import Body, Query, Headers, NotGiven, not_given
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options

__all__ = ["ModelResource", "AsyncModelResource"]


class ModelResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ModelResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return ModelResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return ModelResourceWithStreamingResponse(self)

    def delete(
        self,
        trailing_uri: str,
        *,
        namespace: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Proxy requests to model entity inference endpoints.

        This is a stub
        implementation that returns request details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        if not trailing_uri:
            raise ValueError(f"Expected a non-empty value for `trailing_uri` but received {trailing_uri!r}")
        return self._delete(
            f"/v2/inference/gateway/model/{namespace}/{model_name}/-/{trailing_uri}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get(
        self,
        trailing_uri: str,
        *,
        namespace: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Proxy requests to model entity inference endpoints.

        This is a stub
        implementation that returns request details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        if not trailing_uri:
            raise ValueError(f"Expected a non-empty value for `trailing_uri` but received {trailing_uri!r}")
        return self._get(
            f"/v2/inference/gateway/model/{namespace}/{model_name}/-/{trailing_uri}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def patch(
        self,
        trailing_uri: str,
        *,
        namespace: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Proxy requests to model entity inference endpoints.

        This is a stub
        implementation that returns request details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        if not trailing_uri:
            raise ValueError(f"Expected a non-empty value for `trailing_uri` but received {trailing_uri!r}")
        return self._patch(
            f"/v2/inference/gateway/model/{namespace}/{model_name}/-/{trailing_uri}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def post(
        self,
        trailing_uri: str,
        *,
        namespace: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Proxy requests to model entity inference endpoints.

        This is a stub
        implementation that returns request details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        if not trailing_uri:
            raise ValueError(f"Expected a non-empty value for `trailing_uri` but received {trailing_uri!r}")
        return self._post(
            f"/v2/inference/gateway/model/{namespace}/{model_name}/-/{trailing_uri}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def put(
        self,
        trailing_uri: str,
        *,
        namespace: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Proxy requests to model entity inference endpoints.

        This is a stub
        implementation that returns request details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        if not trailing_uri:
            raise ValueError(f"Expected a non-empty value for `trailing_uri` but received {trailing_uri!r}")
        return self._put(
            f"/v2/inference/gateway/model/{namespace}/{model_name}/-/{trailing_uri}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncModelResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncModelResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncModelResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncModelResourceWithStreamingResponse(self)

    async def delete(
        self,
        trailing_uri: str,
        *,
        namespace: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Proxy requests to model entity inference endpoints.

        This is a stub
        implementation that returns request details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        if not trailing_uri:
            raise ValueError(f"Expected a non-empty value for `trailing_uri` but received {trailing_uri!r}")
        return await self._delete(
            f"/v2/inference/gateway/model/{namespace}/{model_name}/-/{trailing_uri}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get(
        self,
        trailing_uri: str,
        *,
        namespace: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Proxy requests to model entity inference endpoints.

        This is a stub
        implementation that returns request details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        if not trailing_uri:
            raise ValueError(f"Expected a non-empty value for `trailing_uri` but received {trailing_uri!r}")
        return await self._get(
            f"/v2/inference/gateway/model/{namespace}/{model_name}/-/{trailing_uri}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def patch(
        self,
        trailing_uri: str,
        *,
        namespace: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Proxy requests to model entity inference endpoints.

        This is a stub
        implementation that returns request details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        if not trailing_uri:
            raise ValueError(f"Expected a non-empty value for `trailing_uri` but received {trailing_uri!r}")
        return await self._patch(
            f"/v2/inference/gateway/model/{namespace}/{model_name}/-/{trailing_uri}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def post(
        self,
        trailing_uri: str,
        *,
        namespace: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Proxy requests to model entity inference endpoints.

        This is a stub
        implementation that returns request details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        if not trailing_uri:
            raise ValueError(f"Expected a non-empty value for `trailing_uri` but received {trailing_uri!r}")
        return await self._post(
            f"/v2/inference/gateway/model/{namespace}/{model_name}/-/{trailing_uri}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def put(
        self,
        trailing_uri: str,
        *,
        namespace: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Proxy requests to model entity inference endpoints.

        This is a stub
        implementation that returns request details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        if not trailing_uri:
            raise ValueError(f"Expected a non-empty value for `trailing_uri` but received {trailing_uri!r}")
        return await self._put(
            f"/v2/inference/gateway/model/{namespace}/{model_name}/-/{trailing_uri}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class ModelResourceWithRawResponse:
    def __init__(self, model: ModelResource) -> None:
        self._model = model

        self.delete = to_raw_response_wrapper(
            model.delete,
        )
        self.get = to_raw_response_wrapper(
            model.get,
        )
        self.patch = to_raw_response_wrapper(
            model.patch,
        )
        self.post = to_raw_response_wrapper(
            model.post,
        )
        self.put = to_raw_response_wrapper(
            model.put,
        )


class AsyncModelResourceWithRawResponse:
    def __init__(self, model: AsyncModelResource) -> None:
        self._model = model

        self.delete = async_to_raw_response_wrapper(
            model.delete,
        )
        self.get = async_to_raw_response_wrapper(
            model.get,
        )
        self.patch = async_to_raw_response_wrapper(
            model.patch,
        )
        self.post = async_to_raw_response_wrapper(
            model.post,
        )
        self.put = async_to_raw_response_wrapper(
            model.put,
        )


class ModelResourceWithStreamingResponse:
    def __init__(self, model: ModelResource) -> None:
        self._model = model

        self.delete = to_streamed_response_wrapper(
            model.delete,
        )
        self.get = to_streamed_response_wrapper(
            model.get,
        )
        self.patch = to_streamed_response_wrapper(
            model.patch,
        )
        self.post = to_streamed_response_wrapper(
            model.post,
        )
        self.put = to_streamed_response_wrapper(
            model.put,
        )


class AsyncModelResourceWithStreamingResponse:
    def __init__(self, model: AsyncModelResource) -> None:
        self._model = model

        self.delete = async_to_streamed_response_wrapper(
            model.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            model.get,
        )
        self.patch = async_to_streamed_response_wrapper(
            model.patch,
        )
        self.post = async_to_streamed_response_wrapper(
            model.post,
        )
        self.put = async_to_streamed_response_wrapper(
            model.put,
        )
