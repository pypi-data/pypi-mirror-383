# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["DetectedElement"]


class DetectedElement(BaseModel):
    id: str
    """Element id"""

    center_x: float = FieldInfo(alias="centerX")
    """Element center x coordinate relative to screen"""

    center_y: float = FieldInfo(alias="centerY")
    """Element center y coordinate relative to screen"""

    height: float
    """Element height"""

    label: str
    """
    A human-readable identifier generated from the element's visible attributes to
    help understand what this element represents. For images, it uses alt text or
    filename; for links, it uses text content or href; for buttons, it uses text
    content or aria-label; for inputs, it uses placeholder or value; etc.
    """

    path: str
    """Element path"""

    source: str
    """Element source"""

    type: str
    """Element type"""

    width: float
    """Element width"""

    x: float
    """Element x coordinate relative to screen"""

    y: float
    """Element y coordinate relative to screen"""
