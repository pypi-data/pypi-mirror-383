# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "AgentRunParams",
    "Callback",
    "Datastore",
    "FinalOutput",
    "McpServer",
    "Query",
    "Workflow",
    "WorkflowStep",
    "WorkflowStepRetryPolicy",
]


class AgentRunParams(TypedDict, total=False):
    message: Required[str]
    """The task or message to run the agent with."""

    session: str
    """The session ID to continue the agent session conversation.

    If not provided, a new session will be created.
    """

    background: bool
    """Whether to run the agent asynchronously on the server.

    When set to true, use callback parameter to receive events.
    """

    callback: Callback
    """A callback endpoint configuration to send agent message events back to.

    Use with background true.
    """

    datastores: Iterable[Datastore]
    """A set of datastores for the agent to utilize.

    Each object must include a `id` and `name`.
    """

    final_output: FinalOutput
    """
    Configuration for an extra final output event that processes the entire agent
    message thread and produces a structured output based on the provided JSON
    schema.
    """

    mcp_servers: Iterable[McpServer]
    """A list of MCP server configurations.

    Each object must include a `serverName` and `serverUrl`.
    """

    mode: Literal["flash", "fast", "max"]
    """The agent mode.

    Allowed values are `flash`, `fast` or `max`. Defaults to `fast` if not supplied.
    """

    queries: Iterable[Query]
    """A set of custom actions based on datastore (database) queries.

    Allows you to quickly define actions that the agent can use to query your
    datastores.
    """

    rules: SequenceNotStr[str]
    """A list of constraints that the agent must follow."""

    streaming_tokens: bool
    """Whether to stream the agent messages token by token."""

    system: str
    """A system prompt to provide system information to the agent."""

    workflows: Iterable[Workflow]
    """A set of declarative workflows for the agent to execute.

    Each workflow is a DAG (Directed Acyclic Graph) of steps that the agent
    interprets and executes dynamically.
    """


class Callback(TypedDict, total=False):
    url: Required[str]
    """The webhook URL to send events to."""

    headers: Dict[str, str]
    """Optional headers to include in the callback request."""


class Datastore(TypedDict, total=False):
    id: Required[str]
    """The ID of the datastore."""

    name: Required[str]
    """The name of the datastore."""


class FinalOutput(TypedDict, total=False):
    name: Required[str]
    """Name for the final output."""

    schema: Required[object]
    """JSON schema defining the structure of the final output."""

    strict: bool
    """Whether to enforce strict schema validation."""


class McpServer(TypedDict, total=False):
    server_name: Required[Annotated[str, PropertyInfo(alias="serverName")]]
    """Name of the MCP server."""

    server_url: Required[Annotated[str, PropertyInfo(alias="serverUrl")]]
    """URL of the MCP server."""


class Query(TypedDict, total=False):
    description: Required[str]
    """Description of what the query does."""

    name: Required[str]
    """Name of the query action."""

    query: Required[str]
    """The SQL query to execute."""


class WorkflowStepRetryPolicy(TypedDict, total=False):
    backoff: str

    max_attempts: int


class WorkflowStep(TypedDict, total=False):
    id: Required[str]
    """Unique identifier for the step."""

    depends_on: Required[SequenceNotStr[str]]
    """Array of step IDs that must complete before this step runs."""

    description: Required[str]
    """What the step should accomplish."""

    name: Required[str]
    """Name of the step."""

    optional: bool
    """Whether the step can be skipped if it fails."""

    output_schema: object
    """JSON schema for expected output validation."""

    retry_policy: WorkflowStepRetryPolicy
    """Retry configuration for the step."""


class Workflow(TypedDict, total=False):
    id: Required[str]
    """Unique identifier for the workflow."""

    description: Required[str]
    """What the workflow accomplishes."""

    name: Required[str]
    """Name of the workflow."""

    steps: Required[Iterable[WorkflowStep]]
    """Array of step objects."""
