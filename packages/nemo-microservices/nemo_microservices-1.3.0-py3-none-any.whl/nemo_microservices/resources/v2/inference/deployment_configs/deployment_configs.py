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

from .versions import (
    VersionsResource,
    AsyncVersionsResource,
    VersionsResourceWithRawResponse,
    AsyncVersionsResourceWithRawResponse,
    VersionsResourceWithStreamingResponse,
    AsyncVersionsResourceWithStreamingResponse,
)
from ....._types import Body, Query, Headers, NoneType, NotGiven, not_given
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options

__all__ = ["DeploymentConfigsResource", "AsyncDeploymentConfigsResource"]


class DeploymentConfigsResource(SyncAPIResource):
    @cached_property
    def versions(self) -> VersionsResource:
        return VersionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> DeploymentConfigsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return DeploymentConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeploymentConfigsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return DeploymentConfigsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Create ModelDeploymentConfig endpoint - returns a simple hello world response
        for now.
        """
        return self._post(
            "/v2/inference/deployment-configs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def retrieve(
        self,
        deployment_config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Get Latest ModelDeploymentConfig Version endpoint - returns a simple hello world
        response for now.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_config_name:
            raise ValueError(
                f"Expected a non-empty value for `deployment_config_name` but received {deployment_config_name!r}"
            )
        return self._get(
            f"/v2/inference/deployment-configs/{namespace}/{deployment_config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def update(
        self,
        deployment_config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Update ModelDeploymentConfig endpoint - returns a simple hello world response
        for now.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_config_name:
            raise ValueError(
                f"Expected a non-empty value for `deployment_config_name` but received {deployment_config_name!r}"
            )
        return self._post(
            f"/v2/inference/deployment-configs/{namespace}/{deployment_config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        List ModelDeploymentConfigs endpoint - returns a simple hello world response for
        now.
        """
        return self._get(
            "/v2/inference/deployment-configs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def delete(
        self,
        deployment_config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete All ModelDeploymentConfig Versions endpoint - returns a simple hello
        world response for now.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_config_name:
            raise ValueError(
                f"Expected a non-empty value for `deployment_config_name` but received {deployment_config_name!r}"
            )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v2/inference/deployment-configs/{namespace}/{deployment_config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def list_namespace(
        self,
        namespace: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        List ModelDeploymentConfigs By Namespace endpoint - returns a simple hello world
        response for now.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        return self._get(
            f"/v2/inference/deployment-configs/{namespace}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncDeploymentConfigsResource(AsyncAPIResource):
    @cached_property
    def versions(self) -> AsyncVersionsResource:
        return AsyncVersionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDeploymentConfigsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncDeploymentConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeploymentConfigsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncDeploymentConfigsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Create ModelDeploymentConfig endpoint - returns a simple hello world response
        for now.
        """
        return await self._post(
            "/v2/inference/deployment-configs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def retrieve(
        self,
        deployment_config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Get Latest ModelDeploymentConfig Version endpoint - returns a simple hello world
        response for now.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_config_name:
            raise ValueError(
                f"Expected a non-empty value for `deployment_config_name` but received {deployment_config_name!r}"
            )
        return await self._get(
            f"/v2/inference/deployment-configs/{namespace}/{deployment_config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def update(
        self,
        deployment_config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Update ModelDeploymentConfig endpoint - returns a simple hello world response
        for now.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_config_name:
            raise ValueError(
                f"Expected a non-empty value for `deployment_config_name` but received {deployment_config_name!r}"
            )
        return await self._post(
            f"/v2/inference/deployment-configs/{namespace}/{deployment_config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        List ModelDeploymentConfigs endpoint - returns a simple hello world response for
        now.
        """
        return await self._get(
            "/v2/inference/deployment-configs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def delete(
        self,
        deployment_config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete All ModelDeploymentConfig Versions endpoint - returns a simple hello
        world response for now.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_config_name:
            raise ValueError(
                f"Expected a non-empty value for `deployment_config_name` but received {deployment_config_name!r}"
            )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v2/inference/deployment-configs/{namespace}/{deployment_config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def list_namespace(
        self,
        namespace: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        List ModelDeploymentConfigs By Namespace endpoint - returns a simple hello world
        response for now.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        return await self._get(
            f"/v2/inference/deployment-configs/{namespace}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class DeploymentConfigsResourceWithRawResponse:
    def __init__(self, deployment_configs: DeploymentConfigsResource) -> None:
        self._deployment_configs = deployment_configs

        self.create = to_raw_response_wrapper(
            deployment_configs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            deployment_configs.retrieve,
        )
        self.update = to_raw_response_wrapper(
            deployment_configs.update,
        )
        self.list = to_raw_response_wrapper(
            deployment_configs.list,
        )
        self.delete = to_raw_response_wrapper(
            deployment_configs.delete,
        )
        self.list_namespace = to_raw_response_wrapper(
            deployment_configs.list_namespace,
        )

    @cached_property
    def versions(self) -> VersionsResourceWithRawResponse:
        return VersionsResourceWithRawResponse(self._deployment_configs.versions)


class AsyncDeploymentConfigsResourceWithRawResponse:
    def __init__(self, deployment_configs: AsyncDeploymentConfigsResource) -> None:
        self._deployment_configs = deployment_configs

        self.create = async_to_raw_response_wrapper(
            deployment_configs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            deployment_configs.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            deployment_configs.update,
        )
        self.list = async_to_raw_response_wrapper(
            deployment_configs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            deployment_configs.delete,
        )
        self.list_namespace = async_to_raw_response_wrapper(
            deployment_configs.list_namespace,
        )

    @cached_property
    def versions(self) -> AsyncVersionsResourceWithRawResponse:
        return AsyncVersionsResourceWithRawResponse(self._deployment_configs.versions)


class DeploymentConfigsResourceWithStreamingResponse:
    def __init__(self, deployment_configs: DeploymentConfigsResource) -> None:
        self._deployment_configs = deployment_configs

        self.create = to_streamed_response_wrapper(
            deployment_configs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            deployment_configs.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            deployment_configs.update,
        )
        self.list = to_streamed_response_wrapper(
            deployment_configs.list,
        )
        self.delete = to_streamed_response_wrapper(
            deployment_configs.delete,
        )
        self.list_namespace = to_streamed_response_wrapper(
            deployment_configs.list_namespace,
        )

    @cached_property
    def versions(self) -> VersionsResourceWithStreamingResponse:
        return VersionsResourceWithStreamingResponse(self._deployment_configs.versions)


class AsyncDeploymentConfigsResourceWithStreamingResponse:
    def __init__(self, deployment_configs: AsyncDeploymentConfigsResource) -> None:
        self._deployment_configs = deployment_configs

        self.create = async_to_streamed_response_wrapper(
            deployment_configs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            deployment_configs.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            deployment_configs.update,
        )
        self.list = async_to_streamed_response_wrapper(
            deployment_configs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            deployment_configs.delete,
        )
        self.list_namespace = async_to_streamed_response_wrapper(
            deployment_configs.list_namespace,
        )

    @cached_property
    def versions(self) -> AsyncVersionsResourceWithStreamingResponse:
        return AsyncVersionsResourceWithStreamingResponse(self._deployment_configs.versions)
