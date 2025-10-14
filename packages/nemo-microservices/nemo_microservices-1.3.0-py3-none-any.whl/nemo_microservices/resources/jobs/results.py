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

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    to_custom_raw_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from ...types.jobs import PlatformJobSortField, result_list_params, result_create_params
from ..._base_client import make_request_options
from ...types.jobs.platform_job_result import PlatformJobResult
from ...types.shared.file_storage_type import FileStorageType
from ...types.jobs.platform_job_sort_field import PlatformJobSortField
from ...types.jobs.platform_job_list_result_response import PlatformJobListResultResponse

__all__ = ["ResultsResource", "AsyncResultsResource"]


class ResultsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ResultsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return ResultsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ResultsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return ResultsResourceWithStreamingResponse(self)

    def create(
        self,
        result_name: str,
        *,
        job_id: str,
        artifact_storage_type: FileStorageType,
        artifact_url: str,
        namespace: str,
        project: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobResult:
        """
        Create a new result for a job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not result_name:
            raise ValueError(f"Expected a non-empty value for `result_name` but received {result_name!r}")
        return self._post(
            f"/v1/jobs/{job_id}/results/{result_name}",
            body=maybe_transform(
                {
                    "artifact_storage_type": artifact_storage_type,
                    "artifact_url": artifact_url,
                    "namespace": namespace,
                    "project": project,
                },
                result_create_params.ResultCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobResult,
        )

    def retrieve(
        self,
        result_name: str,
        *,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobResult:
        """
        Get Job Result

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not result_name:
            raise ValueError(f"Expected a non-empty value for `result_name` but received {result_name!r}")
        return self._get(
            f"/v1/jobs/{job_id}/results/{result_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobResult,
        )

    def list(
        self,
        job_id: str,
        *,
        sort: PlatformJobSortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobListResultResponse:
        """List Job Results

        Args:
          sort: The field to sort by.

        To sort in decreasing order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._get(
            f"/v1/jobs/{job_id}/results",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"sort": sort}, result_list_params.ResultListParams),
            ),
            cast_to=PlatformJobListResultResponse,
        )

    def download(
        self,
        result_name: str,
        *,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BinaryAPIResponse:
        """
        Download Job Result

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not result_name:
            raise ValueError(f"Expected a non-empty value for `result_name` but received {result_name!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return self._get(
            f"/v1/jobs/{job_id}/results/{result_name}/download",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )


class AsyncResultsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncResultsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncResultsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncResultsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncResultsResourceWithStreamingResponse(self)

    async def create(
        self,
        result_name: str,
        *,
        job_id: str,
        artifact_storage_type: FileStorageType,
        artifact_url: str,
        namespace: str,
        project: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobResult:
        """
        Create a new result for a job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not result_name:
            raise ValueError(f"Expected a non-empty value for `result_name` but received {result_name!r}")
        return await self._post(
            f"/v1/jobs/{job_id}/results/{result_name}",
            body=await async_maybe_transform(
                {
                    "artifact_storage_type": artifact_storage_type,
                    "artifact_url": artifact_url,
                    "namespace": namespace,
                    "project": project,
                },
                result_create_params.ResultCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobResult,
        )

    async def retrieve(
        self,
        result_name: str,
        *,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobResult:
        """
        Get Job Result

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not result_name:
            raise ValueError(f"Expected a non-empty value for `result_name` but received {result_name!r}")
        return await self._get(
            f"/v1/jobs/{job_id}/results/{result_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobResult,
        )

    async def list(
        self,
        job_id: str,
        *,
        sort: PlatformJobSortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobListResultResponse:
        """List Job Results

        Args:
          sort: The field to sort by.

        To sort in decreasing order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._get(
            f"/v1/jobs/{job_id}/results",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"sort": sort}, result_list_params.ResultListParams),
            ),
            cast_to=PlatformJobListResultResponse,
        )

    async def download(
        self,
        result_name: str,
        *,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncBinaryAPIResponse:
        """
        Download Job Result

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not result_name:
            raise ValueError(f"Expected a non-empty value for `result_name` but received {result_name!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return await self._get(
            f"/v1/jobs/{job_id}/results/{result_name}/download",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )


class ResultsResourceWithRawResponse:
    def __init__(self, results: ResultsResource) -> None:
        self._results = results

        self.create = to_raw_response_wrapper(
            results.create,
        )
        self.retrieve = to_raw_response_wrapper(
            results.retrieve,
        )
        self.list = to_raw_response_wrapper(
            results.list,
        )
        self.download = to_custom_raw_response_wrapper(
            results.download,
            BinaryAPIResponse,
        )


class AsyncResultsResourceWithRawResponse:
    def __init__(self, results: AsyncResultsResource) -> None:
        self._results = results

        self.create = async_to_raw_response_wrapper(
            results.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            results.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            results.list,
        )
        self.download = async_to_custom_raw_response_wrapper(
            results.download,
            AsyncBinaryAPIResponse,
        )


class ResultsResourceWithStreamingResponse:
    def __init__(self, results: ResultsResource) -> None:
        self._results = results

        self.create = to_streamed_response_wrapper(
            results.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            results.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            results.list,
        )
        self.download = to_custom_streamed_response_wrapper(
            results.download,
            StreamedBinaryAPIResponse,
        )


class AsyncResultsResourceWithStreamingResponse:
    def __init__(self, results: AsyncResultsResource) -> None:
        self._results = results

        self.create = async_to_streamed_response_wrapper(
            results.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            results.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            results.list,
        )
        self.download = async_to_custom_streamed_response_wrapper(
            results.download,
            AsyncStreamedBinaryAPIResponse,
        )
