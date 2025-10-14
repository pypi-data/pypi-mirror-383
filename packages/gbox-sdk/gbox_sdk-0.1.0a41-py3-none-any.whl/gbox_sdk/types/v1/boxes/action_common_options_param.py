# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, TypeAlias, TypedDict

from .action_screenshot_options_param import ActionScreenshotOptionsParam

__all__ = ["ActionCommonOptionsParam", "Screenshot"]

Screenshot: TypeAlias = Union[ActionScreenshotOptionsParam, bool]


class ActionCommonOptionsParam(TypedDict, total=False):
    model: Literal["gpt-5", "gpt-4o", "ui-tars", "openai-computer-use"]
    """Model to use for natural-language target resolution. Defaults to 'uitars'."""

    screenshot: Screenshot
    """Screenshot options.

    Can be a boolean to enable/disable screenshots, or an object to configure
    screenshot options.
    """
