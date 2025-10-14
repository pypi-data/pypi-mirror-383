# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gbox_sdk import GboxClient, AsyncGboxClient
from tests.utils import assert_matches_type
from gbox_sdk.types.v1.boxes import (
    ActionResult,
    ActionExtractResponse,
    ActionSettingsResponse,
    ActionScreenshotResponse,
    ActionScreenLayoutResponse,
    ActionRecordingStopResponse,
    ActionRewindExtractResponse,
    ActionSettingsResetResponse,
    ActionElementsDetectResponse,
    ActionSettingsUpdateResponse,
)
from gbox_sdk.types.v1.boxes.detected_element import DetectedElement

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestActions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_click_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_click_with_all_params_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
            button="left",
            double=False,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_click_overload_1(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_click_overload_1(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_click_overload_1(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.click(
                box_id="",
                x=350,
                y=250,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_click_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_click_with_all_params_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
            button="left",
            double=False,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_click_overload_2(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_click_overload_2(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_click_overload_2(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.click(
                box_id="",
                target="login button",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_click_overload_3(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_click_with_all_params_overload_3(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
            button="left",
            double=False,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_click_overload_3(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_click_overload_3(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_click_overload_3(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.click(
                box_id="",
                target=cast(
                    DetectedElement,
                    {
                        "id": "1",
                        "center_x": 150,
                        "center_y": 125,
                        "height": 50,
                        "label": "Click me",
                        "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                        "source": "chromium",
                        "type": "button",
                        "width": 100,
                        "x": 100,
                        "y": 100,
                    },
                ),
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clipboard_get(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.clipboard_get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(str, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clipboard_get(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.clipboard_get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(str, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clipboard_get(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.clipboard_get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(str, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_clipboard_get(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.clipboard_get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clipboard_set(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.clipboard_set(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, world!",
        )
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clipboard_set(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.clipboard_set(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, world!",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clipboard_set(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.clipboard_set(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, world!",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert action is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_clipboard_set(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.clipboard_set(
                box_id="",
                content="Hello, world!",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_drag_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_drag_with_all_params_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
            duration="500ms",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_drag_overload_1(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_drag_overload_1(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_drag_overload_1(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.drag(
                box_id="",
                end={
                    "x": 400,
                    "y": 300,
                },
                start={
                    "x": 100,
                    "y": 150,
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_drag_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_drag_with_all_params_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
            duration="50ms",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_drag_overload_2(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_drag_overload_2(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_drag_overload_2(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.drag(
                box_id="",
                path=[
                    {
                        "x": 100,
                        "y": 150,
                    },
                    {
                        "x": 200,
                        "y": 200,
                    },
                    {
                        "x": 300,
                        "y": 250,
                    },
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_elements_detect(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.elements_detect(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionElementsDetectResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_elements_detect_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.elements_detect(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            screenshot={
                "output_format": "base64",
                "presigned_expires_in": "30m",
            },
        )
        assert_matches_type(ActionElementsDetectResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_elements_detect(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.elements_detect(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionElementsDetectResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_elements_detect(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.elements_detect(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionElementsDetectResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_elements_detect(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.elements_detect(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
        )
        assert_matches_type(ActionExtractResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
            schema={},
        )
        assert_matches_type(ActionExtractResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_extract(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionExtractResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_extract(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionExtractResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_extract(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.extract(
                box_id="",
                instruction="Extract the email address from the UI interface",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_long_press_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_long_press_with_all_params_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
            duration="1s",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_long_press_overload_1(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_long_press_overload_1(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_long_press_overload_1(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.long_press(
                box_id="",
                x=350,
                y=250,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_long_press_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="Chrome icon",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_long_press_with_all_params_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="Chrome icon",
            duration="1s",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_long_press_overload_2(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="Chrome icon",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_long_press_overload_2(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="Chrome icon",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_long_press_overload_2(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.long_press(
                box_id="",
                target="Chrome icon",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_long_press_overload_3(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_long_press_with_all_params_overload_3(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
            duration="1s",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_long_press_overload_3(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_long_press_overload_3(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_long_press_overload_3(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.long_press(
                box_id="",
                target=cast(
                    DetectedElement,
                    {
                        "id": "1",
                        "center_x": 150,
                        "center_y": 125,
                        "height": 50,
                        "label": "Click me",
                        "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                        "source": "chromium",
                        "type": "button",
                        "width": 100,
                        "x": 100,
                        "y": 100,
                    },
                ),
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_move(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_move_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_move(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_move(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_move(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.move(
                box_id="",
                x=200,
                y=300,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_press_button(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_press_button_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_press_button(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_press_button(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_press_button(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.press_button(
                box_id="",
                buttons=["power"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_press_key(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_press_key_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
            combination=True,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_press_key(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_press_key(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_press_key(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.press_key(
                box_id="",
                keys=["enter"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_recording_start(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.recording_start(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_recording_start(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.recording_start(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_recording_start(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.recording_start(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert action is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_recording_start(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.recording_start(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_recording_stop(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.recording_stop(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionRecordingStopResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_recording_stop(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.recording_stop(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionRecordingStopResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_recording_stop(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.recording_stop(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionRecordingStopResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_recording_stop(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.recording_stop(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_rewind_disable(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.rewind_disable(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_rewind_disable(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.rewind_disable(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_rewind_disable(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.rewind_disable(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert action is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_rewind_disable(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.rewind_disable(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_rewind_enable(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.rewind_enable(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_rewind_enable(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.rewind_enable(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_rewind_enable(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.rewind_enable(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert action is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_rewind_enable(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.rewind_enable(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_rewind_extract(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.rewind_extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionRewindExtractResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_rewind_extract_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.rewind_extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            duration="10s",
        )
        assert_matches_type(ActionRewindExtractResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_rewind_extract(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.rewind_extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionRewindExtractResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_rewind_extract(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.rewind_extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionRewindExtractResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_rewind_extract(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.rewind_extract(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_screen_layout(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.screen_layout(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionScreenLayoutResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_screen_layout(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.screen_layout(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionScreenLayoutResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_screen_layout(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.screen_layout(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionScreenLayoutResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_screen_layout(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.screen_layout(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_screen_rotation(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            orientation="landscapeLeft",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_screen_rotation_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            orientation="landscapeLeft",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_screen_rotation(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            orientation="landscapeLeft",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_screen_rotation(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            orientation="landscapeLeft",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_screen_rotation(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.screen_rotation(
                box_id="",
                orientation="landscapeLeft",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_screenshot(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionScreenshotResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_screenshot_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            clip={
                "height": 600,
                "width": 800,
                "x": 100,
                "y": 50,
            },
            output_format="base64",
            presigned_expires_in="30m",
            save_to_album=False,
            scroll_capture={
                "max_height": 4000,
                "scroll_back": True,
            },
        )
        assert_matches_type(ActionScreenshotResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_screenshot(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionScreenshotResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_screenshot(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionScreenshotResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_screenshot(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.screenshot(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_scroll_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=-100,
            x=400,
            y=300,
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_scroll_with_all_params_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=-100,
            x=400,
            y=300,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_scroll_overload_1(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=-100,
            x=400,
            y=300,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_scroll_overload_1(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=-100,
            x=400,
            y=300,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_scroll_overload_1(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.scroll(
                box_id="",
                scroll_x=0,
                scroll_y=-100,
                x=400,
                y=300,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_scroll_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_scroll_with_all_params_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
            distance=300,
            duration="500ms",
            include_screenshot=False,
            location="Side bar",
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_scroll_overload_2(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_scroll_overload_2(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_scroll_overload_2(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.scroll(
                box_id="",
                direction="up",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_settings(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.settings(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionSettingsResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_settings(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.settings(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionSettingsResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_settings(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.settings(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionSettingsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_settings(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.settings(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_settings_reset(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.settings_reset(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionSettingsResetResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_settings_reset(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.settings_reset(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionSettingsResetResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_settings_reset(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.settings_reset(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionSettingsResetResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_settings_reset(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.settings_reset(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_settings_update(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.settings_update(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scale=1,
        )
        assert_matches_type(ActionSettingsUpdateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_settings_update(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.settings_update(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scale=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionSettingsUpdateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_settings_update(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.settings_update(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scale=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionSettingsUpdateResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_settings_update(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.settings_update(
                box_id="",
                scale=1,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_swipe_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_swipe_with_all_params_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
            distance=300,
            duration="500ms",
            include_screenshot=False,
            location="Chrome App",
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_swipe_overload_1(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_swipe_overload_1(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_swipe_overload_1(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.swipe(
                box_id="",
                direction="up",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_swipe_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_swipe_with_all_params_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
            duration="500ms",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_swipe_overload_2(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_swipe_overload_2(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_swipe_overload_2(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.swipe(
                box_id="",
                end={
                    "x": 400,
                    "y": 300,
                },
                start={
                    "x": 100,
                    "y": 150,
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_tap_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_tap_with_all_params_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_tap_overload_1(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_tap_overload_1(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_tap_overload_1(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.tap(
                box_id="",
                x=350,
                y=250,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_tap_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_tap_with_all_params_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_tap_overload_2(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_tap_overload_2(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_tap_overload_2(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.tap(
                box_id="",
                target="login button",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_tap_overload_3(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_tap_with_all_params_overload_3(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_tap_overload_3(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_tap_overload_3(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_tap_overload_3(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.tap(
                box_id="",
                target=cast(
                    DetectedElement,
                    {
                        "id": "1",
                        "center_x": 150,
                        "center_y": 125,
                        "height": 50,
                        "label": "Click me",
                        "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                        "source": "chromium",
                        "type": "button",
                        "width": 100,
                        "x": 100,
                        "y": 100,
                    },
                ),
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_touch(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    }
                }
            ],
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_touch_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    },
                    "actions": [
                        {
                            "duration": "200ms",
                            "type": "move",
                        }
                    ],
                }
            ],
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_touch(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    }
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_touch(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    }
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_touch(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.touch(
                box_id="",
                points=[
                    {
                        "start": {
                            "x": 100,
                            "y": 150,
                        }
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_type(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_type_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
            include_screenshot=False,
            mode="append",
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            press_enter=False,
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_type(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_type(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_type(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.type(
                box_id="",
                text="Hello World",
            )


class TestAsyncActions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_click_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_click_with_all_params_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
            button="left",
            double=False,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_click_overload_1(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_click_overload_1(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_click_overload_1(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.click(
                box_id="",
                x=350,
                y=250,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_click_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_click_with_all_params_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
            button="left",
            double=False,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_click_overload_2(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_click_overload_2(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_click_overload_2(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.click(
                box_id="",
                target="login button",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_click_overload_3(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_click_with_all_params_overload_3(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
            button="left",
            double=False,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_click_overload_3(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_click_overload_3(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_click_overload_3(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.click(
                box_id="",
                target=cast(
                    DetectedElement,
                    {
                        "id": "1",
                        "center_x": 150,
                        "center_y": 125,
                        "height": 50,
                        "label": "Click me",
                        "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                        "source": "chromium",
                        "type": "button",
                        "width": 100,
                        "x": 100,
                        "y": 100,
                    },
                ),
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clipboard_get(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.clipboard_get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(str, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clipboard_get(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.clipboard_get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(str, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clipboard_get(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.clipboard_get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(str, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_clipboard_get(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.clipboard_get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clipboard_set(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.clipboard_set(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, world!",
        )
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clipboard_set(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.clipboard_set(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, world!",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clipboard_set(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.clipboard_set(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            content="Hello, world!",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert action is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_clipboard_set(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.clipboard_set(
                box_id="",
                content="Hello, world!",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_drag_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_drag_with_all_params_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
            duration="500ms",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_drag_overload_1(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_drag_overload_1(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_drag_overload_1(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.drag(
                box_id="",
                end={
                    "x": 400,
                    "y": 300,
                },
                start={
                    "x": 100,
                    "y": 150,
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_drag_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_drag_with_all_params_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
            duration="50ms",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_drag_overload_2(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_drag_overload_2(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_drag_overload_2(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.drag(
                box_id="",
                path=[
                    {
                        "x": 100,
                        "y": 150,
                    },
                    {
                        "x": 200,
                        "y": 200,
                    },
                    {
                        "x": 300,
                        "y": 250,
                    },
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_elements_detect(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.elements_detect(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionElementsDetectResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_elements_detect_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.elements_detect(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            screenshot={
                "output_format": "base64",
                "presigned_expires_in": "30m",
            },
        )
        assert_matches_type(ActionElementsDetectResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_elements_detect(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.elements_detect(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionElementsDetectResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_elements_detect(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.elements_detect(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionElementsDetectResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_elements_detect(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.elements_detect(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
        )
        assert_matches_type(ActionExtractResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
            schema={},
        )
        assert_matches_type(ActionExtractResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_extract(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionExtractResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_extract(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionExtractResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_extract(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.extract(
                box_id="",
                instruction="Extract the email address from the UI interface",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_long_press_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_long_press_with_all_params_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
            duration="1s",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_long_press_overload_1(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_long_press_overload_1(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_long_press_overload_1(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.long_press(
                box_id="",
                x=350,
                y=250,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_long_press_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="Chrome icon",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_long_press_with_all_params_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="Chrome icon",
            duration="1s",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_long_press_overload_2(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="Chrome icon",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_long_press_overload_2(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="Chrome icon",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_long_press_overload_2(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.long_press(
                box_id="",
                target="Chrome icon",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_long_press_overload_3(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_long_press_with_all_params_overload_3(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
            duration="1s",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_long_press_overload_3(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_long_press_overload_3(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.long_press(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_long_press_overload_3(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.long_press(
                box_id="",
                target=cast(
                    DetectedElement,
                    {
                        "id": "1",
                        "center_x": 150,
                        "center_y": 125,
                        "height": 50,
                        "label": "Click me",
                        "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                        "source": "chromium",
                        "type": "button",
                        "width": 100,
                        "x": 100,
                        "y": 100,
                    },
                ),
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_move(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_move_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_move(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_move(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_move(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.move(
                box_id="",
                x=200,
                y=300,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_press_button(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_press_button_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_press_button(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_press_button(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_press_button(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.press_button(
                box_id="",
                buttons=["power"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_press_key(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_press_key_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
            combination=True,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_press_key(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_press_key(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_press_key(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.press_key(
                box_id="",
                keys=["enter"],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_recording_start(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.recording_start(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_recording_start(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.recording_start(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_recording_start(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.recording_start(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert action is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_recording_start(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.recording_start(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_recording_stop(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.recording_stop(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionRecordingStopResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_recording_stop(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.recording_stop(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionRecordingStopResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_recording_stop(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.recording_stop(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionRecordingStopResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_recording_stop(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.recording_stop(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_rewind_disable(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.rewind_disable(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_rewind_disable(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.rewind_disable(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_rewind_disable(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.rewind_disable(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert action is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_rewind_disable(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.rewind_disable(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_rewind_enable(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.rewind_enable(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_rewind_enable(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.rewind_enable(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert action is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_rewind_enable(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.rewind_enable(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert action is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_rewind_enable(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.rewind_enable(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_rewind_extract(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.rewind_extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionRewindExtractResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_rewind_extract_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.rewind_extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            duration="10s",
        )
        assert_matches_type(ActionRewindExtractResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_rewind_extract(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.rewind_extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionRewindExtractResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_rewind_extract(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.rewind_extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionRewindExtractResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_rewind_extract(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.rewind_extract(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_screen_layout(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.screen_layout(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionScreenLayoutResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_screen_layout(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.screen_layout(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionScreenLayoutResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_screen_layout(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.screen_layout(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionScreenLayoutResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_screen_layout(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.screen_layout(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_screen_rotation(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            orientation="landscapeLeft",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_screen_rotation_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            orientation="landscapeLeft",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_screen_rotation(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            orientation="landscapeLeft",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_screen_rotation(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            orientation="landscapeLeft",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_screen_rotation(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.screen_rotation(
                box_id="",
                orientation="landscapeLeft",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_screenshot(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionScreenshotResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_screenshot_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            clip={
                "height": 600,
                "width": 800,
                "x": 100,
                "y": 50,
            },
            output_format="base64",
            presigned_expires_in="30m",
            save_to_album=False,
            scroll_capture={
                "max_height": 4000,
                "scroll_back": True,
            },
        )
        assert_matches_type(ActionScreenshotResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_screenshot(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionScreenshotResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_screenshot(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionScreenshotResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_screenshot(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.screenshot(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_scroll_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=-100,
            x=400,
            y=300,
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_scroll_with_all_params_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=-100,
            x=400,
            y=300,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_scroll_overload_1(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=-100,
            x=400,
            y=300,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_scroll_overload_1(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=-100,
            x=400,
            y=300,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_scroll_overload_1(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.scroll(
                box_id="",
                scroll_x=0,
                scroll_y=-100,
                x=400,
                y=300,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_scroll_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_scroll_with_all_params_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
            distance=300,
            duration="500ms",
            include_screenshot=False,
            location="Side bar",
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_scroll_overload_2(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_scroll_overload_2(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_scroll_overload_2(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.scroll(
                box_id="",
                direction="up",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_settings(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.settings(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionSettingsResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_settings(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.settings(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionSettingsResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_settings(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.settings(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionSettingsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_settings(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.settings(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_settings_reset(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.settings_reset(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionSettingsResetResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_settings_reset(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.settings_reset(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionSettingsResetResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_settings_reset(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.settings_reset(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionSettingsResetResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_settings_reset(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.settings_reset(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_settings_update(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.settings_update(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scale=1,
        )
        assert_matches_type(ActionSettingsUpdateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_settings_update(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.settings_update(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scale=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionSettingsUpdateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_settings_update(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.settings_update(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scale=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionSettingsUpdateResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_settings_update(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.settings_update(
                box_id="",
                scale=1,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_swipe_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_swipe_with_all_params_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
            distance=300,
            duration="500ms",
            include_screenshot=False,
            location="Chrome App",
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_swipe_overload_1(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_swipe_overload_1(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_swipe_overload_1(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.swipe(
                box_id="",
                direction="up",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_swipe_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_swipe_with_all_params_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
            duration="500ms",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_swipe_overload_2(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_swipe_overload_2(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_swipe_overload_2(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.swipe(
                box_id="",
                end={
                    "x": 400,
                    "y": 300,
                },
                start={
                    "x": 100,
                    "y": 150,
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_tap_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_tap_with_all_params_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_tap_overload_1(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_tap_overload_1(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=350,
            y=250,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_tap_overload_1(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.tap(
                box_id="",
                x=350,
                y=250,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_tap_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_tap_with_all_params_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_tap_overload_2(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_tap_overload_2(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target="login button",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_tap_overload_2(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.tap(
                box_id="",
                target="login button",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_tap_overload_3(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_tap_with_all_params_overload_3(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_tap_overload_3(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_tap_overload_3(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.tap(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            target=cast(
                DetectedElement,
                {
                    "id": "1",
                    "center_x": 150,
                    "center_y": 125,
                    "height": 50,
                    "label": "Click me",
                    "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                    "source": "chromium",
                    "type": "button",
                    "width": 100,
                    "x": 100,
                    "y": 100,
                },
            ),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_tap_overload_3(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.tap(
                box_id="",
                target=cast(
                    DetectedElement,
                    {
                        "id": "1",
                        "center_x": 150,
                        "center_y": 125,
                        "height": 50,
                        "label": "Click me",
                        "path": "#root > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > button",
                        "source": "chromium",
                        "type": "button",
                        "width": 100,
                        "x": 100,
                        "y": 100,
                    },
                ),
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_touch(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    }
                }
            ],
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_touch_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    },
                    "actions": [
                        {
                            "duration": "200ms",
                            "type": "move",
                        }
                    ],
                }
            ],
            include_screenshot=False,
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_touch(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    }
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_touch(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    }
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_touch(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.touch(
                box_id="",
                points=[
                    {
                        "start": {
                            "x": 100,
                            "y": 150,
                        }
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_type(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_type_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
            include_screenshot=False,
            mode="append",
            options={
                "model": "gpt-5",
                "screenshot": {
                    "delay": "500ms",
                    "output_format": "base64",
                    "phases": ["before", "after"],
                    "presigned_expires_in": "30m",
                },
            },
            output_format="base64",
            presigned_expires_in="30m",
            press_enter=False,
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_type(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionResult, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_type(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionResult, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_type(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.type(
                box_id="",
                text="Hello World",
            )
