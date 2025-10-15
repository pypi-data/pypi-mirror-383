# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["Message"]


class Message(BaseModel):
    message: str
    """Error message"""

    code: Optional[int] = None
    """Error code"""
