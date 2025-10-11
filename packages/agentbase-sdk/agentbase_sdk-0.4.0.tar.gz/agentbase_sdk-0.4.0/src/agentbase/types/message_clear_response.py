# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["MessageClearResponse"]


class MessageClearResponse(BaseModel):
    message: Optional[str] = None
    """Human‑readable status message."""

    success: Optional[bool] = None
    """Indicates whether messages were successfully cleared."""
