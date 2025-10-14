# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo
from .detected_element_param import DetectedElementParam
from .action_common_options_param import ActionCommonOptionsParam

__all__ = ["ActionLongPressParams", "LongPress", "LongPressByNaturalLanguage", "LongPressByElement"]


class LongPress(TypedDict, total=False):
    x: Required[float]
    """X coordinate of the long press"""

    y: Required[float]
    """Y coordinate of the long press"""

    duration: str
    """Duration to hold the press (e.g. '1s', '500ms')

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 1s
    """

    include_screenshot: Annotated[bool, PropertyInfo(alias="includeScreenshot")]
    """⚠️ DEPRECATED: Use `options.screenshot.phases` instead.

    This field will be ignored when `options.screenshot` is provided. Whether to
    include screenshots in the action response. If false, the screenshot object will
    still be returned but with empty URIs. Default is false.
    """

    options: ActionCommonOptionsParam
    """Action common options"""

    output_format: Annotated[Literal["base64", "storageKey"], PropertyInfo(alias="outputFormat")]
    """⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead.

    Type of the URI. default is base64. This field will be ignored when
    `options.screenshot` is provided.
    """

    presigned_expires_in: Annotated[str, PropertyInfo(alias="presignedExpiresIn")]
    """⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead.

    Presigned url expires in. Only takes effect when outputFormat is storageKey.
    This field will be ignored when `options.screenshot` is provided.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Annotated[str, PropertyInfo(alias="screenshotDelay")]
    """⚠️ DEPRECATED: Use `options.screenshot.delay` instead.

    This field will be ignored when `options.screenshot` is provided.

    Delay after performing the action, before taking the final screenshot.

    Execution flow:

    1. Take screenshot before action
    2. Perform the action
    3. Wait for screenshotDelay (this parameter)
    4. Take screenshot after action

    Example: '500ms' means wait 500ms after the action before capturing the final
    screenshot.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s
    """


class LongPressByNaturalLanguage(TypedDict, total=False):
    target: Required[str]
    """
    Describe the target to operate using natural language, e.g., 'Chrome icon',
    'login button'
    """

    duration: str
    """Duration to hold the press (e.g. '1s', '500ms')

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 1s
    """

    include_screenshot: Annotated[bool, PropertyInfo(alias="includeScreenshot")]
    """⚠️ DEPRECATED: Use `options.screenshot.phases` instead.

    This field will be ignored when `options.screenshot` is provided. Whether to
    include screenshots in the action response. If false, the screenshot object will
    still be returned but with empty URIs. Default is false.
    """

    options: ActionCommonOptionsParam
    """Action common options"""

    output_format: Annotated[Literal["base64", "storageKey"], PropertyInfo(alias="outputFormat")]
    """⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead.

    Type of the URI. default is base64. This field will be ignored when
    `options.screenshot` is provided.
    """

    presigned_expires_in: Annotated[str, PropertyInfo(alias="presignedExpiresIn")]
    """⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead.

    Presigned url expires in. Only takes effect when outputFormat is storageKey.
    This field will be ignored when `options.screenshot` is provided.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Annotated[str, PropertyInfo(alias="screenshotDelay")]
    """⚠️ DEPRECATED: Use `options.screenshot.delay` instead.

    This field will be ignored when `options.screenshot` is provided.

    Delay after performing the action, before taking the final screenshot.

    Execution flow:

    1. Take screenshot before action
    2. Perform the action
    3. Wait for screenshotDelay (this parameter)
    4. Take screenshot after action

    Example: '500ms' means wait 500ms after the action before capturing the final
    screenshot.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s
    """


class LongPressByElement(TypedDict, total=False):
    target: Required[DetectedElementParam]
    """Detected UI element"""

    duration: str
    """Duration to hold the press (e.g. '1s', '500ms')

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 1s
    """

    include_screenshot: Annotated[bool, PropertyInfo(alias="includeScreenshot")]
    """⚠️ DEPRECATED: Use `options.screenshot.phases` instead.

    This field will be ignored when `options.screenshot` is provided. Whether to
    include screenshots in the action response. If false, the screenshot object will
    still be returned but with empty URIs. Default is false.
    """

    options: ActionCommonOptionsParam
    """Action common options"""

    output_format: Annotated[Literal["base64", "storageKey"], PropertyInfo(alias="outputFormat")]
    """⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead.

    Type of the URI. default is base64. This field will be ignored when
    `options.screenshot` is provided.
    """

    presigned_expires_in: Annotated[str, PropertyInfo(alias="presignedExpiresIn")]
    """⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead.

    Presigned url expires in. Only takes effect when outputFormat is storageKey.
    This field will be ignored when `options.screenshot` is provided.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Annotated[str, PropertyInfo(alias="screenshotDelay")]
    """⚠️ DEPRECATED: Use `options.screenshot.delay` instead.

    This field will be ignored when `options.screenshot` is provided.

    Delay after performing the action, before taking the final screenshot.

    Execution flow:

    1. Take screenshot before action
    2. Perform the action
    3. Wait for screenshotDelay (this parameter)
    4. Take screenshot after action

    Example: '500ms' means wait 500ms after the action before capturing the final
    screenshot.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s
    """


ActionLongPressParams: TypeAlias = Union[LongPress, LongPressByNaturalLanguage, LongPressByElement]
