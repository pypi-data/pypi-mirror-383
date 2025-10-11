# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Mapping, Iterable
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from .types import client_run_agent_params
from ._types import (
    Body,
    Omit,
    Query,
    Headers,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    SequenceNotStr,
    omit,
    not_given,
)
from ._utils import (
    is_given,
    maybe_transform,
    get_async_library,
    async_maybe_transform,
)
from ._version import __version__
from ._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .resources import agent, messages
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import AgentbaseError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
    make_request_options,
)
from .types.run_agent_response import RunAgentResponse

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Agentbase",
    "AsyncAgentbase",
    "Client",
    "AsyncClient",
]


class Agentbase(SyncAPIClient):
    agent: agent.AgentResource
    messages: messages.MessagesResource
    with_raw_response: AgentbaseWithRawResponse
    with_streaming_response: AgentbaseWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Agentbase client instance.

        This automatically infers the `api_key` argument from the `AGENTBASE_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("AGENTBASE_API_KEY")
        if api_key is None:
            raise AgentbaseError(
                "The api_key client option must be set either by passing api_key to the client or by setting the AGENTBASE_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("AGENTBASE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.agentbase.sh"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.agent = agent.AgentResource(self)
        self.messages = messages.MessagesResource(self)
        self.with_raw_response = AgentbaseWithRawResponse(self)
        self.with_streaming_response = AgentbaseWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    def run_agent(
        self,
        *,
        message: str,
        session: str | Omit = omit,
        background: bool | Omit = omit,
        callback: client_run_agent_params.Callback | Omit = omit,
        datastores: Iterable[client_run_agent_params.Datastore] | Omit = omit,
        final_output: client_run_agent_params.FinalOutput | Omit = omit,
        mcp_servers: Iterable[client_run_agent_params.McpServer] | Omit = omit,
        mode: Literal["flash", "fast", "max"] | Omit = omit,
        queries: Iterable[client_run_agent_params.Query] | Omit = omit,
        rules: SequenceNotStr[str] | Omit = omit,
        streaming_tokens: bool | Omit = omit,
        system: str | Omit = omit,
        workflows: Iterable[client_run_agent_params.Workflow] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[RunAgentResponse]:
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
        return self.post(
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
                client_run_agent_params.ClientRunAgentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"session": session}, client_run_agent_params.ClientRunAgentParams),
            ),
            cast_to=str,
            stream=True,
            stream_cls=Stream[RunAgentResponse],
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncAgentbase(AsyncAPIClient):
    agent: agent.AsyncAgentResource
    messages: messages.AsyncMessagesResource
    with_raw_response: AsyncAgentbaseWithRawResponse
    with_streaming_response: AsyncAgentbaseWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncAgentbase client instance.

        This automatically infers the `api_key` argument from the `AGENTBASE_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("AGENTBASE_API_KEY")
        if api_key is None:
            raise AgentbaseError(
                "The api_key client option must be set either by passing api_key to the client or by setting the AGENTBASE_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("AGENTBASE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.agentbase.sh"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.agent = agent.AsyncAgentResource(self)
        self.messages = messages.AsyncMessagesResource(self)
        self.with_raw_response = AsyncAgentbaseWithRawResponse(self)
        self.with_streaming_response = AsyncAgentbaseWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    async def run_agent(
        self,
        *,
        message: str,
        session: str | Omit = omit,
        background: bool | Omit = omit,
        callback: client_run_agent_params.Callback | Omit = omit,
        datastores: Iterable[client_run_agent_params.Datastore] | Omit = omit,
        final_output: client_run_agent_params.FinalOutput | Omit = omit,
        mcp_servers: Iterable[client_run_agent_params.McpServer] | Omit = omit,
        mode: Literal["flash", "fast", "max"] | Omit = omit,
        queries: Iterable[client_run_agent_params.Query] | Omit = omit,
        rules: SequenceNotStr[str] | Omit = omit,
        streaming_tokens: bool | Omit = omit,
        system: str | Omit = omit,
        workflows: Iterable[client_run_agent_params.Workflow] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[RunAgentResponse]:
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
        return await self.post(
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
                client_run_agent_params.ClientRunAgentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"session": session}, client_run_agent_params.ClientRunAgentParams),
            ),
            cast_to=str,
            stream=True,
            stream_cls=AsyncStream[RunAgentResponse],
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AgentbaseWithRawResponse:
    def __init__(self, client: Agentbase) -> None:
        self.agent = agent.AgentResourceWithRawResponse(client.agent)
        self.messages = messages.MessagesResourceWithRawResponse(client.messages)

        self.run_agent = to_raw_response_wrapper(
            client.run_agent,
        )


class AsyncAgentbaseWithRawResponse:
    def __init__(self, client: AsyncAgentbase) -> None:
        self.agent = agent.AsyncAgentResourceWithRawResponse(client.agent)
        self.messages = messages.AsyncMessagesResourceWithRawResponse(client.messages)

        self.run_agent = async_to_raw_response_wrapper(
            client.run_agent,
        )


class AgentbaseWithStreamedResponse:
    def __init__(self, client: Agentbase) -> None:
        self.agent = agent.AgentResourceWithStreamingResponse(client.agent)
        self.messages = messages.MessagesResourceWithStreamingResponse(client.messages)

        self.run_agent = to_streamed_response_wrapper(
            client.run_agent,
        )


class AsyncAgentbaseWithStreamedResponse:
    def __init__(self, client: AsyncAgentbase) -> None:
        self.agent = agent.AsyncAgentResourceWithStreamingResponse(client.agent)
        self.messages = messages.AsyncMessagesResourceWithStreamingResponse(client.messages)

        self.run_agent = async_to_streamed_response_wrapper(
            client.run_agent,
        )


Client = Agentbase

AsyncClient = AsyncAgentbase
