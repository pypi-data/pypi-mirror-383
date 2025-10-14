# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["BoxResolutionSetParams"]


class BoxResolutionSetParams(TypedDict, total=False):
    height: Required[float]
    """The height of the screen"""

    width: Required[float]
    """The width of the screen"""
