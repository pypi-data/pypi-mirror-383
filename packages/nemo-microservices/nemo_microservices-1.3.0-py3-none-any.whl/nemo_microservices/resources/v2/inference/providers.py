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

from typing import Optional

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.inference import (
    ModelProviderStatus,
    provider_list_params,
    provider_create_params,
    provider_update_params,
    provider_list_namespace_params,
)
from ....types.v2.inference.model_provider import ModelProvider
from ....types.v2.inference.model_provider_status import ModelProviderStatus
from ....types.v2.inference.provider_list_response import ProviderListResponse
from ....types.v2.inference.provider_list_namespace_response import ProviderListNamespaceResponse

__all__ = ["ProvidersResource", "AsyncProvidersResource"]


class ProvidersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProvidersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return ProvidersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProvidersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return ProvidersResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        host_url: str,
        name: str,
        api_key: str | Omit = omit,
        api_key_id: str | Omit = omit,
        description: str | Omit = omit,
        enabled_models: SequenceNotStr[str] | Omit = omit,
        namespace: str | Omit = omit,
        project: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelProvider:
        """
        Create a new model provider.

        Args:
          host_url: The network endpoint URL for the model provider

          name: Name of the model provider

          api_key: The API key value itself. Will be stored in Secrets service. Mutually exclusive
              with api_key_id.

          api_key_id: Reference to the API key stored in Secrets service. Mutually exclusive with
              api_key.

          description: Optional description of the model provider

          enabled_models: Optional list of specific models to enable from this provider

          namespace: The namespace of the model provider

          project: The URN of the project associated with this model provider

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v2/inference/providers",
            body=maybe_transform(
                {
                    "host_url": host_url,
                    "name": name,
                    "api_key": api_key,
                    "api_key_id": api_key_id,
                    "description": description,
                    "enabled_models": enabled_models,
                    "namespace": namespace,
                    "project": project,
                },
                provider_create_params.ProviderCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelProvider,
        )

    def retrieve(
        self,
        provider_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelProvider:
        """
        Get a model provider by namespace and name.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not provider_name:
            raise ValueError(f"Expected a non-empty value for `provider_name` but received {provider_name!r}")
        return self._get(
            f"/v2/inference/providers/{namespace}/{provider_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelProvider,
        )

    def update(
        self,
        provider_name: str,
        *,
        namespace: str,
        host_url: str,
        api_key: str | Omit = omit,
        api_key_id: str | Omit = omit,
        description: str | Omit = omit,
        enabled_models: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelProvider:
        """
        Create or update a model provider.

        Args:
          host_url: The network endpoint URL for the model provider

          api_key: The API key value itself. Will be stored in Secrets service. Mutually exclusive
              with api_key_id.

          api_key_id: Reference to the API key stored in Secrets service. Mutually exclusive with
              api_key.

          description: Optional description of the model provider

          enabled_models: Optional list of specific models to enable from this provider

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not provider_name:
            raise ValueError(f"Expected a non-empty value for `provider_name` but received {provider_name!r}")
        return self._put(
            f"/v2/inference/providers/{namespace}/{provider_name}",
            body=maybe_transform(
                {
                    "host_url": host_url,
                    "api_key": api_key,
                    "api_key_id": api_key_id,
                    "description": description,
                    "enabled_models": enabled_models,
                },
                provider_update_params.ProviderUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelProvider,
        )

    def list(
        self,
        *,
        models: Optional[SequenceNotStr[str]] | Omit = omit,
        namespace: Optional[str] | Omit = omit,
        project: Optional[str] | Omit = omit,
        status: Optional[ModelProviderStatus] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProviderListResponse:
        """List model providers with optional filtering.

        Supports filter parameters for
        either status (to list healthy ModelProviders) or models (to discover
        ModelProviders based on the models they're advertising).

        Args:
          models: Filter by models

          namespace: Filter by namespace

          project: Filter by project URN

          status: Status enum for ModelProvider objects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v2/inference/providers",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "models": models,
                        "namespace": namespace,
                        "project": project,
                        "status": status,
                    },
                    provider_list_params.ProviderListParams,
                ),
            ),
            cast_to=ProviderListResponse,
        )

    def delete(
        self,
        provider_name: str,
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
        Delete a model provider by namespace and name.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not provider_name:
            raise ValueError(f"Expected a non-empty value for `provider_name` but received {provider_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v2/inference/providers/{namespace}/{provider_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def list_namespace(
        self,
        namespace: str,
        *,
        models: Optional[SequenceNotStr[str]] | Omit = omit,
        project: Optional[str] | Omit = omit,
        status: Optional[ModelProviderStatus] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProviderListNamespaceResponse:
        """
        List model providers for a specific namespace.

        Args:
          models: Filter by models

          project: Filter by project URN

          status: Status enum for ModelProvider objects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        return self._get(
            f"/v2/inference/providers/{namespace}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "models": models,
                        "project": project,
                        "status": status,
                    },
                    provider_list_namespace_params.ProviderListNamespaceParams,
                ),
            ),
            cast_to=ProviderListNamespaceResponse,
        )


class AsyncProvidersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProvidersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncProvidersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProvidersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncProvidersResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        host_url: str,
        name: str,
        api_key: str | Omit = omit,
        api_key_id: str | Omit = omit,
        description: str | Omit = omit,
        enabled_models: SequenceNotStr[str] | Omit = omit,
        namespace: str | Omit = omit,
        project: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelProvider:
        """
        Create a new model provider.

        Args:
          host_url: The network endpoint URL for the model provider

          name: Name of the model provider

          api_key: The API key value itself. Will be stored in Secrets service. Mutually exclusive
              with api_key_id.

          api_key_id: Reference to the API key stored in Secrets service. Mutually exclusive with
              api_key.

          description: Optional description of the model provider

          enabled_models: Optional list of specific models to enable from this provider

          namespace: The namespace of the model provider

          project: The URN of the project associated with this model provider

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v2/inference/providers",
            body=await async_maybe_transform(
                {
                    "host_url": host_url,
                    "name": name,
                    "api_key": api_key,
                    "api_key_id": api_key_id,
                    "description": description,
                    "enabled_models": enabled_models,
                    "namespace": namespace,
                    "project": project,
                },
                provider_create_params.ProviderCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelProvider,
        )

    async def retrieve(
        self,
        provider_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelProvider:
        """
        Get a model provider by namespace and name.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not provider_name:
            raise ValueError(f"Expected a non-empty value for `provider_name` but received {provider_name!r}")
        return await self._get(
            f"/v2/inference/providers/{namespace}/{provider_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelProvider,
        )

    async def update(
        self,
        provider_name: str,
        *,
        namespace: str,
        host_url: str,
        api_key: str | Omit = omit,
        api_key_id: str | Omit = omit,
        description: str | Omit = omit,
        enabled_models: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelProvider:
        """
        Create or update a model provider.

        Args:
          host_url: The network endpoint URL for the model provider

          api_key: The API key value itself. Will be stored in Secrets service. Mutually exclusive
              with api_key_id.

          api_key_id: Reference to the API key stored in Secrets service. Mutually exclusive with
              api_key.

          description: Optional description of the model provider

          enabled_models: Optional list of specific models to enable from this provider

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not provider_name:
            raise ValueError(f"Expected a non-empty value for `provider_name` but received {provider_name!r}")
        return await self._put(
            f"/v2/inference/providers/{namespace}/{provider_name}",
            body=await async_maybe_transform(
                {
                    "host_url": host_url,
                    "api_key": api_key,
                    "api_key_id": api_key_id,
                    "description": description,
                    "enabled_models": enabled_models,
                },
                provider_update_params.ProviderUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelProvider,
        )

    async def list(
        self,
        *,
        models: Optional[SequenceNotStr[str]] | Omit = omit,
        namespace: Optional[str] | Omit = omit,
        project: Optional[str] | Omit = omit,
        status: Optional[ModelProviderStatus] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProviderListResponse:
        """List model providers with optional filtering.

        Supports filter parameters for
        either status (to list healthy ModelProviders) or models (to discover
        ModelProviders based on the models they're advertising).

        Args:
          models: Filter by models

          namespace: Filter by namespace

          project: Filter by project URN

          status: Status enum for ModelProvider objects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v2/inference/providers",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "models": models,
                        "namespace": namespace,
                        "project": project,
                        "status": status,
                    },
                    provider_list_params.ProviderListParams,
                ),
            ),
            cast_to=ProviderListResponse,
        )

    async def delete(
        self,
        provider_name: str,
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
        Delete a model provider by namespace and name.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not provider_name:
            raise ValueError(f"Expected a non-empty value for `provider_name` but received {provider_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v2/inference/providers/{namespace}/{provider_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def list_namespace(
        self,
        namespace: str,
        *,
        models: Optional[SequenceNotStr[str]] | Omit = omit,
        project: Optional[str] | Omit = omit,
        status: Optional[ModelProviderStatus] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProviderListNamespaceResponse:
        """
        List model providers for a specific namespace.

        Args:
          models: Filter by models

          project: Filter by project URN

          status: Status enum for ModelProvider objects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        return await self._get(
            f"/v2/inference/providers/{namespace}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "models": models,
                        "project": project,
                        "status": status,
                    },
                    provider_list_namespace_params.ProviderListNamespaceParams,
                ),
            ),
            cast_to=ProviderListNamespaceResponse,
        )


class ProvidersResourceWithRawResponse:
    def __init__(self, providers: ProvidersResource) -> None:
        self._providers = providers

        self.create = to_raw_response_wrapper(
            providers.create,
        )
        self.retrieve = to_raw_response_wrapper(
            providers.retrieve,
        )
        self.update = to_raw_response_wrapper(
            providers.update,
        )
        self.list = to_raw_response_wrapper(
            providers.list,
        )
        self.delete = to_raw_response_wrapper(
            providers.delete,
        )
        self.list_namespace = to_raw_response_wrapper(
            providers.list_namespace,
        )


class AsyncProvidersResourceWithRawResponse:
    def __init__(self, providers: AsyncProvidersResource) -> None:
        self._providers = providers

        self.create = async_to_raw_response_wrapper(
            providers.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            providers.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            providers.update,
        )
        self.list = async_to_raw_response_wrapper(
            providers.list,
        )
        self.delete = async_to_raw_response_wrapper(
            providers.delete,
        )
        self.list_namespace = async_to_raw_response_wrapper(
            providers.list_namespace,
        )


class ProvidersResourceWithStreamingResponse:
    def __init__(self, providers: ProvidersResource) -> None:
        self._providers = providers

        self.create = to_streamed_response_wrapper(
            providers.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            providers.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            providers.update,
        )
        self.list = to_streamed_response_wrapper(
            providers.list,
        )
        self.delete = to_streamed_response_wrapper(
            providers.delete,
        )
        self.list_namespace = to_streamed_response_wrapper(
            providers.list_namespace,
        )


class AsyncProvidersResourceWithStreamingResponse:
    def __init__(self, providers: AsyncProvidersResource) -> None:
        self._providers = providers

        self.create = async_to_streamed_response_wrapper(
            providers.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            providers.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            providers.update,
        )
        self.list = async_to_streamed_response_wrapper(
            providers.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            providers.delete,
        )
        self.list_namespace = async_to_streamed_response_wrapper(
            providers.list_namespace,
        )
