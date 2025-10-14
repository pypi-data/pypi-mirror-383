# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable
from typing_extensions import Literal, overload

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ...._utils import required_args, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.boxes import (
    action_tap_params,
    action_drag_params,
    action_move_params,
    action_type_params,
    action_click_params,
    action_swipe_params,
    action_touch_params,
    action_scroll_params,
    action_extract_params,
    action_press_key_params,
    action_long_press_params,
    action_screenshot_params,
    action_press_button_params,
    action_clipboard_set_params,
    action_rewind_extract_params,
    action_elements_detect_params,
    action_screen_rotation_params,
    action_settings_update_params,
)
from ....types.v1.boxes.action_result import ActionResult
from ....types.v1.boxes.detected_element import DetectedElement
from ....types.v1.boxes.action_extract_response import ActionExtractResponse
from ....types.v1.boxes.action_settings_response import ActionSettingsResponse
from ....types.v1.boxes.action_screenshot_response import ActionScreenshotResponse
from ....types.v1.boxes.action_common_options_param import ActionCommonOptionsParam
from ....types.v1.boxes.action_screen_layout_response import ActionScreenLayoutResponse
from ....types.v1.boxes.action_recording_stop_response import ActionRecordingStopResponse
from ....types.v1.boxes.action_rewind_extract_response import ActionRewindExtractResponse
from ....types.v1.boxes.action_settings_reset_response import ActionSettingsResetResponse
from ....types.v1.boxes.action_elements_detect_response import ActionElementsDetectResponse
from ....types.v1.boxes.action_settings_update_response import ActionSettingsUpdateResponse

__all__ = ["ActionsResource", "AsyncActionsResource"]


class ActionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ActionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return ActionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ActionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return ActionsResourceWithStreamingResponse(self)

    @overload
    def click(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        button: Literal["left", "right", "middle"] | Omit = omit,
        double: bool | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Simulates a click action on the box

        Args:
          x: X coordinate of the click

          y: Y coordinate of the click

          button: Mouse button to click

          double: Whether to perform a double click

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def click(
        self,
        box_id: str,
        *,
        target: str,
        button: Literal["left", "right", "middle"] | Omit = omit,
        double: bool | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Simulates a click action on the box

        Args:
          target: Describe the target to operate using natural language, e.g., 'login button' or
              'Chrome'.

          button: Mouse button to click

          double: Whether to perform a double click

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def click(
        self,
        box_id: str,
        *,
        target: DetectedElement,
        button: Literal["left", "right", "middle"] | Omit = omit,
        double: bool | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Simulates a click action on the box

        Args:
          target: Detected UI element

          button: Mouse button to click

          double: Whether to perform a double click

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["x", "y"], ["target"])
    def click(
        self,
        box_id: str,
        *,
        x: float | Omit = omit,
        y: float | Omit = omit,
        button: Literal["left", "right", "middle"] | Omit = omit,
        double: bool | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        target: str | DetectedElement | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/click",
            body=maybe_transform(
                {
                    "x": x,
                    "y": y,
                    "button": button,
                    "double": double,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                    "target": target,
                },
                action_click_params.ActionClickParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    def clipboard_get(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> str:
        """
        Get the clipboard content

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/actions/clipboard",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )

    def clipboard_set(
        self,
        box_id: str,
        *,
        content: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Set the clipboard content

        Args:
          content: The content to set the clipboard content

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/actions/clipboard",
            body=maybe_transform({"content": content}, action_clipboard_set_params.ActionClipboardSetParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    @overload
    def drag(
        self,
        box_id: str,
        *,
        end: action_drag_params.DragSimpleEnd,
        start: action_drag_params.DragSimpleStart,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Simulates a drag gesture, moving from a start point to an end point over a set
        duration. Supports simple start/end coordinates, multi-point drag paths, and
        natural-language targets.

        Args:
          end: End point of the drag path (coordinates or natural language)

          start: Start point of the drag path (coordinates or natural language)

          duration: Duration to complete the movement from start to end coordinates

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def drag(
        self,
        box_id: str,
        *,
        path: Iterable[action_drag_params.DragAdvancedPath],
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Simulates a drag gesture, moving from a start point to an end point over a set
        duration. Supports simple start/end coordinates, multi-point drag paths, and
        natural-language targets.

        Args:
          path: Path of the drag action as a series of coordinates

          duration: Time interval between points (e.g. "50ms")

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 50ms

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["end", "start"], ["path"])
    def drag(
        self,
        box_id: str,
        *,
        end: action_drag_params.DragSimpleEnd | Omit = omit,
        start: action_drag_params.DragSimpleStart | Omit = omit,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        path: Iterable[action_drag_params.DragAdvancedPath] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/drag",
            body=maybe_transform(
                {
                    "end": end,
                    "start": start,
                    "duration": duration,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                    "path": path,
                },
                action_drag_params.ActionDragParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    def elements_detect(
        self,
        box_id: str,
        *,
        screenshot: action_elements_detect_params.Screenshot | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionElementsDetectResponse:
        """Detect and identify interactive UI elements in the current screen.

        Note: This
        feature currently only supports element detection within a running browser. If
        the browser is not running, the Elements array will be empty.

        Args:
          screenshot: Detect elements screenshot options

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/elements/detect",
            body=maybe_transform({"screenshot": screenshot}, action_elements_detect_params.ActionElementsDetectParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionElementsDetectResponse,
        )

    def extract(
        self,
        box_id: str,
        *,
        instruction: str,
        schema: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionExtractResponse:
        """
        Extract data from the UI interface using a JSON schema.

        Args:
          instruction: The instruction of the action to extract data from the UI interface

          schema: JSON Schema defining the structure of data to extract. Supports object, array,
              string, number, boolean types with validation rules.

              Common use cases:

              - Extract text content: { "type": "string" }
              - Extract structured data: { "type": "object", "properties": {...} }
              - Extract lists: { "type": "array", "items": {...} }
              - Extract with validation: Add constraints like "required", "enum", "pattern",
                etc.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/extract",
            body=maybe_transform(
                {
                    "instruction": instruction,
                    "schema": schema,
                },
                action_extract_params.ActionExtractParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionExtractResponse,
        )

    @overload
    def long_press(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Perform a long press action at specified coordinates for a specified duration.
        Useful for triggering context menus, drag operations, or other long-press
        interactions.

        Args:
          x: X coordinate of the long press

          y: Y coordinate of the long press

          duration: Duration to hold the press (e.g. '1s', '500ms')

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 1s

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def long_press(
        self,
        box_id: str,
        *,
        target: str,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Perform a long press action at specified coordinates for a specified duration.
        Useful for triggering context menus, drag operations, or other long-press
        interactions.

        Args:
          target: Describe the target to operate using natural language, e.g., 'Chrome icon',
              'login button'

          duration: Duration to hold the press (e.g. '1s', '500ms')

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 1s

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def long_press(
        self,
        box_id: str,
        *,
        target: DetectedElement,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Perform a long press action at specified coordinates for a specified duration.
        Useful for triggering context menus, drag operations, or other long-press
        interactions.

        Args:
          target: Detected UI element

          duration: Duration to hold the press (e.g. '1s', '500ms')

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 1s

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["x", "y"], ["target"])
    def long_press(
        self,
        box_id: str,
        *,
        x: float | Omit = omit,
        y: float | Omit = omit,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        target: str | DetectedElement | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/long-press",
            body=maybe_transform(
                {
                    "x": x,
                    "y": y,
                    "duration": duration,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                    "target": target,
                },
                action_long_press_params.ActionLongPressParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    def move(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Moves the focus to a specific coordinate on the box without performing a click
        or tap. Use this endpoint to position the cursor, hover over elements, or
        prepare for chained actions such as drag or swipe.

        Args:
          x: X coordinate to move to

          y: Y coordinate to move to

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/move",
            body=maybe_transform(
                {
                    "x": x,
                    "y": y,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                },
                action_move_params.ActionMoveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    def press_button(
        self,
        box_id: str,
        *,
        buttons: List[Literal["power", "volumeUp", "volumeDown", "volumeMute", "home", "back", "menu", "appSwitch"]],
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Press device buttons like power, volume, home, back, etc.

        Args:
          buttons: Button to press

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/press-button",
            body=maybe_transform(
                {
                    "buttons": buttons,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                },
                action_press_button_params.ActionPressButtonParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    def press_key(
        self,
        box_id: str,
        *,
        keys: List[
            Literal[
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
                "g",
                "h",
                "i",
                "j",
                "k",
                "l",
                "m",
                "n",
                "o",
                "p",
                "q",
                "r",
                "s",
                "t",
                "u",
                "v",
                "w",
                "x",
                "y",
                "z",
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "f1",
                "f2",
                "f3",
                "f4",
                "f5",
                "f6",
                "f7",
                "f8",
                "f9",
                "f10",
                "f11",
                "f12",
                "control",
                "alt",
                "shift",
                "meta",
                "win",
                "cmd",
                "option",
                "arrowUp",
                "arrowDown",
                "arrowLeft",
                "arrowRight",
                "home",
                "end",
                "pageUp",
                "pageDown",
                "enter",
                "space",
                "tab",
                "escape",
                "backspace",
                "delete",
                "insert",
                "capsLock",
                "numLock",
                "scrollLock",
                "pause",
                "printScreen",
                ";",
                "=",
                ",",
                "-",
                ".",
                "/",
                "`",
                "[",
                "\\",
                "]",
                "'",
                "numpad0",
                "numpad1",
                "numpad2",
                "numpad3",
                "numpad4",
                "numpad5",
                "numpad6",
                "numpad7",
                "numpad8",
                "numpad9",
                "numpadAdd",
                "numpadSubtract",
                "numpadMultiply",
                "numpadDivide",
                "numpadDecimal",
                "numpadEnter",
                "numpadEqual",
                "volumeUp",
                "volumeDown",
                "volumeMute",
                "mediaPlayPause",
                "mediaStop",
                "mediaNextTrack",
                "mediaPreviousTrack",
            ]
        ],
        combination: bool | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Simulates pressing a specific key by triggering the complete keyboard key event
        chain (keydown, keypress, keyup). Use this to activate keyboard key event
        listeners such as shortcuts or form submissions.

        Args:
          keys: This is an array of keyboard keys to press. Supports cross-platform
              compatibility.

          combination: Whether to press keys as combination (simultaneously) or sequentially. When
              true, all keys are pressed together as a shortcut (e.g., Ctrl+C). When false,
              keys are pressed one by one in sequence.

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/press-key",
            body=maybe_transform(
                {
                    "keys": keys,
                    "combination": combination,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                },
                action_press_key_params.ActionPressKeyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    def recording_start(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Start recording the box screen.

        Only one recording can be active at a time. If a
        recording is already in progress, starting a new recording will stop the
        previous one and keep only the latest recording.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/actions/recording/start",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def recording_stop(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionRecordingStopResponse:
        """
        Stop recording the box screen

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/recording/stop",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionRecordingStopResponse,
        )

    def rewind_disable(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Disable the device's background screen rewind recording.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/boxes/{box_id}/actions/recording/rewind",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def rewind_enable(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Enable the device's background screen rewind recording.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/actions/recording/rewind",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def rewind_extract(
        self,
        box_id: str,
        *,
        duration: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionRewindExtractResponse:
        """
        Rewind and capture the device's background screen recording from a specified
        time period.

        Args:
          duration: How far back in time to rewind for extracting recorded video. This specifies the
              duration to go back from the current moment (e.g., '30s' rewinds 30 seconds to
              get recent recorded activity). Default is 30s, max is 5m.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Maximum allowed: 5m

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/recording/rewind/extract",
            body=maybe_transform({"duration": duration}, action_rewind_extract_params.ActionRewindExtractParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionRewindExtractResponse,
        )

    def screen_layout(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionScreenLayoutResponse:
        """Get the current structured screen layout information.

        This endpoint returns
        detailed structural information about the UI elements currently displayed on the
        screen, which can be used for UI automation, element analysis, and accessibility
        purposes. The format varies by box type: Android boxes return XML format with
        detailed UI hierarchy information including element bounds, text content,
        resource IDs, and properties, while other box types may return different
        structured formats.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/actions/screen-layout",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionScreenLayoutResponse,
        )

    def screen_rotation(
        self,
        box_id: str,
        *,
        orientation: Literal["portrait", "landscapeLeft", "portraitUpsideDown", "landscapeRight"],
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """Rotates the screen orientation.

        Note that even after rotating the screen,
        applications or system layouts may not automatically adapt to the gravity sensor
        changes, so visual changes may not always occur.

        Args:
          orientation: Target screen orientation

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/screen-rotation",
            body=maybe_transform(
                {
                    "orientation": orientation,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                },
                action_screen_rotation_params.ActionScreenRotationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    def screenshot(
        self,
        box_id: str,
        *,
        clip: action_screenshot_params.Clip | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        save_to_album: bool | Omit = omit,
        scroll_capture: action_screenshot_params.ScrollCapture | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionScreenshotResponse:
        """
        Captures a screenshot of the current box screen

        Args:
          clip: Clipping region for screenshot capture

          output_format: Type of the URI. default is base64.

          presigned_expires_in: Presigned url expires in. Only takes effect when outputFormat is storageKey.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          save_to_album: Whether to save the screenshot to the device screenshot album

          scroll_capture: Scroll capture parameters

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/screenshot",
            body=maybe_transform(
                {
                    "clip": clip,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "save_to_album": save_to_album,
                    "scroll_capture": scroll_capture,
                },
                action_screenshot_params.ActionScreenshotParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionScreenshotResponse,
        )

    @overload
    def scroll(
        self,
        box_id: str,
        *,
        scroll_x: float,
        scroll_y: float,
        x: float,
        y: float,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """Performs a scroll action.

        Supports both advanced scroll with coordinates and
        simple scroll with direction.

        Args:
          scroll_x: Horizontal scroll amount. Positive values scroll content rightward (reveals
              content on the right), negative values scroll content leftward (reveals content
              on the left).

          scroll_y: Vertical scroll amount. Positive values scroll content downward (reveals content
              below), negative values scroll content upward (reveals content above).

          x: X coordinate of the scroll position

          y: Y coordinate of the scroll position

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def scroll(
        self,
        box_id: str,
        *,
        direction: Literal["up", "down", "left", "right"],
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | Omit = omit,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        location: str | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """Performs a scroll action.

        Supports both advanced scroll with coordinates and
        simple scroll with direction.

        Args:
          direction: Direction to scroll. The scroll will be performed from the center of the screen
              towards this direction. 'up' scrolls content upward (reveals content below),
              'down' scrolls content downward (reveals content above), 'left' scrolls content
              leftward (reveals content on the right), 'right' scrolls content rightward
              (reveals content on the left).

          distance: Distance of the scroll. Can be either a number (in pixels) or a predefined enum
              value (tiny, short, medium, long). If not provided, the scroll will be performed
              from the center of the screen to the screen edge

          duration: Duration of the scroll

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          location: Natural language description of the location where the scroll should originate.
              If not provided, the scroll will be performed from the center of the screen.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["scroll_x", "scroll_y", "x", "y"], ["direction"])
    def scroll(
        self,
        box_id: str,
        *,
        scroll_x: float | Omit = omit,
        scroll_y: float | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        direction: Literal["up", "down", "left", "right"] | Omit = omit,
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | Omit = omit,
        duration: str | Omit = omit,
        location: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/scroll",
            body=maybe_transform(
                {
                    "scroll_x": scroll_x,
                    "scroll_y": scroll_y,
                    "x": x,
                    "y": y,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                    "direction": direction,
                    "distance": distance,
                    "duration": duration,
                    "location": location,
                },
                action_scroll_params.ActionScrollParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    def settings(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionSettingsResponse:
        """
        Get the action settings for the box

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/actions/settings",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionSettingsResponse,
        )

    def settings_reset(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionSettingsResetResponse:
        """
        Resets the box settings to default

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._delete(
            f"/boxes/{box_id}/actions/settings",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionSettingsResetResponse,
        )

    def settings_update(
        self,
        box_id: str,
        *,
        scale: float,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionSettingsUpdateResponse:
        """
        Update the action settings for the box

        Args:
          scale: The scale of the action to be performed. Must be greater than 0.1 and less than
              or equal to 1.

              Notes:

              - Scale does not change the box's actual screen resolution.
              - It affects the size of the output screenshot and the coordinates/distances of
                actions. Coordinates and distances are scaled by this factor. Example: when
                scale = 1, Click({x:100, y:100}); when scale = 0.5, the equivalent position is
                Click({x:50, y:50}).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._put(
            f"/boxes/{box_id}/actions/settings",
            body=maybe_transform({"scale": scale}, action_settings_update_params.ActionSettingsUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionSettingsUpdateResponse,
        )

    @overload
    def swipe(
        self,
        box_id: str,
        *,
        direction: Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"],
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | Omit = omit,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        location: str | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Performs a swipe in the specified direction

        Args:
          direction: Direction to swipe. The gesture will be performed from the center of the screen
              towards this direction.

          distance: Distance of the swipe. Can be either a number (in pixels) or a predefined enum
              value (tiny, short, medium, long). If not provided, the swipe will be performed
              from the center of the screen to the screen edge

          duration: Duration of the swipe

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          location: Natural language description of the location where the swipe should originate.
              If not provided, the swipe will be performed from the center of the screen.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def swipe(
        self,
        box_id: str,
        *,
        end: action_swipe_params.SwipeAdvancedEnd,
        start: action_swipe_params.SwipeAdvancedStart,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Performs a swipe in the specified direction

        Args:
          end: End point of the swipe path (coordinates or natural language)

          start: Start point of the swipe path (coordinates or natural language)

          duration: Duration of the swipe

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["direction"], ["end", "start"])
    def swipe(
        self,
        box_id: str,
        *,
        direction: Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"] | Omit = omit,
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | Omit = omit,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        location: str | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        end: action_swipe_params.SwipeAdvancedEnd | Omit = omit,
        start: action_swipe_params.SwipeAdvancedStart | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/swipe",
            body=maybe_transform(
                {
                    "direction": direction,
                    "distance": distance,
                    "duration": duration,
                    "include_screenshot": include_screenshot,
                    "location": location,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                    "end": end,
                    "start": start,
                },
                action_swipe_params.ActionSwipeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    @overload
    def tap(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Tap action for Android devices using ADB input tap command

        Args:
          x: X coordinate of the tap

          y: Y coordinate of the tap

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def tap(
        self,
        box_id: str,
        *,
        target: str,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Tap action for Android devices using ADB input tap command

        Args:
          target: Describe the target to operate using natural language, e.g., 'login button' or
              'Chrome'.

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def tap(
        self,
        box_id: str,
        *,
        target: DetectedElement,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Tap action for Android devices using ADB input tap command

        Args:
          target: Detected UI element

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["x", "y"], ["target"])
    def tap(
        self,
        box_id: str,
        *,
        x: float | Omit = omit,
        y: float | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        target: str | DetectedElement | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/tap",
            body=maybe_transform(
                {
                    "x": x,
                    "y": y,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                    "target": target,
                },
                action_tap_params.ActionTapParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    def touch(
        self,
        box_id: str,
        *,
        points: Iterable[action_touch_params.Point],
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """Performs more advanced touch gestures.

        Use this endpoint to simulate realistic
        behaviors.

        Args:
          points: Array of touch points and their actions

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/touch",
            body=maybe_transform(
                {
                    "points": points,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                },
                action_touch_params.ActionTouchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    def type(
        self,
        box_id: str,
        *,
        text: str,
        include_screenshot: bool | Omit = omit,
        mode: Literal["append", "replace"] | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        press_enter: bool | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Directly inputs text content without triggering physical key events (keydown,
        etc.), ideal for quickly filling large amounts of text when intermediate input
        events aren't needed.

        Args:
          text: Text to type

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          mode: Text input mode: 'append' to add text to existing content, 'replace' to replace
              all existing text

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          press_enter: Whether to press Enter after typing the text

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/actions/type",
            body=maybe_transform(
                {
                    "text": text,
                    "include_screenshot": include_screenshot,
                    "mode": mode,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "press_enter": press_enter,
                    "screenshot_delay": screenshot_delay,
                },
                action_type_params.ActionTypeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )


class AsyncActionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncActionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncActionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncActionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return AsyncActionsResourceWithStreamingResponse(self)

    @overload
    async def click(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        button: Literal["left", "right", "middle"] | Omit = omit,
        double: bool | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Simulates a click action on the box

        Args:
          x: X coordinate of the click

          y: Y coordinate of the click

          button: Mouse button to click

          double: Whether to perform a double click

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def click(
        self,
        box_id: str,
        *,
        target: str,
        button: Literal["left", "right", "middle"] | Omit = omit,
        double: bool | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Simulates a click action on the box

        Args:
          target: Describe the target to operate using natural language, e.g., 'login button' or
              'Chrome'.

          button: Mouse button to click

          double: Whether to perform a double click

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def click(
        self,
        box_id: str,
        *,
        target: DetectedElement,
        button: Literal["left", "right", "middle"] | Omit = omit,
        double: bool | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Simulates a click action on the box

        Args:
          target: Detected UI element

          button: Mouse button to click

          double: Whether to perform a double click

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["x", "y"], ["target"])
    async def click(
        self,
        box_id: str,
        *,
        x: float | Omit = omit,
        y: float | Omit = omit,
        button: Literal["left", "right", "middle"] | Omit = omit,
        double: bool | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        target: str | DetectedElement | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/click",
            body=await async_maybe_transform(
                {
                    "x": x,
                    "y": y,
                    "button": button,
                    "double": double,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                    "target": target,
                },
                action_click_params.ActionClickParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    async def clipboard_get(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> str:
        """
        Get the clipboard content

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/actions/clipboard",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )

    async def clipboard_set(
        self,
        box_id: str,
        *,
        content: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Set the clipboard content

        Args:
          content: The content to set the clipboard content

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/actions/clipboard",
            body=await async_maybe_transform(
                {"content": content}, action_clipboard_set_params.ActionClipboardSetParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    @overload
    async def drag(
        self,
        box_id: str,
        *,
        end: action_drag_params.DragSimpleEnd,
        start: action_drag_params.DragSimpleStart,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Simulates a drag gesture, moving from a start point to an end point over a set
        duration. Supports simple start/end coordinates, multi-point drag paths, and
        natural-language targets.

        Args:
          end: End point of the drag path (coordinates or natural language)

          start: Start point of the drag path (coordinates or natural language)

          duration: Duration to complete the movement from start to end coordinates

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def drag(
        self,
        box_id: str,
        *,
        path: Iterable[action_drag_params.DragAdvancedPath],
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Simulates a drag gesture, moving from a start point to an end point over a set
        duration. Supports simple start/end coordinates, multi-point drag paths, and
        natural-language targets.

        Args:
          path: Path of the drag action as a series of coordinates

          duration: Time interval between points (e.g. "50ms")

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 50ms

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["end", "start"], ["path"])
    async def drag(
        self,
        box_id: str,
        *,
        end: action_drag_params.DragSimpleEnd | Omit = omit,
        start: action_drag_params.DragSimpleStart | Omit = omit,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        path: Iterable[action_drag_params.DragAdvancedPath] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/drag",
            body=await async_maybe_transform(
                {
                    "end": end,
                    "start": start,
                    "duration": duration,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                    "path": path,
                },
                action_drag_params.ActionDragParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    async def elements_detect(
        self,
        box_id: str,
        *,
        screenshot: action_elements_detect_params.Screenshot | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionElementsDetectResponse:
        """Detect and identify interactive UI elements in the current screen.

        Note: This
        feature currently only supports element detection within a running browser. If
        the browser is not running, the Elements array will be empty.

        Args:
          screenshot: Detect elements screenshot options

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/elements/detect",
            body=await async_maybe_transform(
                {"screenshot": screenshot}, action_elements_detect_params.ActionElementsDetectParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionElementsDetectResponse,
        )

    async def extract(
        self,
        box_id: str,
        *,
        instruction: str,
        schema: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionExtractResponse:
        """
        Extract data from the UI interface using a JSON schema.

        Args:
          instruction: The instruction of the action to extract data from the UI interface

          schema: JSON Schema defining the structure of data to extract. Supports object, array,
              string, number, boolean types with validation rules.

              Common use cases:

              - Extract text content: { "type": "string" }
              - Extract structured data: { "type": "object", "properties": {...} }
              - Extract lists: { "type": "array", "items": {...} }
              - Extract with validation: Add constraints like "required", "enum", "pattern",
                etc.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/extract",
            body=await async_maybe_transform(
                {
                    "instruction": instruction,
                    "schema": schema,
                },
                action_extract_params.ActionExtractParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionExtractResponse,
        )

    @overload
    async def long_press(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Perform a long press action at specified coordinates for a specified duration.
        Useful for triggering context menus, drag operations, or other long-press
        interactions.

        Args:
          x: X coordinate of the long press

          y: Y coordinate of the long press

          duration: Duration to hold the press (e.g. '1s', '500ms')

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 1s

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def long_press(
        self,
        box_id: str,
        *,
        target: str,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Perform a long press action at specified coordinates for a specified duration.
        Useful for triggering context menus, drag operations, or other long-press
        interactions.

        Args:
          target: Describe the target to operate using natural language, e.g., 'Chrome icon',
              'login button'

          duration: Duration to hold the press (e.g. '1s', '500ms')

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 1s

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def long_press(
        self,
        box_id: str,
        *,
        target: DetectedElement,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Perform a long press action at specified coordinates for a specified duration.
        Useful for triggering context menus, drag operations, or other long-press
        interactions.

        Args:
          target: Detected UI element

          duration: Duration to hold the press (e.g. '1s', '500ms')

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 1s

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["x", "y"], ["target"])
    async def long_press(
        self,
        box_id: str,
        *,
        x: float | Omit = omit,
        y: float | Omit = omit,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        target: str | DetectedElement | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/long-press",
            body=await async_maybe_transform(
                {
                    "x": x,
                    "y": y,
                    "duration": duration,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                    "target": target,
                },
                action_long_press_params.ActionLongPressParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    async def move(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Moves the focus to a specific coordinate on the box without performing a click
        or tap. Use this endpoint to position the cursor, hover over elements, or
        prepare for chained actions such as drag or swipe.

        Args:
          x: X coordinate to move to

          y: Y coordinate to move to

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/move",
            body=await async_maybe_transform(
                {
                    "x": x,
                    "y": y,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                },
                action_move_params.ActionMoveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    async def press_button(
        self,
        box_id: str,
        *,
        buttons: List[Literal["power", "volumeUp", "volumeDown", "volumeMute", "home", "back", "menu", "appSwitch"]],
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Press device buttons like power, volume, home, back, etc.

        Args:
          buttons: Button to press

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/press-button",
            body=await async_maybe_transform(
                {
                    "buttons": buttons,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                },
                action_press_button_params.ActionPressButtonParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    async def press_key(
        self,
        box_id: str,
        *,
        keys: List[
            Literal[
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
                "g",
                "h",
                "i",
                "j",
                "k",
                "l",
                "m",
                "n",
                "o",
                "p",
                "q",
                "r",
                "s",
                "t",
                "u",
                "v",
                "w",
                "x",
                "y",
                "z",
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "f1",
                "f2",
                "f3",
                "f4",
                "f5",
                "f6",
                "f7",
                "f8",
                "f9",
                "f10",
                "f11",
                "f12",
                "control",
                "alt",
                "shift",
                "meta",
                "win",
                "cmd",
                "option",
                "arrowUp",
                "arrowDown",
                "arrowLeft",
                "arrowRight",
                "home",
                "end",
                "pageUp",
                "pageDown",
                "enter",
                "space",
                "tab",
                "escape",
                "backspace",
                "delete",
                "insert",
                "capsLock",
                "numLock",
                "scrollLock",
                "pause",
                "printScreen",
                ";",
                "=",
                ",",
                "-",
                ".",
                "/",
                "`",
                "[",
                "\\",
                "]",
                "'",
                "numpad0",
                "numpad1",
                "numpad2",
                "numpad3",
                "numpad4",
                "numpad5",
                "numpad6",
                "numpad7",
                "numpad8",
                "numpad9",
                "numpadAdd",
                "numpadSubtract",
                "numpadMultiply",
                "numpadDivide",
                "numpadDecimal",
                "numpadEnter",
                "numpadEqual",
                "volumeUp",
                "volumeDown",
                "volumeMute",
                "mediaPlayPause",
                "mediaStop",
                "mediaNextTrack",
                "mediaPreviousTrack",
            ]
        ],
        combination: bool | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Simulates pressing a specific key by triggering the complete keyboard key event
        chain (keydown, keypress, keyup). Use this to activate keyboard key event
        listeners such as shortcuts or form submissions.

        Args:
          keys: This is an array of keyboard keys to press. Supports cross-platform
              compatibility.

          combination: Whether to press keys as combination (simultaneously) or sequentially. When
              true, all keys are pressed together as a shortcut (e.g., Ctrl+C). When false,
              keys are pressed one by one in sequence.

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/press-key",
            body=await async_maybe_transform(
                {
                    "keys": keys,
                    "combination": combination,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                },
                action_press_key_params.ActionPressKeyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    async def recording_start(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Start recording the box screen.

        Only one recording can be active at a time. If a
        recording is already in progress, starting a new recording will stop the
        previous one and keep only the latest recording.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/actions/recording/start",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def recording_stop(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionRecordingStopResponse:
        """
        Stop recording the box screen

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/recording/stop",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionRecordingStopResponse,
        )

    async def rewind_disable(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Disable the device's background screen rewind recording.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/boxes/{box_id}/actions/recording/rewind",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def rewind_enable(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Enable the device's background screen rewind recording.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/actions/recording/rewind",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def rewind_extract(
        self,
        box_id: str,
        *,
        duration: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionRewindExtractResponse:
        """
        Rewind and capture the device's background screen recording from a specified
        time period.

        Args:
          duration: How far back in time to rewind for extracting recorded video. This specifies the
              duration to go back from the current moment (e.g., '30s' rewinds 30 seconds to
              get recent recorded activity). Default is 30s, max is 5m.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Maximum allowed: 5m

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/recording/rewind/extract",
            body=await async_maybe_transform(
                {"duration": duration}, action_rewind_extract_params.ActionRewindExtractParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionRewindExtractResponse,
        )

    async def screen_layout(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionScreenLayoutResponse:
        """Get the current structured screen layout information.

        This endpoint returns
        detailed structural information about the UI elements currently displayed on the
        screen, which can be used for UI automation, element analysis, and accessibility
        purposes. The format varies by box type: Android boxes return XML format with
        detailed UI hierarchy information including element bounds, text content,
        resource IDs, and properties, while other box types may return different
        structured formats.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/actions/screen-layout",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionScreenLayoutResponse,
        )

    async def screen_rotation(
        self,
        box_id: str,
        *,
        orientation: Literal["portrait", "landscapeLeft", "portraitUpsideDown", "landscapeRight"],
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """Rotates the screen orientation.

        Note that even after rotating the screen,
        applications or system layouts may not automatically adapt to the gravity sensor
        changes, so visual changes may not always occur.

        Args:
          orientation: Target screen orientation

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/screen-rotation",
            body=await async_maybe_transform(
                {
                    "orientation": orientation,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                },
                action_screen_rotation_params.ActionScreenRotationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    async def screenshot(
        self,
        box_id: str,
        *,
        clip: action_screenshot_params.Clip | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        save_to_album: bool | Omit = omit,
        scroll_capture: action_screenshot_params.ScrollCapture | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionScreenshotResponse:
        """
        Captures a screenshot of the current box screen

        Args:
          clip: Clipping region for screenshot capture

          output_format: Type of the URI. default is base64.

          presigned_expires_in: Presigned url expires in. Only takes effect when outputFormat is storageKey.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          save_to_album: Whether to save the screenshot to the device screenshot album

          scroll_capture: Scroll capture parameters

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/screenshot",
            body=await async_maybe_transform(
                {
                    "clip": clip,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "save_to_album": save_to_album,
                    "scroll_capture": scroll_capture,
                },
                action_screenshot_params.ActionScreenshotParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionScreenshotResponse,
        )

    @overload
    async def scroll(
        self,
        box_id: str,
        *,
        scroll_x: float,
        scroll_y: float,
        x: float,
        y: float,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """Performs a scroll action.

        Supports both advanced scroll with coordinates and
        simple scroll with direction.

        Args:
          scroll_x: Horizontal scroll amount. Positive values scroll content rightward (reveals
              content on the right), negative values scroll content leftward (reveals content
              on the left).

          scroll_y: Vertical scroll amount. Positive values scroll content downward (reveals content
              below), negative values scroll content upward (reveals content above).

          x: X coordinate of the scroll position

          y: Y coordinate of the scroll position

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def scroll(
        self,
        box_id: str,
        *,
        direction: Literal["up", "down", "left", "right"],
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | Omit = omit,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        location: str | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """Performs a scroll action.

        Supports both advanced scroll with coordinates and
        simple scroll with direction.

        Args:
          direction: Direction to scroll. The scroll will be performed from the center of the screen
              towards this direction. 'up' scrolls content upward (reveals content below),
              'down' scrolls content downward (reveals content above), 'left' scrolls content
              leftward (reveals content on the right), 'right' scrolls content rightward
              (reveals content on the left).

          distance: Distance of the scroll. Can be either a number (in pixels) or a predefined enum
              value (tiny, short, medium, long). If not provided, the scroll will be performed
              from the center of the screen to the screen edge

          duration: Duration of the scroll

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          location: Natural language description of the location where the scroll should originate.
              If not provided, the scroll will be performed from the center of the screen.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["scroll_x", "scroll_y", "x", "y"], ["direction"])
    async def scroll(
        self,
        box_id: str,
        *,
        scroll_x: float | Omit = omit,
        scroll_y: float | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        direction: Literal["up", "down", "left", "right"] | Omit = omit,
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | Omit = omit,
        duration: str | Omit = omit,
        location: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/scroll",
            body=await async_maybe_transform(
                {
                    "scroll_x": scroll_x,
                    "scroll_y": scroll_y,
                    "x": x,
                    "y": y,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                    "direction": direction,
                    "distance": distance,
                    "duration": duration,
                    "location": location,
                },
                action_scroll_params.ActionScrollParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    async def settings(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionSettingsResponse:
        """
        Get the action settings for the box

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/actions/settings",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionSettingsResponse,
        )

    async def settings_reset(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionSettingsResetResponse:
        """
        Resets the box settings to default

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._delete(
            f"/boxes/{box_id}/actions/settings",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionSettingsResetResponse,
        )

    async def settings_update(
        self,
        box_id: str,
        *,
        scale: float,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionSettingsUpdateResponse:
        """
        Update the action settings for the box

        Args:
          scale: The scale of the action to be performed. Must be greater than 0.1 and less than
              or equal to 1.

              Notes:

              - Scale does not change the box's actual screen resolution.
              - It affects the size of the output screenshot and the coordinates/distances of
                actions. Coordinates and distances are scaled by this factor. Example: when
                scale = 1, Click({x:100, y:100}); when scale = 0.5, the equivalent position is
                Click({x:50, y:50}).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._put(
            f"/boxes/{box_id}/actions/settings",
            body=await async_maybe_transform(
                {"scale": scale}, action_settings_update_params.ActionSettingsUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionSettingsUpdateResponse,
        )

    @overload
    async def swipe(
        self,
        box_id: str,
        *,
        direction: Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"],
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | Omit = omit,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        location: str | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Performs a swipe in the specified direction

        Args:
          direction: Direction to swipe. The gesture will be performed from the center of the screen
              towards this direction.

          distance: Distance of the swipe. Can be either a number (in pixels) or a predefined enum
              value (tiny, short, medium, long). If not provided, the swipe will be performed
              from the center of the screen to the screen edge

          duration: Duration of the swipe

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          location: Natural language description of the location where the swipe should originate.
              If not provided, the swipe will be performed from the center of the screen.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def swipe(
        self,
        box_id: str,
        *,
        end: action_swipe_params.SwipeAdvancedEnd,
        start: action_swipe_params.SwipeAdvancedStart,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Performs a swipe in the specified direction

        Args:
          end: End point of the swipe path (coordinates or natural language)

          start: Start point of the swipe path (coordinates or natural language)

          duration: Duration of the swipe

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 500ms

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["direction"], ["end", "start"])
    async def swipe(
        self,
        box_id: str,
        *,
        direction: Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"] | Omit = omit,
        distance: Union[float, Literal["tiny", "short", "medium", "long"]] | Omit = omit,
        duration: str | Omit = omit,
        include_screenshot: bool | Omit = omit,
        location: str | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        end: action_swipe_params.SwipeAdvancedEnd | Omit = omit,
        start: action_swipe_params.SwipeAdvancedStart | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/swipe",
            body=await async_maybe_transform(
                {
                    "direction": direction,
                    "distance": distance,
                    "duration": duration,
                    "include_screenshot": include_screenshot,
                    "location": location,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                    "end": end,
                    "start": start,
                },
                action_swipe_params.ActionSwipeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    @overload
    async def tap(
        self,
        box_id: str,
        *,
        x: float,
        y: float,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Tap action for Android devices using ADB input tap command

        Args:
          x: X coordinate of the tap

          y: Y coordinate of the tap

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def tap(
        self,
        box_id: str,
        *,
        target: str,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Tap action for Android devices using ADB input tap command

        Args:
          target: Describe the target to operate using natural language, e.g., 'login button' or
              'Chrome'.

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def tap(
        self,
        box_id: str,
        *,
        target: DetectedElement,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Tap action for Android devices using ADB input tap command

        Args:
          target: Detected UI element

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["x", "y"], ["target"])
    async def tap(
        self,
        box_id: str,
        *,
        x: float | Omit = omit,
        y: float | Omit = omit,
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        target: str | DetectedElement | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/tap",
            body=await async_maybe_transform(
                {
                    "x": x,
                    "y": y,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                    "target": target,
                },
                action_tap_params.ActionTapParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    async def touch(
        self,
        box_id: str,
        *,
        points: Iterable[action_touch_params.Point],
        include_screenshot: bool | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """Performs more advanced touch gestures.

        Use this endpoint to simulate realistic
        behaviors.

        Args:
          points: Array of touch points and their actions

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/touch",
            body=await async_maybe_transform(
                {
                    "points": points,
                    "include_screenshot": include_screenshot,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "screenshot_delay": screenshot_delay,
                },
                action_touch_params.ActionTouchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )

    async def type(
        self,
        box_id: str,
        *,
        text: str,
        include_screenshot: bool | Omit = omit,
        mode: Literal["append", "replace"] | Omit = omit,
        options: ActionCommonOptionsParam | Omit = omit,
        output_format: Literal["base64", "storageKey"] | Omit = omit,
        presigned_expires_in: str | Omit = omit,
        press_enter: bool | Omit = omit,
        screenshot_delay: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActionResult:
        """
        Directly inputs text content without triggering physical key events (keydown,
        etc.), ideal for quickly filling large amounts of text when intermediate input
        events aren't needed.

        Args:
          text: Text to type

          include_screenshot: ⚠️ DEPRECATED: Use `options.screenshot.phases` instead. This field will be
              ignored when `options.screenshot` is provided. Whether to include screenshots in
              the action response. If false, the screenshot object will still be returned but
              with empty URIs. Default is false.

          mode: Text input mode: 'append' to add text to existing content, 'replace' to replace
              all existing text

          options: Action common options

          output_format: ⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead. Type of the URI.
              default is base64. This field will be ignored when `options.screenshot` is
              provided.

          presigned_expires_in: ⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead. Presigned
              url expires in. Only takes effect when outputFormat is storageKey. This field
              will be ignored when `options.screenshot` is provided.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          press_enter: Whether to press Enter after typing the text

          screenshot_delay: ⚠️ DEPRECATED: Use `options.screenshot.delay` instead. This field will be
              ignored when `options.screenshot` is provided.

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

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/actions/type",
            body=await async_maybe_transform(
                {
                    "text": text,
                    "include_screenshot": include_screenshot,
                    "mode": mode,
                    "options": options,
                    "output_format": output_format,
                    "presigned_expires_in": presigned_expires_in,
                    "press_enter": press_enter,
                    "screenshot_delay": screenshot_delay,
                },
                action_type_params.ActionTypeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ActionResult,
        )


class ActionsResourceWithRawResponse:
    def __init__(self, actions: ActionsResource) -> None:
        self._actions = actions

        self.click = to_raw_response_wrapper(
            actions.click,
        )
        self.clipboard_get = to_raw_response_wrapper(
            actions.clipboard_get,
        )
        self.clipboard_set = to_raw_response_wrapper(
            actions.clipboard_set,
        )
        self.drag = to_raw_response_wrapper(
            actions.drag,
        )
        self.elements_detect = to_raw_response_wrapper(
            actions.elements_detect,
        )
        self.extract = to_raw_response_wrapper(
            actions.extract,
        )
        self.long_press = to_raw_response_wrapper(
            actions.long_press,
        )
        self.move = to_raw_response_wrapper(
            actions.move,
        )
        self.press_button = to_raw_response_wrapper(
            actions.press_button,
        )
        self.press_key = to_raw_response_wrapper(
            actions.press_key,
        )
        self.recording_start = to_raw_response_wrapper(
            actions.recording_start,
        )
        self.recording_stop = to_raw_response_wrapper(
            actions.recording_stop,
        )
        self.rewind_disable = to_raw_response_wrapper(
            actions.rewind_disable,
        )
        self.rewind_enable = to_raw_response_wrapper(
            actions.rewind_enable,
        )
        self.rewind_extract = to_raw_response_wrapper(
            actions.rewind_extract,
        )
        self.screen_layout = to_raw_response_wrapper(
            actions.screen_layout,
        )
        self.screen_rotation = to_raw_response_wrapper(
            actions.screen_rotation,
        )
        self.screenshot = to_raw_response_wrapper(
            actions.screenshot,
        )
        self.scroll = to_raw_response_wrapper(
            actions.scroll,
        )
        self.settings = to_raw_response_wrapper(
            actions.settings,
        )
        self.settings_reset = to_raw_response_wrapper(
            actions.settings_reset,
        )
        self.settings_update = to_raw_response_wrapper(
            actions.settings_update,
        )
        self.swipe = to_raw_response_wrapper(
            actions.swipe,
        )
        self.tap = to_raw_response_wrapper(
            actions.tap,
        )
        self.touch = to_raw_response_wrapper(
            actions.touch,
        )
        self.type = to_raw_response_wrapper(
            actions.type,
        )


class AsyncActionsResourceWithRawResponse:
    def __init__(self, actions: AsyncActionsResource) -> None:
        self._actions = actions

        self.click = async_to_raw_response_wrapper(
            actions.click,
        )
        self.clipboard_get = async_to_raw_response_wrapper(
            actions.clipboard_get,
        )
        self.clipboard_set = async_to_raw_response_wrapper(
            actions.clipboard_set,
        )
        self.drag = async_to_raw_response_wrapper(
            actions.drag,
        )
        self.elements_detect = async_to_raw_response_wrapper(
            actions.elements_detect,
        )
        self.extract = async_to_raw_response_wrapper(
            actions.extract,
        )
        self.long_press = async_to_raw_response_wrapper(
            actions.long_press,
        )
        self.move = async_to_raw_response_wrapper(
            actions.move,
        )
        self.press_button = async_to_raw_response_wrapper(
            actions.press_button,
        )
        self.press_key = async_to_raw_response_wrapper(
            actions.press_key,
        )
        self.recording_start = async_to_raw_response_wrapper(
            actions.recording_start,
        )
        self.recording_stop = async_to_raw_response_wrapper(
            actions.recording_stop,
        )
        self.rewind_disable = async_to_raw_response_wrapper(
            actions.rewind_disable,
        )
        self.rewind_enable = async_to_raw_response_wrapper(
            actions.rewind_enable,
        )
        self.rewind_extract = async_to_raw_response_wrapper(
            actions.rewind_extract,
        )
        self.screen_layout = async_to_raw_response_wrapper(
            actions.screen_layout,
        )
        self.screen_rotation = async_to_raw_response_wrapper(
            actions.screen_rotation,
        )
        self.screenshot = async_to_raw_response_wrapper(
            actions.screenshot,
        )
        self.scroll = async_to_raw_response_wrapper(
            actions.scroll,
        )
        self.settings = async_to_raw_response_wrapper(
            actions.settings,
        )
        self.settings_reset = async_to_raw_response_wrapper(
            actions.settings_reset,
        )
        self.settings_update = async_to_raw_response_wrapper(
            actions.settings_update,
        )
        self.swipe = async_to_raw_response_wrapper(
            actions.swipe,
        )
        self.tap = async_to_raw_response_wrapper(
            actions.tap,
        )
        self.touch = async_to_raw_response_wrapper(
            actions.touch,
        )
        self.type = async_to_raw_response_wrapper(
            actions.type,
        )


class ActionsResourceWithStreamingResponse:
    def __init__(self, actions: ActionsResource) -> None:
        self._actions = actions

        self.click = to_streamed_response_wrapper(
            actions.click,
        )
        self.clipboard_get = to_streamed_response_wrapper(
            actions.clipboard_get,
        )
        self.clipboard_set = to_streamed_response_wrapper(
            actions.clipboard_set,
        )
        self.drag = to_streamed_response_wrapper(
            actions.drag,
        )
        self.elements_detect = to_streamed_response_wrapper(
            actions.elements_detect,
        )
        self.extract = to_streamed_response_wrapper(
            actions.extract,
        )
        self.long_press = to_streamed_response_wrapper(
            actions.long_press,
        )
        self.move = to_streamed_response_wrapper(
            actions.move,
        )
        self.press_button = to_streamed_response_wrapper(
            actions.press_button,
        )
        self.press_key = to_streamed_response_wrapper(
            actions.press_key,
        )
        self.recording_start = to_streamed_response_wrapper(
            actions.recording_start,
        )
        self.recording_stop = to_streamed_response_wrapper(
            actions.recording_stop,
        )
        self.rewind_disable = to_streamed_response_wrapper(
            actions.rewind_disable,
        )
        self.rewind_enable = to_streamed_response_wrapper(
            actions.rewind_enable,
        )
        self.rewind_extract = to_streamed_response_wrapper(
            actions.rewind_extract,
        )
        self.screen_layout = to_streamed_response_wrapper(
            actions.screen_layout,
        )
        self.screen_rotation = to_streamed_response_wrapper(
            actions.screen_rotation,
        )
        self.screenshot = to_streamed_response_wrapper(
            actions.screenshot,
        )
        self.scroll = to_streamed_response_wrapper(
            actions.scroll,
        )
        self.settings = to_streamed_response_wrapper(
            actions.settings,
        )
        self.settings_reset = to_streamed_response_wrapper(
            actions.settings_reset,
        )
        self.settings_update = to_streamed_response_wrapper(
            actions.settings_update,
        )
        self.swipe = to_streamed_response_wrapper(
            actions.swipe,
        )
        self.tap = to_streamed_response_wrapper(
            actions.tap,
        )
        self.touch = to_streamed_response_wrapper(
            actions.touch,
        )
        self.type = to_streamed_response_wrapper(
            actions.type,
        )


class AsyncActionsResourceWithStreamingResponse:
    def __init__(self, actions: AsyncActionsResource) -> None:
        self._actions = actions

        self.click = async_to_streamed_response_wrapper(
            actions.click,
        )
        self.clipboard_get = async_to_streamed_response_wrapper(
            actions.clipboard_get,
        )
        self.clipboard_set = async_to_streamed_response_wrapper(
            actions.clipboard_set,
        )
        self.drag = async_to_streamed_response_wrapper(
            actions.drag,
        )
        self.elements_detect = async_to_streamed_response_wrapper(
            actions.elements_detect,
        )
        self.extract = async_to_streamed_response_wrapper(
            actions.extract,
        )
        self.long_press = async_to_streamed_response_wrapper(
            actions.long_press,
        )
        self.move = async_to_streamed_response_wrapper(
            actions.move,
        )
        self.press_button = async_to_streamed_response_wrapper(
            actions.press_button,
        )
        self.press_key = async_to_streamed_response_wrapper(
            actions.press_key,
        )
        self.recording_start = async_to_streamed_response_wrapper(
            actions.recording_start,
        )
        self.recording_stop = async_to_streamed_response_wrapper(
            actions.recording_stop,
        )
        self.rewind_disable = async_to_streamed_response_wrapper(
            actions.rewind_disable,
        )
        self.rewind_enable = async_to_streamed_response_wrapper(
            actions.rewind_enable,
        )
        self.rewind_extract = async_to_streamed_response_wrapper(
            actions.rewind_extract,
        )
        self.screen_layout = async_to_streamed_response_wrapper(
            actions.screen_layout,
        )
        self.screen_rotation = async_to_streamed_response_wrapper(
            actions.screen_rotation,
        )
        self.screenshot = async_to_streamed_response_wrapper(
            actions.screenshot,
        )
        self.scroll = async_to_streamed_response_wrapper(
            actions.scroll,
        )
        self.settings = async_to_streamed_response_wrapper(
            actions.settings,
        )
        self.settings_reset = async_to_streamed_response_wrapper(
            actions.settings_reset,
        )
        self.settings_update = async_to_streamed_response_wrapper(
            actions.settings_update,
        )
        self.swipe = async_to_streamed_response_wrapper(
            actions.swipe,
        )
        self.tap = async_to_streamed_response_wrapper(
            actions.tap,
        )
        self.touch = async_to_streamed_response_wrapper(
            actions.touch,
        )
        self.type = async_to_streamed_response_wrapper(
            actions.type,
        )
