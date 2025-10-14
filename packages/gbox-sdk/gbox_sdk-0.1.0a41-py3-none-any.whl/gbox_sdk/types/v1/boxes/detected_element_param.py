# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["DetectedElementParam"]


class DetectedElementParam(TypedDict, total=False):
    id: Required[str]
    """Element id"""

    center_x: Required[Annotated[float, PropertyInfo(alias="centerX")]]
    """Element center x coordinate relative to screen"""

    center_y: Required[Annotated[float, PropertyInfo(alias="centerY")]]
    """Element center y coordinate relative to screen"""

    height: Required[float]
    """Element height"""

    label: Required[str]
    """
    A human-readable identifier generated from the element's visible attributes to
    help understand what this element represents. For images, it uses alt text or
    filename; for links, it uses text content or href; for buttons, it uses text
    content or aria-label; for inputs, it uses placeholder or value; etc.
    """

    path: Required[str]
    """Element path"""

    source: Required[str]
    """Element source"""

    type: Required[str]
    """Element type"""

    width: Required[float]
    """Element width"""

    x: Required[float]
    """Element x coordinate relative to screen"""

    y: Required[float]
    """Element y coordinate relative to screen"""
