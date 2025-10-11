# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["MessageGetResponse", "MessageGetResponseItem"]


class MessageGetResponseItem(BaseModel):
    content: str
    """The textual content of the message."""

    type: str
    """
    Type of the message (e.g., user_message, agent_thinking, agent_response,
    agent_tool_use).
    """


MessageGetResponse: TypeAlias = List[MessageGetResponseItem]
