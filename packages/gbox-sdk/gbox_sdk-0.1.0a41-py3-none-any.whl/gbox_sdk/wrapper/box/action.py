import os
import base64
from typing import List, Union, Optional
from typing_extensions import Literal, Iterable, cast, overload

from gbox_sdk._types import Omit, omit
from gbox_sdk._client import GboxClient
from gbox_sdk._utils._utils import required_args
from gbox_sdk.types.v1.boxes.action_result import ActionResult
from gbox_sdk.types.v1.boxes.detected_element import DetectedElement
from gbox_sdk.types.v1.boxes.action_drag_params import DragSimpleEnd, DragSimpleStart, DragAdvancedPath
from gbox_sdk.types.v1.boxes.action_swipe_params import SwipeAdvancedEnd, SwipeAdvancedStart
from gbox_sdk.types.v1.boxes.action_touch_params import Point
from gbox_sdk.types.v1.boxes.action_extract_response import ActionExtractResponse
from gbox_sdk.types.v1.boxes.action_press_key_params import KeysType
from gbox_sdk.types.v1.boxes.action_screenshot_params import Clip, ActionScreenshotParams
from gbox_sdk.types.v1.boxes.action_settings_response import ActionSettingsResponse
from gbox_sdk.types.v1.boxes.action_screenshot_response import ActionScreenshotResponse
from gbox_sdk.types.v1.boxes.action_common_options_param import ActionCommonOptionsParam
from gbox_sdk.types.v1.boxes.action_elements_detect_params import Screenshot
from gbox_sdk.types.v1.boxes.action_screen_layout_response import ActionScreenLayoutResponse
from gbox_sdk.types.v1.boxes.action_recording_stop_response import ActionRecordingStopResponse
from gbox_sdk.types.v1.boxes.action_rewind_extract_response import ActionRewindExtractResponse
from gbox_sdk.types.v1.boxes.action_settings_reset_response import ActionSettingsResetResponse
from gbox_sdk.types.v1.boxes.action_elements_detect_response import Screenshot as ElementsDetectScreenshot
from gbox_sdk.types.v1.boxes.action_settings_update_response import ActionSettingsUpdateResponse


class ActionScreenshot(ActionScreenshotParams, total=False):
    """
    Extends ActionScreenshotParams to optionally include a file path for saving the screenshot.

    Attributes:
        path (Optional[str]): The file path where the screenshot will be saved.
    """

    path: Optional[str]


