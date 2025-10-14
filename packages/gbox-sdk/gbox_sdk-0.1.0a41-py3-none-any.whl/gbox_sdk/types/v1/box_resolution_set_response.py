# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["BoxResolutionSetResponse"]


class BoxResolutionSetResponse(BaseModel):
    height: float
    """Height of the screen"""

    width: float
    """Width of the screen"""
