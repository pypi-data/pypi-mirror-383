# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["BrowserOpenParams"]


class BrowserOpenParams(TypedDict, total=False):
    maximize: bool
    """Whether to maximize the browser window."""

    show_controls: Annotated[bool, PropertyInfo(alias="showControls")]
    """Whether to show the browser's minimize, maximize and close buttons.

    Default is true.
    """

    size: str
    """The window size, format: <width>x<height>.

    If not specified, the browser will open with the default size. If both
    `maximize` and `size` are specified, `maximize` will take precedence.
    """
