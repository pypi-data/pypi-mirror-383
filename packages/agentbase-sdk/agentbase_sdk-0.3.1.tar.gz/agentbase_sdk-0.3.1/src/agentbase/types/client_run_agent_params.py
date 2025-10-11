# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["ClientRunAgentParams", "Datastore", "McpServer"]


class ClientRunAgentParams(TypedDict, total=False):
    message: Required[str]
    """The task or message to run the agent with."""

    session: str
    """The session ID to continue the agent session conversation.

    If not provided, a new session will be created.
    """

    datastores: Iterable[Datastore]
    """A set of datastores for the agent to utilize.

    Each object must include a `id` and `name`.
    """

    mcp_servers: Iterable[McpServer]
    """A list of MCP server configurations.

    Each object must include a `serverName` and `serverUrl`.
    """

    mode: Literal["flash", "fast", "max"]
    """The agent mode.

    Allowed values are `flash`, `fast` or `max`. Defaults to `fast` if not supplied.
    """

    rules: SequenceNotStr[str]
    """A list of constraints that the agent must follow."""

    streaming_tokens: bool
    """Whether to stream the agent messages token by token."""

    system: str
    """A system prompt to provide system information to the agent."""


class Datastore(TypedDict, total=False):
    id: Required[str]
    """The ID of the datastore."""

    name: Required[str]
    """The name of the datastore."""


class McpServer(TypedDict, total=False):
    server_name: Required[Annotated[str, PropertyInfo(alias="serverName")]]
    """Name of the MCP server."""

    server_url: Required[Annotated[str, PropertyInfo(alias="serverUrl")]]
    """URL of the MCP server."""