class ActionOperator:
    """
    Provides high-level action operations for a specific box using the GboxClient.

    Methods correspond to various box actions such as click, drag, swipe, type, screenshot, etc.
    """

    def __init__(self, client: GboxClient, box_id: str):
        """
        Initialize the ActionOperator.

        Args:
            client (GboxClient): The GboxClient instance to use for API calls.
            box_id (str): The ID of the box to operate on.
        """
        self.client = client
        self.box_id = box_id
        self.recording = RecordingOperator(client, box_id)
        self.clipboard = ClipboardOperator(client, box_id)
        self.elements = ElementsOperator(client, box_id)

    @overload
    def click(
        self,
        *,
        x: float,
        y: float,
        button: Union[Literal["left", "right", "middle"], Omit] = omit,
        double: Union[bool, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
    ) -> ActionResult:
        """
        Perform a click action on the box.

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

        Returns:
            ActionResult: The response from the click action.

        Example:
            >>> response = myBox.action.click(x=100, y=100)
        """

    @overload
    def click(
        self,
        *,
        target: str,
        button: Union[Literal["left", "right", "middle"], Omit] = omit,
        double: Union[bool, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
    ) -> ActionResult:
        """
        Perform a click action on the box.

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

        Returns:
            ActionResult: The response from the click action.

        Example:
            >>> response = myBox.action.click(x=100, y=100)
        """

    @overload
    def click(
        self,
        *,
        target: DetectedElement,
        button: Union[Literal["left", "right", "middle"], Omit] = omit,
        double: Union[bool, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
    ) -> ActionResult:
        """
        Perform a click action on the box.

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

        Returns:
            ActionResult: The response from the click action.

        Example:
            >>> response = myBox.action.click(x=100, y=100)
        """

    @required_args(["x", "y"], ["target"])
    def click(
        self,
        *,
        x: Union[float, Omit] = omit,
        y: Union[float, Omit] = omit,
        button: Union[Literal["left", "right", "middle"], Omit] = omit,
        double: Union[bool, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        target: Union[str, DetectedElement, Omit] = omit,
    ) -> ActionResult:
        if isinstance(target, str):
            return self.client.v1.boxes.actions.click(
                box_id=self.box_id,
                target=target,
                button=button,
                double=double,
                include_screenshot=include_screenshot,
                options=options,
                output_format=output_format,
                presigned_expires_in=presigned_expires_in,
                screenshot_delay=screenshot_delay,
            )
        elif isinstance(target, DetectedElement):
            return self.client.v1.boxes.actions.click(
                box_id=self.box_id,
                target=target,
                button=button,
                double=double,
                include_screenshot=include_screenshot,
                options=options,
                output_format=output_format,
                presigned_expires_in=presigned_expires_in,
                screenshot_delay=screenshot_delay,
            )
        elif x is not omit and y is not omit:
            return self.client.v1.boxes.actions.click(
                box_id=self.box_id,
                x=cast(float, x),
                y=cast(float, y),
                button=button,
                double=double,
                include_screenshot=include_screenshot,
                options=options,
                output_format=output_format,
                presigned_expires_in=presigned_expires_in,
                screenshot_delay=screenshot_delay,
            )
        else:
            raise ValueError("Either 'x' and 'y' (for simple click) or 'target' (for target click) must be provided")

    @overload
    def drag(
        self,
        *,
        end: DragSimpleEnd,
        start: DragSimpleStart,
        duration: Union[str, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
    ) -> ActionResult:
        """
        Drag

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
        """
        ...

    @overload
    def drag(
        self,
        *,
        path: Iterable[DragAdvancedPath],
        duration: Union[str, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
    ) -> ActionResult:
        """
        Drag

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
        """
        ...

    @required_args(["end", "start"], ["path"])
    def drag(
        self,
        *,
        end: Union[DragSimpleEnd, Omit] = omit,
        start: Union[DragSimpleStart, Omit] = omit,
        duration: Union[str, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
        path: Union[Iterable[DragAdvancedPath], Omit] = omit,
    ) -> ActionResult:
        if path is not omit:
            return self.client.v1.boxes.actions.drag(
                box_id=self.box_id,
                path=cast(Iterable[DragAdvancedPath], path),
                duration=duration,
                include_screenshot=include_screenshot,
                output_format=output_format,
                screenshot_delay=screenshot_delay,
                options=options,
                presigned_expires_in=presigned_expires_in,
            )
        elif start is not omit and end is not omit:
            return self.client.v1.boxes.actions.drag(
                box_id=self.box_id,
                start=cast(DragSimpleStart, start),
                end=cast(DragSimpleEnd, end),
                duration=duration,
                include_screenshot=include_screenshot,
                output_format=output_format,
                screenshot_delay=screenshot_delay,
                options=options,
                presigned_expires_in=presigned_expires_in,
            )
        else:
            raise ValueError(
                "Either 'path' (for advanced drag) or both 'start' and 'end' (for simple drag) must be provided"
            )

    @overload
    def swipe(
        self,
        *,
        direction: Union[
            Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"], Omit
        ] = omit,
        distance: Union[float, Literal["tiny", "short", "medium", "long"], Omit] = omit,
        duration: Union[str, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        location: Union[str, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
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
        """
        ...

    @overload
    def swipe(
        self,
        *,
        end: SwipeAdvancedEnd,
        start: SwipeAdvancedStart,
        duration: Union[str, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
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
        """
        ...

    @required_args(["direction"], ["end", "start"])
    def swipe(
        self,
        *,
        direction: Union[
            Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"], Omit
        ] = omit,
        distance: Union[float, Literal["tiny", "short", "medium", "long"], Omit] = omit,
        duration: Union[str, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        location: Union[str, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
        end: Union[SwipeAdvancedEnd, Omit] = omit,
        start: Union[SwipeAdvancedStart, Omit] = omit,
    ) -> ActionResult:
        if direction is not omit:
            return self.client.v1.boxes.actions.swipe(
                box_id=self.box_id,
                direction=cast(
                    Literal["up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight"], direction
                ),
                distance=distance,
                duration=duration,
                include_screenshot=include_screenshot,
                output_format=output_format,
                screenshot_delay=screenshot_delay,
                options=options,
                presigned_expires_in=presigned_expires_in,
                location=location,
            )
        elif start is not omit and end is not omit:
            return self.client.v1.boxes.actions.swipe(
                box_id=self.box_id,
                start=cast(SwipeAdvancedStart, start),
                end=cast(SwipeAdvancedEnd, end),
                duration=duration,
                include_screenshot=include_screenshot,
                output_format=output_format,
                screenshot_delay=screenshot_delay,
                options=options,
                presigned_expires_in=presigned_expires_in,
            )
        else:
            raise ValueError(
                "Either 'direction' and 'distance' (for simple swipe) or both 'start' and 'end' "
                "(for advanced swipe) must be provided"
            )

    def press_key(
        self,
        *,
        keys: KeysType,
        combination: Union[bool, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
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

        Returns:
            ActionPressKeyResponse: The response from the key press action.

        Example:
            >>> response = myBox.action.press_key(keys=["enter"])
            >>> response = myBox.action.press_key(keys=["control", "c"], combination=True)
        """
        return self.client.v1.boxes.actions.press_key(
            box_id=self.box_id,
            keys=keys,
            combination=combination,
            include_screenshot=include_screenshot,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
            options=options,
            presigned_expires_in=presigned_expires_in,
        )

    def press_button(
        self,
        buttons: List[Literal["power", "volumeUp", "volumeDown", "volumeMute", "home", "back", "menu", "appSwitch"]],
        *,
        include_screenshot: Union[bool, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
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

        Returns:
            ActionPressButtonResponse: The response from the button press action.

        Example:
            >>> response = myBox.action.press_button(buttons=["power"])
        """
        return self.client.v1.boxes.actions.press_button(
            box_id=self.box_id,
            buttons=buttons,
            include_screenshot=include_screenshot,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
            options=options,
            presigned_expires_in=presigned_expires_in,
        )

    def move(
        self,
        *,
        x: float,
        y: float,
        include_screenshot: Union[bool, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
    ) -> ActionResult:
        """
        Move an element or pointer on the box.

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

        Returns:
            ActionMoveResponse: The response from the move action.

        Example:
            >>> response = myBox.action.move(x=200, y=300)
        """
        return self.client.v1.boxes.actions.move(
            box_id=self.box_id,
            x=x,
            y=y,
            include_screenshot=include_screenshot,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
            options=options,
            presigned_expires_in=presigned_expires_in,
        )

    @overload
    def tap(
        self,
        *,
        x: float,
        y: float,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
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
        """
        ...

    @overload
    def tap(
        self,
        *,
        target: str,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
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
        """
        ...

    @overload
    def tap(
        self,
        *,
        target: DetectedElement,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
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
        """
        ...

    @required_args(["x", "y"], ["target"])
    def tap(
        self,
        *,
        x: Union[float, Omit] = omit,
        y: Union[float, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
        target: Union[str, DetectedElement, Omit] = omit,
    ) -> ActionResult:
        if x is not omit and y is not omit:
            return self.client.v1.boxes.actions.tap(
                box_id=self.box_id,
                x=cast(float, x),
                y=cast(float, y),
                include_screenshot=include_screenshot,
                options=options,
                output_format=output_format,
                presigned_expires_in=presigned_expires_in,
                screenshot_delay=screenshot_delay,
            )
        elif target is not omit and isinstance(target, str):
            return self.client.v1.boxes.actions.tap(
                box_id=self.box_id,
                target=target,
                include_screenshot=include_screenshot,
                options=options,
                output_format=output_format,
                presigned_expires_in=presigned_expires_in,
                screenshot_delay=screenshot_delay,
            )
        elif target is not omit and isinstance(target, DetectedElement):
            return self.client.v1.boxes.actions.tap(
                box_id=self.box_id,
                target=target,
                include_screenshot=include_screenshot,
                options=options,
                output_format=output_format,
                presigned_expires_in=presigned_expires_in,
                screenshot_delay=screenshot_delay,
            )
        else:
            raise ValueError("Either 'x' and 'y' (for simple click) or 'target' (for target click) must be provided")

    @overload
    def long_press(
        self,
        *,
        x: float,
        y: float,
        duration: Union[str, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
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
        """
        ...

    @overload
    def long_press(
        self,
        *,
        target: str,
        duration: Union[str, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
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
        """
        ...

    @overload
    def long_press(
        self,
        *,
        target: DetectedElement,
        duration: Union[str, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
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
        """
        ...

    @required_args(["x", "y"], ["target"])
    def long_press(
        self,
        *,
        x: Union[float, Omit] = omit,
        y: Union[float, Omit] = omit,
        duration: Union[str, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
        target: Union[str, DetectedElement, Omit] = omit,
    ) -> ActionResult:
        if x is not omit and y is not omit:
            return self.client.v1.boxes.actions.long_press(
                box_id=self.box_id,
                x=cast(float, x),
                y=cast(float, y),
                duration=duration,
                include_screenshot=include_screenshot,
                output_format=output_format,
                presigned_expires_in=presigned_expires_in,
                screenshot_delay=screenshot_delay,
                options=options,
            )
        elif target is not omit and isinstance(target, str):
            return self.client.v1.boxes.actions.long_press(
                box_id=self.box_id,
                target=target,
                duration=duration,
                include_screenshot=include_screenshot,
                output_format=output_format,
                presigned_expires_in=presigned_expires_in,
                screenshot_delay=screenshot_delay,
                options=options,
            )
        elif target is not omit and isinstance(target, DetectedElement):
            return self.client.v1.boxes.actions.long_press(
                box_id=self.box_id,
                target=target,
                duration=duration,
                include_screenshot=include_screenshot,
                output_format=output_format,
                presigned_expires_in=presigned_expires_in,
                screenshot_delay=screenshot_delay,
                options=options,
            )
        else:
            raise ValueError(
                "Either 'x' and 'y' (for simple long press) or 'target' (for target long press) must be provided"
            )

    @overload
    def scroll(
        self,
        *,
        scroll_x: float,
        scroll_y: float,
        x: float,
        y: float,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
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
        """
        ...

    @overload
    def scroll(
        self,
        *,
        direction: Literal["up", "down", "left", "right"],
        distance: Union[float, Literal["tiny", "short", "medium", "long"], Omit] = omit,
        duration: Union[str, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
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
        """
        ...

    @required_args(["scroll_x", "scroll_y", "x", "y"], ["direction"])
    def scroll(
        self,
        *,
        scroll_x: Union[float, Omit] = omit,
        scroll_y: Union[float, Omit] = omit,
        x: Union[float, Omit] = omit,
        y: Union[float, Omit] = omit,
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
        direction: Union[Literal["up", "down", "left", "right"], Omit] = omit,
        distance: Union[float, Literal["tiny", "short", "medium", "long"], Omit] = omit,
        duration: Union[str, Omit] = omit,
    ) -> ActionResult:
        if scroll_x is not omit and scroll_y is not omit and x is not omit and y is not omit:
            return self.client.v1.boxes.actions.scroll(
                box_id=self.box_id,
                scroll_x=cast(float, scroll_x),
                scroll_y=cast(float, scroll_y),
                x=cast(float, x),
                y=cast(float, y),
                include_screenshot=include_screenshot,
                output_format=output_format,
                screenshot_delay=screenshot_delay,
                options=options,
                presigned_expires_in=presigned_expires_in,
            )
        elif direction is not omit:
            return self.client.v1.boxes.actions.scroll(
                box_id=self.box_id,
                direction=cast(Literal["up", "down", "left", "right"], direction),
                distance=distance,
                duration=duration,
                include_screenshot=include_screenshot,
                output_format=output_format,
                presigned_expires_in=presigned_expires_in,
                screenshot_delay=screenshot_delay,
                options=options,
            )
        else:
            raise ValueError(
                "Either 'scroll_x' and 'scroll_y' (for simple scroll) or 'direction' "
                "(for direction scroll) must be provided"
            )

    def touch(
        self,
        *,
        points: Iterable[Point],
        include_screenshot: Union[bool, Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
    ) -> ActionResult:
        """
        Simulate a touch action on the box.

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

        Returns:
            ActionTouchResponse: The response from the touch action.

        Example:
            >>> response = myBox.action.touch(points=[{"start": {"x": 0, "y": 0}}])
        """
        return self.client.v1.boxes.actions.touch(
            box_id=self.box_id,
            points=points,
            include_screenshot=include_screenshot,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
            options=options,
            presigned_expires_in=presigned_expires_in,
        )

    def type(
        self,
        text: str,
        *,
        include_screenshot: Union[bool, Omit] = omit,
        mode: Union[Literal["append", "replace"], Omit] = omit,
        options: Union[ActionCommonOptionsParam, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        press_enter: Union[bool, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
    ) -> ActionResult:
        """
        Simulate typing text on the box.

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

        Returns:
            ActionTypeResponse: The response from the type action.

        Example:
            >>> response = myBox.action.type(text="Hello, World!")
        """
        return self.client.v1.boxes.actions.type(
            box_id=self.box_id,
            text=text,
            include_screenshot=include_screenshot,
            mode=mode,
            output_format=output_format,
            screenshot_delay=screenshot_delay,
            options=options,
            presigned_expires_in=presigned_expires_in,
            press_enter=press_enter,
        )

    def extract(
        self,
        *,
        instruction: str,
        schema: Union[object, Omit] = omit,
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

        Returns:
            ActionExtractResponse: The response containing the extracted data.

        Example:
            >>> response = myBox.action.extract(
            ...     instruction="Extract the user name from the profile",
            ...     schema={"type": "string"},
            ... )
        """
        return self.client.v1.boxes.actions.extract(
            box_id=self.box_id,
            instruction=instruction,
            schema=schema,
        )

    def screenshot(
        self,
        *,
        path: Union[str, Omit] = omit,
        clip: Union[Clip, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        save_to_album: Union[bool, Omit] = omit,
    ) -> ActionScreenshotResponse:
        """
        Take a screenshot of the box.

        Args:
          clip: Clipping region for screenshot capture

          output_format: Type of the URI. default is base64.

          presigned_expires_in: Presigned url expires in. Only takes effect when outputFormat is storageKey.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Default: 30m

          save_to_album: Whether to save the screenshot to the device screenshot album

        Returns:
            ActionScreenshotResponse: The response containing the screenshot data.

        Examples:
            Take a screenshot and return base64 data:
            >>> response = action_operator.screenshot()

            Take a screenshot and save to file:
            >>> response = action_operator.screenshot(path="/path/to/screenshot.png")

            Take a screenshot with specific format:
            >>> response = action_operator.screenshot(output_format="base64")
        """
        if path is not omit:
            file_path = path
        else:
            file_path = None

        response = self.client.v1.boxes.actions.screenshot(
            box_id=self.box_id,
            clip=clip,
            output_format=output_format,
            presigned_expires_in=presigned_expires_in,
            save_to_album=save_to_album,
        )

        if file_path:
            self._save_data_url_to_file(response.uri, file_path)

        return response

    def screen_layout(self) -> ActionScreenLayoutResponse:
        """
        Get the current structured screen layout information.

        Returns:
            ActionScreenLayoutResponse: The response containing the screen layout data.

        Example:
            >>> response = myBox.action.screen_layout()
        """
        return self.client.v1.boxes.actions.screen_layout(box_id=self.box_id)

    def screen_rotation(
        self,
        orientation: Literal["portrait", "landscapeLeft", "portraitUpsideDown", "landscapeRight"],
        *,
        include_screenshot: Union[bool, Omit] = omit,
        output_format: Union[Literal["base64", "storageKey"], Omit] = omit,
        presigned_expires_in: Union[str, Omit] = omit,
        screenshot_delay: Union[str, Omit] = omit,
    ) -> ActionResult:
        """
        Rotate the screen orientation.

        Note that even after rotating the screen,
        applications or system layouts may not automatically adapt to the gravity sensor
        changes, so visual changes may not always occur.

        Args:
            orientation: Target screen orientation

            include_screenshot: Whether to include screenshots in the action response. If false, the screenshot
                object will still be returned but with empty URIs. Default is false.

            output_format: Type of the URI. default is base64.

            presigned_expires_in: Presigned url expires in. Only takes effect when outputFormat is storageKey.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 30m

            screenshot_delay: Delay after performing the action, before taking the final screenshot.

                Execution flow:

                1. Take screenshot before action
                2. Perform the action
                3. Wait for screenshotDelay (this parameter)
                4. Take screenshot after action

                Example: '500ms' means wait 500ms after the action before capturing the final
                screenshot.

                Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
                Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s


        Returns:
            ActionScreenRotationResponse: The response from the screen rotation action.

        Example:
            >>> response = myBox.action.screen_rotation("landscapeLeft")
            >>> response = myBox.action.screen_rotation(
            ...     orientation="landscapeLeft",
            ...     include_screenshot=True,
            ...     output_format="storageKey",
            ...     presigned_expires_in="30m",
            ...     screenshot_delay="500ms",
            ... )
        """
        return self.client.v1.boxes.actions.screen_rotation(
            box_id=self.box_id,
            orientation=orientation,
            include_screenshot=include_screenshot,
            output_format=output_format,
            presigned_expires_in=presigned_expires_in,
            screenshot_delay=screenshot_delay,
        )

    def screen_recording_start(self) -> None:
        """
        Start recording the box screen.

        Only one recording can be active at a time. If a
        recording is already in progress, starting a new recording will stop the
        previous one and keep only the latest recording.

        Args:
          duration: Duration of the recording. Default is 30m, max is 30m. The recording will
              automatically stop when the duration time is reached.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Maximum allowed: 30m

        Example:
            >>> response = myBox.action.screen_recording_start(duration="30m")
        """
        return self.client.v1.boxes.actions.recording_start(box_id=self.box_id)

    def screen_recording_stop(self) -> ActionRecordingStopResponse:
        """
        Stop recording the screen.

        Returns:
            ActionRecordingStopResponse: The response from the screen recording stop action.

        Example:
            >>> response = myBox.action.screen_recording_stop()
        """
        return self.client.v1.boxes.actions.recording_stop(box_id=self.box_id)

    def get_settings(self) -> ActionSettingsResponse:
        """
        Get the box action settings

        Returns:
            ActionSettingsResponse: The response from the box action settings.

        Example:
            >>> response = myBox.action.get_setting()
        """
        return self.client.v1.boxes.actions.settings(box_id=self.box_id)

    def update_settings(self, scale: float) -> ActionSettingsUpdateResponse:
        """
        Update the box action settings

        Args:
            scale: The scale of the action to be performed. Must be greater than 0.1 and less than
              or equal to 1.

              Notes:

              - Scale does not change the box's actual screen resolution.
              - It affects the size of the output screenshot and the coordinates/distances of
                actions. Coordinates and distances are scaled by this factor. Example: when
                scale = 1, Click({x:100, y:100}); when scale = 0.5, the equivalent position is
                Click({x:50, y:50}).

        Returns:
            ActionSettingsUpdateResponse: The response from the box action settings update.

        Example:
            >>> response = myBox.action.update_settings(scale=0.5)
        """
        return self.client.v1.boxes.actions.settings_update(box_id=self.box_id, scale=scale)

    def reset_settings(self) -> ActionSettingsResetResponse:
        """
        Reset the box action settings

        Returns:
            ActionSettingsResetResponse: The response from the box action settings reset.

        Example:
            >>> response = myBox.action.reset_settings()
        """
        return self.client.v1.boxes.actions.settings_reset(box_id=self.box_id)

    def _save_data_url_to_file(self, data_url: str, file_path: str) -> None:
        """
        Save a base64-encoded data URL to a file.

        Args:
            data_url (str): The data URL containing base64-encoded data.
            file_path (str): The file path where the decoded data will be saved.

        Raises:
            ValueError: If the data URL format is invalid.
        """
        if not data_url.startswith("data:"):
            raise ValueError("Invalid data URL format")
        parts = data_url.split(",")
        if len(parts) != 2:
            raise ValueError("Invalid data URL format")
        base64_data = parts[1]

        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(base64.b64decode(base64_data))


class RecordingOperator:
    def __init__(self, client: GboxClient, box_id: str):
        self.client = client
        self.box_id = box_id
        self.rewind = RecordingRewindOperator(client, box_id)

    def start(self) -> None:
        """
        Start recording the box screen.

        Only one recording can be active at a time. If a
        recording is already in progress, starting a new recording will stop the
        previous one and keep only the latest recording.

        Args:
            duration: Duration of the recording. Default is 30m, max is 30m. The recording will
                automatically stop when the duration time is reached.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Maximum allowed: 30m

        Example:
            >>> response = myBox.action.recording.start(duration="30m")
        """
        return self.client.v1.boxes.actions.recording_start(box_id=self.box_id)

    def stop(self) -> ActionRecordingStopResponse:
        """
        Stop recording the box screen.

        Returns:
            ActionRecordingStopResponse: The response from the box screen recording stop.

        Example:
            >>> response = myBox.action.recording.stop()
        """
        return self.client.v1.boxes.actions.recording_stop(box_id=self.box_id)


class RecordingRewindOperator:
    def __init__(self, client: GboxClient, box_id: str):
        self.client = client
        self.box_id = box_id

    def enable(self) -> None:
        """
        Enable the box screen recording rewind.

        Example:
            >>> response = myBox.action.recording.rewind.enable()
        """
        return self.client.v1.boxes.actions.rewind_enable(box_id=self.box_id)

    def disable(self) -> None:
        """
        Disable the box screen recording rewind.

        Example:
            >>> response = myBox.action.recording.rewind.disable()
        """
        return self.client.v1.boxes.actions.rewind_disable(box_id=self.box_id)

    def extract(self, duration: str) -> ActionRewindExtractResponse:
        """
        Rewind and capture the device's background screen recording from a specified
        time period.

        Args:
          duration: How far back in time to rewind for extracting recorded video. This specifies the
              duration to go back from the current moment (e.g., '30s' rewinds 30 seconds to
              get recent recorded activity). Default is 30s, max is 5m.

              Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
              Example formats: "500ms", "30s", "5m", "1h" Maximum allowed: 5m

        Returns:
            ActionRewindExtractResponse: The response from the box screen recording rewind extract.

        Example:
            >>> response = myBox.action.recording.rewind.extract(duration="30s")
        """
        return self.client.v1.boxes.actions.rewind_extract(box_id=self.box_id, duration=duration)


class ClipboardOperator:
    def __init__(self, client: GboxClient, box_id: str):
        self.client = client
        self.box_id = box_id

    def get(self) -> str:
        """
        Get the clipboard content.

        Example:
            >>> response = myBox.action.clipboard.get()
        """
        return self.client.v1.boxes.actions.clipboard_get(box_id=self.box_id)

    def set(self, content: str) -> None:
        """
        Set the clipboard content

        Args:
          content: The content to set the clipboard content

        Example:
            >>> response = myBox.action.clipboard.set("Hello, world!")
        """
        return self.client.v1.boxes.actions.clipboard_set(box_id=self.box_id, content=content)


class ElementsOperator:
    def __init__(self, client: GboxClient, box_id: str):
        self.client = client
        self.box_id = box_id

    class DetectResult:
        """Result of element detection operation."""

        def __init__(self, elements: "ElementManager", screenshot: ElementsDetectScreenshot):
            self.elements = elements
            self.screenshot = screenshot

    def detect(self, screenshot: Union[Screenshot, Omit] = omit) -> "DetectResult":
        """
        Detect and identify interactive UI elements in the current screen.

        Args:
            screenshot: Detect elements screenshot options. See
                `gbox_sdk.types.v1.boxes.action_elements_detect_params.Screenshot`.

        Returns:
            A DetectResult object with:
            - elements: an `ElementManager` for convenient access to detected elements
            - screenshot: the screenshot metadata from detection

        Example:
            >>> response = myBox.action.elements.detect()
            >>> first = response.elements.list()[0]
        """
        result = self.client.v1.boxes.actions.elements_detect(box_id=self.box_id, screenshot=screenshot)
        element_manager = ElementManager(self.client, self.box_id, result.elements)

        return self.DetectResult(elements=element_manager, screenshot=result.screenshot)


class ElementManager:
    """The elements manager contains a list of detected elements."""

    def __init__(self, client: GboxClient, box_id: str, elements: List[DetectedElement]):
        self.client = client
        self.box_id = box_id
        self.elements = elements

    def get(self, id: str) -> DetectedElement:
        """Get an element by its id."""
        element = next((element for element in self.elements if element.id == id), None)
        if element is None:
            raise ValueError(f"Element with id {id} not found")
        return element

    def list(self) -> List[DetectedElement]:
        """List all elements."""
        return self.elements
