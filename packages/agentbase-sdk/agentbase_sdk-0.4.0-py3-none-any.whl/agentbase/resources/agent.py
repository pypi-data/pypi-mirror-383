# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ..types import agent_run_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._streaming import Stream, AsyncStream
from .._base_client import make_request_options
from ..types.agent_run_response import AgentRunResponse

__all__ = ["AgentResource", "AsyncAgentResource"]


class AgentResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AgentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AgentbaseHQ/agentbase-python#accessing-raw-response-data-eg-headers
        """
        return AgentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AgentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AgentbaseHQ/agentbase-python#with_streaming_response
        """
        return AgentResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        message: str,
        session: str | Omit = omit,
        background: bool | Omit = omit,
        callback: agent_run_params.Callback | Omit = omit,
        datastores: Iterable[agent_run_params.Datastore] | Omit = omit,
        final_output: agent_run_params.FinalOutput | Omit = omit,
        mcp_servers: Iterable[agent_run_params.McpServer] | Omit = omit,
        mode: Literal["flash", "fast", "max"] | Omit = omit,
        queries: Iterable[agent_run_params.Query] | Omit = omit,
        rules: SequenceNotStr[str] | Omit = omit,
        streaming_tokens: bool | Omit = omit,
        system: str | Omit = omit,
        workflows: Iterable[agent_run_params.Workflow] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[AgentRunResponse]:
        """Run an agent on a task or message.


        A new session can be created by omitting the `session` query parameter, or an
        existing session can be continued by specifying the session ID in the `session`
        query parameter.
        The request body includes the message, optional system prompt, mode, MCP server
        configuration, optional rules and whether the response should be streamed.
        The response is a streaming response and returns a sequence of events
        representing the agent’s thoughts and responses.

        Args:
          message: The task or message to run the agent with.

          session: The session ID to continue the agent session conversation. If not provided, a
              new session will be created.

          background: Whether to run the agent asynchronously on the server. When set to true, use
              callback parameter to receive events.

          callback: A callback endpoint configuration to send agent message events back to. Use with
              background true.

          datastores: A set of datastores for the agent to utilize. Each object must include a `id`
              and `name`.

          final_output: Configuration for an extra final output event that processes the entire agent
              message thread and produces a structured output based on the provided JSON
              schema.

          mcp_servers: A list of MCP server configurations. Each object must include a `serverName` and
              `serverUrl`.

          mode: The agent mode. Allowed values are `flash`, `fast` or `max`. Defaults to `fast`
              if not supplied.

          queries: A set of custom actions based on datastore (database) queries. Allows you to
              quickly define actions that the agent can use to query your datastores.

          rules: A list of constraints that the agent must follow.

          streaming_tokens: Whether to stream the agent messages token by token.

          system: A system prompt to provide system information to the agent.

          workflows: A set of declarative workflows for the agent to execute. Each workflow is a DAG
              (Directed Acyclic Graph) of steps that the agent interprets and executes
              dynamically.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "text/event-stream", **(extra_headers or {})}
        return self._post(
            "/",
            body=maybe_transform(
                {
                    "message": message,
                    "background": background,
                    "callback": callback,
                    "datastores": datastores,
                    "final_output": final_output,
                    "mcp_servers": mcp_servers,
                    "mode": mode,
                    "queries": queries,
                    "rules": rules,
                    "streaming_tokens": streaming_tokens,
                    "system": system,
                    "workflows": workflows,
                },
                agent_run_params.AgentRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"session": session}, agent_run_params.AgentRunParams),
            ),
            cast_to=str,
            stream=True,
            stream_cls=Stream[AgentRunResponse],
        )


class AsyncAgentResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAgentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/AgentbaseHQ/agentbase-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAgentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAgentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/AgentbaseHQ/agentbase-python#with_streaming_response
        """
        return AsyncAgentResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        message: str,
        session: str | Omit = omit,
        background: bool | Omit = omit,
        callback: agent_run_params.Callback | Omit = omit,
        datastores: Iterable[agent_run_params.Datastore] | Omit = omit,
        final_output: agent_run_params.FinalOutput | Omit = omit,
        mcp_servers: Iterable[agent_run_params.McpServer] | Omit = omit,
        mode: Literal["flash", "fast", "max"] | Omit = omit,
        queries: Iterable[agent_run_params.Query] | Omit = omit,
        rules: SequenceNotStr[str] | Omit = omit,
        streaming_tokens: bool | Omit = omit,
        system: str | Omit = omit,
        workflows: Iterable[agent_run_params.Workflow] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[AgentRunResponse]:
        """Run an agent on a task or message.


        A new session can be created by omitting the `session` query parameter, or an
        existing session can be continued by specifying the session ID in the `session`
        query parameter.
        The request body includes the message, optional system prompt, mode, MCP server
        configuration, optional rules and whether the response should be streamed.
        The response is a streaming response and returns a sequence of events
        representing the agent’s thoughts and responses.

        Args:
          message: The task or message to run the agent with.

          session: The session ID to continue the agent session conversation. If not provided, a
              new session will be created.

          background: Whether to run the agent asynchronously on the server. When set to true, use
              callback parameter to receive events.

          callback: A callback endpoint configuration to send agent message events back to. Use with
              background true.

          datastores: A set of datastores for the agent to utilize. Each object must include a `id`
              and `name`.

          final_output: Configuration for an extra final output event that processes the entire agent
              message thread and produces a structured output based on the provided JSON
              schema.

          mcp_servers: A list of MCP server configurations. Each object must include a `serverName` and
              `serverUrl`.

          mode: The agent mode. Allowed values are `flash`, `fast` or `max`. Defaults to `fast`
              if not supplied.

          queries: A set of custom actions based on datastore (database) queries. Allows you to
              quickly define actions that the agent can use to query your datastores.

          rules: A list of constraints that the agent must follow.

          streaming_tokens: Whether to stream the agent messages token by token.

          system: A system prompt to provide system information to the agent.

          workflows: A set of declarative workflows for the agent to execute. Each workflow is a DAG
              (Directed Acyclic Graph) of steps that the agent interprets and executes
              dynamically.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "text/event-stream", **(extra_headers or {})}
        return await self._post(
            "/",
            body=await async_maybe_transform(
                {
                    "message": message,
                    "background": background,
                    "callback": callback,
                    "datastores": datastores,
                    "final_output": final_output,
                    "mcp_servers": mcp_servers,
                    "mode": mode,
                    "queries": queries,
                    "rules": rules,
                    "streaming_tokens": streaming_tokens,
                    "system": system,
                    "workflows": workflows,
                },
                agent_run_params.AgentRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"session": session}, agent_run_params.AgentRunParams),
            ),
            cast_to=str,
            stream=True,
            stream_cls=AsyncStream[AgentRunResponse],
        )


class AgentResourceWithRawResponse:
    def __init__(self, agent: AgentResource) -> None:
        self._agent = agent

        self.run = to_raw_response_wrapper(
            agent.run,
        )


class AsyncAgentResourceWithRawResponse:
    def __init__(self, agent: AsyncAgentResource) -> None:
        self._agent = agent

        self.run = async_to_raw_response_wrapper(
            agent.run,
        )


class AgentResourceWithStreamingResponse:
    def __init__(self, agent: AgentResource) -> None:
        self._agent = agent

        self.run = to_streamed_response_wrapper(
            agent.run,
        )


class AsyncAgentResourceWithStreamingResponse:
    def __init__(self, agent: AsyncAgentResource) -> None:
        self._agent = agent

        self.run = async_to_streamed_response_wrapper(
            agent.run,
        )
