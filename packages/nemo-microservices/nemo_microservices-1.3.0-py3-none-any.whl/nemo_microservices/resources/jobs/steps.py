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

from typing import Dict

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import SyncDefaultPagination, AsyncDefaultPagination
from ...types.jobs import (
    PlatformJobStatus,
    PlatformJobSortField,
    step_list_params,
    step_update_status_params,
    step_update_status_details_params,
)
from ..._base_client import AsyncPaginator, make_request_options
from ...types.jobs.platform_job_step import PlatformJobStep
from ...types.jobs.platform_job_status import PlatformJobStatus
from ...types.jobs.platform_job_sort_field import PlatformJobSortField
from ...types.jobs.platform_job_step_with_context import PlatformJobStepWithContext
from ...types.jobs.platform_job_steps_list_filter_param import PlatformJobStepsListFilterParam

__all__ = ["StepsResource", "AsyncStepsResource"]


class StepsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StepsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return StepsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StepsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return StepsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        step_name: str,
        *,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobStep:
        """
        Get Job Step

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not step_name:
            raise ValueError(f"Expected a non-empty value for `step_name` but received {step_name!r}")
        return self._get(
            f"/v1/jobs/{job_id}/steps/{step_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobStep,
        )

    def list(
        self,
        job_id: str,
        *,
        filter: PlatformJobStepsListFilterParam | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: PlatformJobSortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncDefaultPagination[PlatformJobStepWithContext]:
        """
        List job steps with pagination and filtering.

        Args:
          filter: Filter steps on various criteria.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in decreasing order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._get_api_list(
            f"/v1/jobs/{job_id}/steps",
            page=SyncDefaultPagination[PlatformJobStepWithContext],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    step_list_params.StepListParams,
                ),
            ),
            model=PlatformJobStepWithContext,
        )

    def update_status(
        self,
        step_name: str,
        *,
        job_id: str,
        status: PlatformJobStatus,
        error_details: Dict[str, object] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobStep:
        """
        Update Job Step Status

        Args:
          status: Enumeration of possible job statuses.

              This enum represents the various states a job can be in during its lifecycle,
              from creation to a terminal state.

          error_details: Optional error details related to the status update.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not step_name:
            raise ValueError(f"Expected a non-empty value for `step_name` but received {step_name!r}")
        return self._patch(
            f"/v1/jobs/{job_id}/steps/{step_name}/status",
            body=maybe_transform(
                {
                    "status": status,
                    "error_details": error_details,
                },
                step_update_status_params.StepUpdateStatusParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobStep,
        )

    def update_status_details(
        self,
        step_name: str,
        *,
        job_id: str,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Update Step Status Details

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not step_name:
            raise ValueError(f"Expected a non-empty value for `step_name` but received {step_name!r}")
        return self._patch(
            f"/v1/jobs/{job_id}/steps/{step_name}/status-details",
            body=maybe_transform(body, step_update_status_details_params.StepUpdateStatusDetailsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncStepsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStepsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncStepsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStepsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncStepsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        step_name: str,
        *,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobStep:
        """
        Get Job Step

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not step_name:
            raise ValueError(f"Expected a non-empty value for `step_name` but received {step_name!r}")
        return await self._get(
            f"/v1/jobs/{job_id}/steps/{step_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobStep,
        )

    def list(
        self,
        job_id: str,
        *,
        filter: PlatformJobStepsListFilterParam | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: PlatformJobSortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[PlatformJobStepWithContext, AsyncDefaultPagination[PlatformJobStepWithContext]]:
        """
        List job steps with pagination and filtering.

        Args:
          filter: Filter steps on various criteria.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in decreasing order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._get_api_list(
            f"/v1/jobs/{job_id}/steps",
            page=AsyncDefaultPagination[PlatformJobStepWithContext],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    step_list_params.StepListParams,
                ),
            ),
            model=PlatformJobStepWithContext,
        )

    async def update_status(
        self,
        step_name: str,
        *,
        job_id: str,
        status: PlatformJobStatus,
        error_details: Dict[str, object] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobStep:
        """
        Update Job Step Status

        Args:
          status: Enumeration of possible job statuses.

              This enum represents the various states a job can be in during its lifecycle,
              from creation to a terminal state.

          error_details: Optional error details related to the status update.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not step_name:
            raise ValueError(f"Expected a non-empty value for `step_name` but received {step_name!r}")
        return await self._patch(
            f"/v1/jobs/{job_id}/steps/{step_name}/status",
            body=await async_maybe_transform(
                {
                    "status": status,
                    "error_details": error_details,
                },
                step_update_status_params.StepUpdateStatusParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobStep,
        )

    async def update_status_details(
        self,
        step_name: str,
        *,
        job_id: str,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Update Step Status Details

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not step_name:
            raise ValueError(f"Expected a non-empty value for `step_name` but received {step_name!r}")
        return await self._patch(
            f"/v1/jobs/{job_id}/steps/{step_name}/status-details",
            body=await async_maybe_transform(body, step_update_status_details_params.StepUpdateStatusDetailsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class StepsResourceWithRawResponse:
    def __init__(self, steps: StepsResource) -> None:
        self._steps = steps

        self.retrieve = to_raw_response_wrapper(
            steps.retrieve,
        )
        self.list = to_raw_response_wrapper(
            steps.list,
        )
        self.update_status = to_raw_response_wrapper(
            steps.update_status,
        )
        self.update_status_details = to_raw_response_wrapper(
            steps.update_status_details,
        )


class AsyncStepsResourceWithRawResponse:
    def __init__(self, steps: AsyncStepsResource) -> None:
        self._steps = steps

        self.retrieve = async_to_raw_response_wrapper(
            steps.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            steps.list,
        )
        self.update_status = async_to_raw_response_wrapper(
            steps.update_status,
        )
        self.update_status_details = async_to_raw_response_wrapper(
            steps.update_status_details,
        )


class StepsResourceWithStreamingResponse:
    def __init__(self, steps: StepsResource) -> None:
        self._steps = steps

        self.retrieve = to_streamed_response_wrapper(
            steps.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            steps.list,
        )
        self.update_status = to_streamed_response_wrapper(
            steps.update_status,
        )
        self.update_status_details = to_streamed_response_wrapper(
            steps.update_status_details,
        )


class AsyncStepsResourceWithStreamingResponse:
    def __init__(self, steps: AsyncStepsResource) -> None:
        self._steps = steps

        self.retrieve = async_to_streamed_response_wrapper(
            steps.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            steps.list,
        )
        self.update_status = async_to_streamed_response_wrapper(
            steps.update_status,
        )
        self.update_status_details = async_to_streamed_response_wrapper(
            steps.update_status_details,
        )
