# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import get_message_retrieve_params
from .._types import Body, Query, Headers, NotGiven, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.get_message_retrieve_response import GetMessageRetrieveResponse

__all__ = ["GetMessagesResource", "AsyncGetMessagesResource"]


class GetMessagesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GetMessagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AgentbaseHQ/agentbase-python#accessing-raw-response-data-eg-headers
        """
        return GetMessagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GetMessagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AgentbaseHQ/agentbase-python#with_streaming_response
        """
        return GetMessagesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        session: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetMessageRetrieveResponse:
        """Retrieve the entire message history for a given agent session.


        Messages include user messages, the agent’s internal thoughts, agent responses,
        and tool usage records.

        Args:
          session: The session ID to retrieve messages from.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/get-messages",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"session": session}, get_message_retrieve_params.GetMessageRetrieveParams),
            ),
            cast_to=GetMessageRetrieveResponse,
        )


class AsyncGetMessagesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGetMessagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AgentbaseHQ/agentbase-python#accessing-raw-response-data-eg-headers
        """
        return AsyncGetMessagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGetMessagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AgentbaseHQ/agentbase-python#with_streaming_response
        """
        return AsyncGetMessagesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        session: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetMessageRetrieveResponse:
        """Retrieve the entire message history for a given agent session.


        Messages include user messages, the agent’s internal thoughts, agent responses,
        and tool usage records.

        Args:
          session: The session ID to retrieve messages from.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/get-messages",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"session": session}, get_message_retrieve_params.GetMessageRetrieveParams
                ),
            ),
            cast_to=GetMessageRetrieveResponse,
        )


class GetMessagesResourceWithRawResponse:
    def __init__(self, get_messages: GetMessagesResource) -> None:
        self._get_messages = get_messages

        self.retrieve = to_raw_response_wrapper(
            get_messages.retrieve,
        )


class AsyncGetMessagesResourceWithRawResponse:
    def __init__(self, get_messages: AsyncGetMessagesResource) -> None:
        self._get_messages = get_messages

        self.retrieve = async_to_raw_response_wrapper(
            get_messages.retrieve,
        )


class GetMessagesResourceWithStreamingResponse:
    def __init__(self, get_messages: GetMessagesResource) -> None:
        self._get_messages = get_messages

        self.retrieve = to_streamed_response_wrapper(
            get_messages.retrieve,
        )


class AsyncGetMessagesResourceWithStreamingResponse:
    def __init__(self, get_messages: AsyncGetMessagesResource) -> None:
        self._get_messages = get_messages

        self.retrieve = async_to_streamed_response_wrapper(
            get_messages.retrieve,
        )
