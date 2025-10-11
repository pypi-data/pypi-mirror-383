# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ClearMessageClearParams"]


class ClearMessageClearParams(TypedDict, total=False):
    session: Required[str]
    """The session ID to clear messages from."""
