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
from ...types.jobs import PlatformJobStatus, task_create_or_update_params, task_update_status_details_params
from ..._base_client import make_request_options
from ...types.jobs.platform_job_task import PlatformJobTask
from ...types.jobs.platform_job_status import PlatformJobStatus
from ...types.jobs.platform_job_list_task_response import PlatformJobListTaskResponse

__all__ = ["TasksResource", "AsyncTasksResource"]


class TasksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TasksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return TasksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TasksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return TasksResourceWithStreamingResponse(self)

    def retrieve(
        self,
        task_id: str,
        *,
        job_id: str,
        step_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobTask:
        """
        Get Job Step Task

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
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._get(
            f"/v1/jobs/{job_id}/steps/{step_name}/tasks/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobTask,
        )

    def list(
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
    ) -> PlatformJobListTaskResponse:
        """
        List Job Step Tasks

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
            f"/v1/jobs/{job_id}/steps/{step_name}/tasks",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobListTaskResponse,
        )

    def create_or_update(
        self,
        task_id: str,
        *,
        job_id: str,
        step_name: str,
        error_details: Dict[str, object] | Omit = omit,
        error_stack: str | Omit = omit,
        status: PlatformJobStatus | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobTask:
        """
        Update Job Step Task

        Args:
          status: Enumeration of possible job statuses.

              This enum represents the various states a job can be in during its lifecycle,
              from creation to a terminal state.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not step_name:
            raise ValueError(f"Expected a non-empty value for `step_name` but received {step_name!r}")
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._put(
            f"/v1/jobs/{job_id}/steps/{step_name}/tasks/{task_id}",
            body=maybe_transform(
                {
                    "error_details": error_details,
                    "error_stack": error_stack,
                    "status": status,
                },
                task_create_or_update_params.TaskCreateOrUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobTask,
        )

    def update_status_details(
        self,
        task_id: str,
        *,
        job_id: str,
        step_name: str,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Update Task Status Details

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
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._patch(
            f"/v1/jobs/{job_id}/steps/{step_name}/tasks/{task_id}/status-details",
            body=maybe_transform(body, task_update_status_details_params.TaskUpdateStatusDetailsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncTasksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTasksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncTasksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTasksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncTasksResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        task_id: str,
        *,
        job_id: str,
        step_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobTask:
        """
        Get Job Step Task

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
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._get(
            f"/v1/jobs/{job_id}/steps/{step_name}/tasks/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobTask,
        )

    async def list(
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
    ) -> PlatformJobListTaskResponse:
        """
        List Job Step Tasks

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
            f"/v1/jobs/{job_id}/steps/{step_name}/tasks",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobListTaskResponse,
        )

    async def create_or_update(
        self,
        task_id: str,
        *,
        job_id: str,
        step_name: str,
        error_details: Dict[str, object] | Omit = omit,
        error_stack: str | Omit = omit,
        status: PlatformJobStatus | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlatformJobTask:
        """
        Update Job Step Task

        Args:
          status: Enumeration of possible job statuses.

              This enum represents the various states a job can be in during its lifecycle,
              from creation to a terminal state.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        if not step_name:
            raise ValueError(f"Expected a non-empty value for `step_name` but received {step_name!r}")
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._put(
            f"/v1/jobs/{job_id}/steps/{step_name}/tasks/{task_id}",
            body=await async_maybe_transform(
                {
                    "error_details": error_details,
                    "error_stack": error_stack,
                    "status": status,
                },
                task_create_or_update_params.TaskCreateOrUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlatformJobTask,
        )

    async def update_status_details(
        self,
        task_id: str,
        *,
        job_id: str,
        step_name: str,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Update Task Status Details

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
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._patch(
            f"/v1/jobs/{job_id}/steps/{step_name}/tasks/{task_id}/status-details",
            body=await async_maybe_transform(body, task_update_status_details_params.TaskUpdateStatusDetailsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class TasksResourceWithRawResponse:
    def __init__(self, tasks: TasksResource) -> None:
        self._tasks = tasks

        self.retrieve = to_raw_response_wrapper(
            tasks.retrieve,
        )
        self.list = to_raw_response_wrapper(
            tasks.list,
        )
        self.create_or_update = to_raw_response_wrapper(
            tasks.create_or_update,
        )
        self.update_status_details = to_raw_response_wrapper(
            tasks.update_status_details,
        )


class AsyncTasksResourceWithRawResponse:
    def __init__(self, tasks: AsyncTasksResource) -> None:
        self._tasks = tasks

        self.retrieve = async_to_raw_response_wrapper(
            tasks.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            tasks.list,
        )
        self.create_or_update = async_to_raw_response_wrapper(
            tasks.create_or_update,
        )
        self.update_status_details = async_to_raw_response_wrapper(
            tasks.update_status_details,
        )


class TasksResourceWithStreamingResponse:
    def __init__(self, tasks: TasksResource) -> None:
        self._tasks = tasks

        self.retrieve = to_streamed_response_wrapper(
            tasks.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            tasks.list,
        )
        self.create_or_update = to_streamed_response_wrapper(
            tasks.create_or_update,
        )
        self.update_status_details = to_streamed_response_wrapper(
            tasks.update_status_details,
        )


class AsyncTasksResourceWithStreamingResponse:
    def __init__(self, tasks: AsyncTasksResource) -> None:
        self._tasks = tasks

        self.retrieve = async_to_streamed_response_wrapper(
            tasks.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            tasks.list,
        )
        self.create_or_update = async_to_streamed_response_wrapper(
            tasks.create_or_update,
        )
        self.update_status_details = async_to_streamed_response_wrapper(
            tasks.update_status_details,
        )
