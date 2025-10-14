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

from typing import Dict, Union, Iterable
from typing_extensions import Literal, overload

import httpx

from ....types import GuardrailsDataParam
from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import required_args, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._streaming import Stream, AsyncStream
from ...._base_client import make_request_options
from ....types.guardrail.chat import completion_create_params
from ....types.guardrails_data_param import GuardrailsDataParam
from ....types.guardrail.chat.guardrail_chat_completion_response import GuardrailChatCompletionResponse
from ....types.guardrail.chat.guardrail_chat_completion_stream_response import GuardrailChatCompletionStreamResponse

__all__ = ["CompletionsResource", "AsyncCompletionsResource"]


class CompletionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CompletionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return CompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CompletionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return CompletionsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: str,
        best_of: int | Omit = omit,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        function_call: Union[str, Dict[str, object]] | Omit = omit,
        guardrails: GuardrailsDataParam | Omit = omit,
        ignore_eos: bool | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: bool | Omit = omit,
        max_tokens: int | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        response_format: Dict[str, str] | Omit = omit,
        seed: int | Omit = omit,
        stop: Union[str, SequenceNotStr[str]] | Omit = omit,
        stream: Literal[False] | Omit = omit,
        suffix: str | Omit = omit,
        system_fingerprint: str | Omit = omit,
        temperature: float | Omit = omit,
        tool_choice: Union[str, Dict[str, object]] | Omit = omit,
        tools: SequenceNotStr[str] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        user: str | Omit = omit,
        vision: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GuardrailChatCompletionResponse:
        """
        Chat completion for the provided conversation.

        Args:
          messages: A list of messages comprising the conversation so far

          model: The model to use for completion. Must be one of the available models.

          best_of: Not supported. Generates best_of completions server-side and returns the "best"
              (the one with the highest log probability per token). Results cannot be
              streamed. When used with n, best_of controls the number of candidate completions
              and n specifies how many to return - best_of must be greater than n.

          echo: Not supported. If `echo` is true, the response will include the prompt and
              optionally its tokens ids and logprobs.

          frequency_penalty: Positive values penalize new tokens based on their existing frequency in the
              text.

          function_call: Not Supported. Deprecated in favor of tool_choice. 'none' means the model will
              not call a function and instead generates a message. 'auto' means the model can
              pick between generating a message or calling a function. Specifying a particular
              function via {'name': 'my_function'} forces the model to call that function.

          guardrails: Guardrails specific options for the request.

          ignore_eos: Ignore the eos when running

          logit_bias: Not Supported. Modify the likelihood of specified tokens appearing in the
              completion.

          logprobs: Whether to return log probabilities of the output tokens or not. If true,
              returns the log probabilities of each output token returned in the content of
              message

          max_tokens: The maximum number of tokens that can be generated in the chat completion.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Positive values penalize new tokens based on whether they appear in the text so
              far.

          response_format: Format of the response, can be 'json_object' to force the model to output valid
              JSON.

          seed: If specified, attempts to sample deterministically.

          stop: Up to 4 sequences where the API will stop generating further tokens.

          stream: If set, partial message deltas will be sent, like in ChatGPT.

          suffix: Not supported. If echo is set, the prompt is returned with the completion.

          system_fingerprint: Represents the backend configuration that the model runs with. Used with seed
              for determinism.

          temperature: What sampling temperature to use, between 0 and 2.

          tool_choice: Not Supported. Favored over function_call. Controls which (if any) function is
              called by the model.

          tools: A list of tools the model may call.

          top_logprobs: The number of most likely tokens to return at each token position.

          top_p: An alternative to sampling with temperature, called nucleus sampling.

          user: Not Supported. A unique identifier representing your end-user.

          vision: Whether this is a vision-capable request with image inputs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: str,
        stream: Literal[True],
        best_of: int | Omit = omit,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        function_call: Union[str, Dict[str, object]] | Omit = omit,
        guardrails: GuardrailsDataParam | Omit = omit,
        ignore_eos: bool | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: bool | Omit = omit,
        max_tokens: int | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        response_format: Dict[str, str] | Omit = omit,
        seed: int | Omit = omit,
        stop: Union[str, SequenceNotStr[str]] | Omit = omit,
        suffix: str | Omit = omit,
        system_fingerprint: str | Omit = omit,
        temperature: float | Omit = omit,
        tool_choice: Union[str, Dict[str, object]] | Omit = omit,
        tools: SequenceNotStr[str] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        user: str | Omit = omit,
        vision: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[GuardrailChatCompletionStreamResponse]:
        """
        Chat completion for the provided conversation.

        Args:
          messages: A list of messages comprising the conversation so far

          model: The model to use for completion. Must be one of the available models.

          stream: If set, partial message deltas will be sent, like in ChatGPT.

          best_of: Not supported. Generates best_of completions server-side and returns the "best"
              (the one with the highest log probability per token). Results cannot be
              streamed. When used with n, best_of controls the number of candidate completions
              and n specifies how many to return - best_of must be greater than n.

          echo: Not supported. If `echo` is true, the response will include the prompt and
              optionally its tokens ids and logprobs.

          frequency_penalty: Positive values penalize new tokens based on their existing frequency in the
              text.

          function_call: Not Supported. Deprecated in favor of tool_choice. 'none' means the model will
              not call a function and instead generates a message. 'auto' means the model can
              pick between generating a message or calling a function. Specifying a particular
              function via {'name': 'my_function'} forces the model to call that function.

          guardrails: Guardrails specific options for the request.

          ignore_eos: Ignore the eos when running

          logit_bias: Not Supported. Modify the likelihood of specified tokens appearing in the
              completion.

          logprobs: Whether to return log probabilities of the output tokens or not. If true,
              returns the log probabilities of each output token returned in the content of
              message

          max_tokens: The maximum number of tokens that can be generated in the chat completion.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Positive values penalize new tokens based on whether they appear in the text so
              far.

          response_format: Format of the response, can be 'json_object' to force the model to output valid
              JSON.

          seed: If specified, attempts to sample deterministically.

          stop: Up to 4 sequences where the API will stop generating further tokens.

          suffix: Not supported. If echo is set, the prompt is returned with the completion.

          system_fingerprint: Represents the backend configuration that the model runs with. Used with seed
              for determinism.

          temperature: What sampling temperature to use, between 0 and 2.

          tool_choice: Not Supported. Favored over function_call. Controls which (if any) function is
              called by the model.

          tools: A list of tools the model may call.

          top_logprobs: The number of most likely tokens to return at each token position.

          top_p: An alternative to sampling with temperature, called nucleus sampling.

          user: Not Supported. A unique identifier representing your end-user.

          vision: Whether this is a vision-capable request with image inputs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: str,
        stream: bool,
        best_of: int | Omit = omit,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        function_call: Union[str, Dict[str, object]] | Omit = omit,
        guardrails: GuardrailsDataParam | Omit = omit,
        ignore_eos: bool | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: bool | Omit = omit,
        max_tokens: int | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        response_format: Dict[str, str] | Omit = omit,
        seed: int | Omit = omit,
        stop: Union[str, SequenceNotStr[str]] | Omit = omit,
        suffix: str | Omit = omit,
        system_fingerprint: str | Omit = omit,
        temperature: float | Omit = omit,
        tool_choice: Union[str, Dict[str, object]] | Omit = omit,
        tools: SequenceNotStr[str] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        user: str | Omit = omit,
        vision: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GuardrailChatCompletionResponse | Stream[GuardrailChatCompletionStreamResponse]:
        """
        Chat completion for the provided conversation.

        Args:
          messages: A list of messages comprising the conversation so far

          model: The model to use for completion. Must be one of the available models.

          stream: If set, partial message deltas will be sent, like in ChatGPT.

          best_of: Not supported. Generates best_of completions server-side and returns the "best"
              (the one with the highest log probability per token). Results cannot be
              streamed. When used with n, best_of controls the number of candidate completions
              and n specifies how many to return - best_of must be greater than n.

          echo: Not supported. If `echo` is true, the response will include the prompt and
              optionally its tokens ids and logprobs.

          frequency_penalty: Positive values penalize new tokens based on their existing frequency in the
              text.

          function_call: Not Supported. Deprecated in favor of tool_choice. 'none' means the model will
              not call a function and instead generates a message. 'auto' means the model can
              pick between generating a message or calling a function. Specifying a particular
              function via {'name': 'my_function'} forces the model to call that function.

          guardrails: Guardrails specific options for the request.

          ignore_eos: Ignore the eos when running

          logit_bias: Not Supported. Modify the likelihood of specified tokens appearing in the
              completion.

          logprobs: Whether to return log probabilities of the output tokens or not. If true,
              returns the log probabilities of each output token returned in the content of
              message

          max_tokens: The maximum number of tokens that can be generated in the chat completion.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Positive values penalize new tokens based on whether they appear in the text so
              far.

          response_format: Format of the response, can be 'json_object' to force the model to output valid
              JSON.

          seed: If specified, attempts to sample deterministically.

          stop: Up to 4 sequences where the API will stop generating further tokens.

          suffix: Not supported. If echo is set, the prompt is returned with the completion.

          system_fingerprint: Represents the backend configuration that the model runs with. Used with seed
              for determinism.

          temperature: What sampling temperature to use, between 0 and 2.

          tool_choice: Not Supported. Favored over function_call. Controls which (if any) function is
              called by the model.

          tools: A list of tools the model may call.

          top_logprobs: The number of most likely tokens to return at each token position.

          top_p: An alternative to sampling with temperature, called nucleus sampling.

          user: Not Supported. A unique identifier representing your end-user.

          vision: Whether this is a vision-capable request with image inputs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["messages", "model"], ["messages", "model", "stream"])
    def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: str,
        best_of: int | Omit = omit,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        function_call: Union[str, Dict[str, object]] | Omit = omit,
        guardrails: GuardrailsDataParam | Omit = omit,
        ignore_eos: bool | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: bool | Omit = omit,
        max_tokens: int | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        response_format: Dict[str, str] | Omit = omit,
        seed: int | Omit = omit,
        stop: Union[str, SequenceNotStr[str]] | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        suffix: str | Omit = omit,
        system_fingerprint: str | Omit = omit,
        temperature: float | Omit = omit,
        tool_choice: Union[str, Dict[str, object]] | Omit = omit,
        tools: SequenceNotStr[str] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        user: str | Omit = omit,
        vision: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GuardrailChatCompletionResponse | Stream[GuardrailChatCompletionStreamResponse]:
        return self._post(
            "/v1/guardrail/chat/completions",
            body=maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "best_of": best_of,
                    "echo": echo,
                    "frequency_penalty": frequency_penalty,
                    "function_call": function_call,
                    "guardrails": guardrails,
                    "ignore_eos": ignore_eos,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_tokens": max_tokens,
                    "n": n,
                    "presence_penalty": presence_penalty,
                    "response_format": response_format,
                    "seed": seed,
                    "stop": stop,
                    "stream": stream,
                    "suffix": suffix,
                    "system_fingerprint": system_fingerprint,
                    "temperature": temperature,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "user": user,
                    "vision": vision,
                },
                completion_create_params.CompletionCreateParamsStreaming
                if stream
                else completion_create_params.CompletionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GuardrailChatCompletionResponse,
            stream=stream or False,
            stream_cls=Stream[GuardrailChatCompletionStreamResponse],
        )


class AsyncCompletionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCompletionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncCompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCompletionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncCompletionsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: str,
        best_of: int | Omit = omit,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        function_call: Union[str, Dict[str, object]] | Omit = omit,
        guardrails: GuardrailsDataParam | Omit = omit,
        ignore_eos: bool | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: bool | Omit = omit,
        max_tokens: int | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        response_format: Dict[str, str] | Omit = omit,
        seed: int | Omit = omit,
        stop: Union[str, SequenceNotStr[str]] | Omit = omit,
        stream: Literal[False] | Omit = omit,
        suffix: str | Omit = omit,
        system_fingerprint: str | Omit = omit,
        temperature: float | Omit = omit,
        tool_choice: Union[str, Dict[str, object]] | Omit = omit,
        tools: SequenceNotStr[str] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        user: str | Omit = omit,
        vision: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GuardrailChatCompletionResponse:
        """
        Chat completion for the provided conversation.

        Args:
          messages: A list of messages comprising the conversation so far

          model: The model to use for completion. Must be one of the available models.

          best_of: Not supported. Generates best_of completions server-side and returns the "best"
              (the one with the highest log probability per token). Results cannot be
              streamed. When used with n, best_of controls the number of candidate completions
              and n specifies how many to return - best_of must be greater than n.

          echo: Not supported. If `echo` is true, the response will include the prompt and
              optionally its tokens ids and logprobs.

          frequency_penalty: Positive values penalize new tokens based on their existing frequency in the
              text.

          function_call: Not Supported. Deprecated in favor of tool_choice. 'none' means the model will
              not call a function and instead generates a message. 'auto' means the model can
              pick between generating a message or calling a function. Specifying a particular
              function via {'name': 'my_function'} forces the model to call that function.

          guardrails: Guardrails specific options for the request.

          ignore_eos: Ignore the eos when running

          logit_bias: Not Supported. Modify the likelihood of specified tokens appearing in the
              completion.

          logprobs: Whether to return log probabilities of the output tokens or not. If true,
              returns the log probabilities of each output token returned in the content of
              message

          max_tokens: The maximum number of tokens that can be generated in the chat completion.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Positive values penalize new tokens based on whether they appear in the text so
              far.

          response_format: Format of the response, can be 'json_object' to force the model to output valid
              JSON.

          seed: If specified, attempts to sample deterministically.

          stop: Up to 4 sequences where the API will stop generating further tokens.

          stream: If set, partial message deltas will be sent, like in ChatGPT.

          suffix: Not supported. If echo is set, the prompt is returned with the completion.

          system_fingerprint: Represents the backend configuration that the model runs with. Used with seed
              for determinism.

          temperature: What sampling temperature to use, between 0 and 2.

          tool_choice: Not Supported. Favored over function_call. Controls which (if any) function is
              called by the model.

          tools: A list of tools the model may call.

          top_logprobs: The number of most likely tokens to return at each token position.

          top_p: An alternative to sampling with temperature, called nucleus sampling.

          user: Not Supported. A unique identifier representing your end-user.

          vision: Whether this is a vision-capable request with image inputs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: str,
        stream: Literal[True],
        best_of: int | Omit = omit,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        function_call: Union[str, Dict[str, object]] | Omit = omit,
        guardrails: GuardrailsDataParam | Omit = omit,
        ignore_eos: bool | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: bool | Omit = omit,
        max_tokens: int | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        response_format: Dict[str, str] | Omit = omit,
        seed: int | Omit = omit,
        stop: Union[str, SequenceNotStr[str]] | Omit = omit,
        suffix: str | Omit = omit,
        system_fingerprint: str | Omit = omit,
        temperature: float | Omit = omit,
        tool_choice: Union[str, Dict[str, object]] | Omit = omit,
        tools: SequenceNotStr[str] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        user: str | Omit = omit,
        vision: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[GuardrailChatCompletionStreamResponse]:
        """
        Chat completion for the provided conversation.

        Args:
          messages: A list of messages comprising the conversation so far

          model: The model to use for completion. Must be one of the available models.

          stream: If set, partial message deltas will be sent, like in ChatGPT.

          best_of: Not supported. Generates best_of completions server-side and returns the "best"
              (the one with the highest log probability per token). Results cannot be
              streamed. When used with n, best_of controls the number of candidate completions
              and n specifies how many to return - best_of must be greater than n.

          echo: Not supported. If `echo` is true, the response will include the prompt and
              optionally its tokens ids and logprobs.

          frequency_penalty: Positive values penalize new tokens based on their existing frequency in the
              text.

          function_call: Not Supported. Deprecated in favor of tool_choice. 'none' means the model will
              not call a function and instead generates a message. 'auto' means the model can
              pick between generating a message or calling a function. Specifying a particular
              function via {'name': 'my_function'} forces the model to call that function.

          guardrails: Guardrails specific options for the request.

          ignore_eos: Ignore the eos when running

          logit_bias: Not Supported. Modify the likelihood of specified tokens appearing in the
              completion.

          logprobs: Whether to return log probabilities of the output tokens or not. If true,
              returns the log probabilities of each output token returned in the content of
              message

          max_tokens: The maximum number of tokens that can be generated in the chat completion.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Positive values penalize new tokens based on whether they appear in the text so
              far.

          response_format: Format of the response, can be 'json_object' to force the model to output valid
              JSON.

          seed: If specified, attempts to sample deterministically.

          stop: Up to 4 sequences where the API will stop generating further tokens.

          suffix: Not supported. If echo is set, the prompt is returned with the completion.

          system_fingerprint: Represents the backend configuration that the model runs with. Used with seed
              for determinism.

          temperature: What sampling temperature to use, between 0 and 2.

          tool_choice: Not Supported. Favored over function_call. Controls which (if any) function is
              called by the model.

          tools: A list of tools the model may call.

          top_logprobs: The number of most likely tokens to return at each token position.

          top_p: An alternative to sampling with temperature, called nucleus sampling.

          user: Not Supported. A unique identifier representing your end-user.

          vision: Whether this is a vision-capable request with image inputs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: str,
        stream: bool,
        best_of: int | Omit = omit,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        function_call: Union[str, Dict[str, object]] | Omit = omit,
        guardrails: GuardrailsDataParam | Omit = omit,
        ignore_eos: bool | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: bool | Omit = omit,
        max_tokens: int | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        response_format: Dict[str, str] | Omit = omit,
        seed: int | Omit = omit,
        stop: Union[str, SequenceNotStr[str]] | Omit = omit,
        suffix: str | Omit = omit,
        system_fingerprint: str | Omit = omit,
        temperature: float | Omit = omit,
        tool_choice: Union[str, Dict[str, object]] | Omit = omit,
        tools: SequenceNotStr[str] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        user: str | Omit = omit,
        vision: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GuardrailChatCompletionResponse | AsyncStream[GuardrailChatCompletionStreamResponse]:
        """
        Chat completion for the provided conversation.

        Args:
          messages: A list of messages comprising the conversation so far

          model: The model to use for completion. Must be one of the available models.

          stream: If set, partial message deltas will be sent, like in ChatGPT.

          best_of: Not supported. Generates best_of completions server-side and returns the "best"
              (the one with the highest log probability per token). Results cannot be
              streamed. When used with n, best_of controls the number of candidate completions
              and n specifies how many to return - best_of must be greater than n.

          echo: Not supported. If `echo` is true, the response will include the prompt and
              optionally its tokens ids and logprobs.

          frequency_penalty: Positive values penalize new tokens based on their existing frequency in the
              text.

          function_call: Not Supported. Deprecated in favor of tool_choice. 'none' means the model will
              not call a function and instead generates a message. 'auto' means the model can
              pick between generating a message or calling a function. Specifying a particular
              function via {'name': 'my_function'} forces the model to call that function.

          guardrails: Guardrails specific options for the request.

          ignore_eos: Ignore the eos when running

          logit_bias: Not Supported. Modify the likelihood of specified tokens appearing in the
              completion.

          logprobs: Whether to return log probabilities of the output tokens or not. If true,
              returns the log probabilities of each output token returned in the content of
              message

          max_tokens: The maximum number of tokens that can be generated in the chat completion.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Positive values penalize new tokens based on whether they appear in the text so
              far.

          response_format: Format of the response, can be 'json_object' to force the model to output valid
              JSON.

          seed: If specified, attempts to sample deterministically.

          stop: Up to 4 sequences where the API will stop generating further tokens.

          suffix: Not supported. If echo is set, the prompt is returned with the completion.

          system_fingerprint: Represents the backend configuration that the model runs with. Used with seed
              for determinism.

          temperature: What sampling temperature to use, between 0 and 2.

          tool_choice: Not Supported. Favored over function_call. Controls which (if any) function is
              called by the model.

          tools: A list of tools the model may call.

          top_logprobs: The number of most likely tokens to return at each token position.

          top_p: An alternative to sampling with temperature, called nucleus sampling.

          user: Not Supported. A unique identifier representing your end-user.

          vision: Whether this is a vision-capable request with image inputs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["messages", "model"], ["messages", "model", "stream"])
    async def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: str,
        best_of: int | Omit = omit,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        function_call: Union[str, Dict[str, object]] | Omit = omit,
        guardrails: GuardrailsDataParam | Omit = omit,
        ignore_eos: bool | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: bool | Omit = omit,
        max_tokens: int | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        response_format: Dict[str, str] | Omit = omit,
        seed: int | Omit = omit,
        stop: Union[str, SequenceNotStr[str]] | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        suffix: str | Omit = omit,
        system_fingerprint: str | Omit = omit,
        temperature: float | Omit = omit,
        tool_choice: Union[str, Dict[str, object]] | Omit = omit,
        tools: SequenceNotStr[str] | Omit = omit,
        top_logprobs: int | Omit = omit,
        top_p: float | Omit = omit,
        user: str | Omit = omit,
        vision: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GuardrailChatCompletionResponse | AsyncStream[GuardrailChatCompletionStreamResponse]:
        return await self._post(
            "/v1/guardrail/chat/completions",
            body=await async_maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "best_of": best_of,
                    "echo": echo,
                    "frequency_penalty": frequency_penalty,
                    "function_call": function_call,
                    "guardrails": guardrails,
                    "ignore_eos": ignore_eos,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_tokens": max_tokens,
                    "n": n,
                    "presence_penalty": presence_penalty,
                    "response_format": response_format,
                    "seed": seed,
                    "stop": stop,
                    "stream": stream,
                    "suffix": suffix,
                    "system_fingerprint": system_fingerprint,
                    "temperature": temperature,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "user": user,
                    "vision": vision,
                },
                completion_create_params.CompletionCreateParamsStreaming
                if stream
                else completion_create_params.CompletionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GuardrailChatCompletionResponse,
            stream=stream or False,
            stream_cls=AsyncStream[GuardrailChatCompletionStreamResponse],
        )


class CompletionsResourceWithRawResponse:
    def __init__(self, completions: CompletionsResource) -> None:
        self._completions = completions

        self.create = to_raw_response_wrapper(
            completions.create,
        )


class AsyncCompletionsResourceWithRawResponse:
    def __init__(self, completions: AsyncCompletionsResource) -> None:
        self._completions = completions

        self.create = async_to_raw_response_wrapper(
            completions.create,
        )


class CompletionsResourceWithStreamingResponse:
    def __init__(self, completions: CompletionsResource) -> None:
        self._completions = completions

        self.create = to_streamed_response_wrapper(
            completions.create,
        )


class AsyncCompletionsResourceWithStreamingResponse:
    def __init__(self, completions: AsyncCompletionsResource) -> None:
        self._completions = completions

        self.create = async_to_streamed_response_wrapper(
            completions.create,
        )
