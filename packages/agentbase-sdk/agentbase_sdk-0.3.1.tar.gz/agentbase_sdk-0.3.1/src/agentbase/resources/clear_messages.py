# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import clear_message_clear_params
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
from ..types.clear_message_clear_response import ClearMessageClearResponse

__all__ = ["ClearMessagesResource", "AsyncClearMessagesResource"]


class ClearMessagesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClearMessagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AgentbaseHQ/agentbase-python#accessing-raw-response-data-eg-headers
        """
        return ClearMessagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClearMessagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AgentbaseHQ/agentbase-python#with_streaming_response
        """
        return ClearMessagesResourceWithStreamingResponse(self)

    def clear(
        self,
        *,
        session: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClearMessageClearResponse:
        """
        Clear all messages from a given agent session.

        Args:
          session: The session ID to clear messages from.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/clear-messages",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"session": session}, clear_message_clear_params.ClearMessageClearParams),
            ),
            cast_to=ClearMessageClearResponse,
        )


class AsyncClearMessagesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClearMessagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AgentbaseHQ/agentbase-python#accessing-raw-response-data-eg-headers
        """
        return AsyncClearMessagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClearMessagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AgentbaseHQ/agentbase-python#with_streaming_response
        """
        return AsyncClearMessagesResourceWithStreamingResponse(self)

    async def clear(
        self,
        *,
        session: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClearMessageClearResponse:
        """
        Clear all messages from a given agent session.

        Args:
          session: The session ID to clear messages from.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/clear-messages",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"session": session}, clear_message_clear_params.ClearMessageClearParams
                ),
            ),
            cast_to=ClearMessageClearResponse,
        )


class ClearMessagesResourceWithRawResponse:
    def __init__(self, clear_messages: ClearMessagesResource) -> None:
        self._clear_messages = clear_messages

        self.clear = to_raw_response_wrapper(
            clear_messages.clear,
        )


class AsyncClearMessagesResourceWithRawResponse:
    def __init__(self, clear_messages: AsyncClearMessagesResource) -> None:
        self._clear_messages = clear_messages

        self.clear = async_to_raw_response_wrapper(
            clear_messages.clear,
        )


class ClearMessagesResourceWithStreamingResponse:
    def __init__(self, clear_messages: ClearMessagesResource) -> None:
        self._clear_messages = clear_messages

        self.clear = to_streamed_response_wrapper(
            clear_messages.clear,
        )


class AsyncClearMessagesResourceWithStreamingResponse:
    def __init__(self, clear_messages: AsyncClearMessagesResource) -> None:
        self._clear_messages = clear_messages

        self.clear = async_to_streamed_response_wrapper(
            clear_messages.clear,
        )
