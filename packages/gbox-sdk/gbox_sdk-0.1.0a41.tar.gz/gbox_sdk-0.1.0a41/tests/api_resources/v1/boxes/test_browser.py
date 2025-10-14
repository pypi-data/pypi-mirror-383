# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gbox_sdk import GboxClient, AsyncGboxClient
from tests.utils import assert_matches_type
from gbox_sdk.types.v1.boxes import (
    BrowserOpenResponse,
    BrowserGetTabsResponse,
    BrowserOpenTabResponse,
    BrowserCloseTabResponse,
    BrowserGetProxyResponse,
    BrowserSwitchTabResponse,
    BrowserUpdateTabResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBrowser:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cdp_url(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.cdp_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(str, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cdp_url_with_all_params(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.cdp_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            expires_in="120m",
        )
        assert_matches_type(str, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cdp_url(self, client: GboxClient) -> None:
        response = client.v1.boxes.browser.with_raw_response.cdp_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(str, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cdp_url(self, client: GboxClient) -> None:
        with client.v1.boxes.browser.with_streaming_response.cdp_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(str, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_cdp_url(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.cdp_url(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clear_proxy(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.clear_proxy(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clear_proxy(self, client: GboxClient) -> None:
        response = client.v1.boxes.browser.with_raw_response.clear_proxy(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clear_proxy(self, client: GboxClient) -> None:
        with client.v1.boxes.browser.with_streaming_response.clear_proxy(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert browser is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_clear_proxy(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.clear_proxy(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_close(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.close(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_close(self, client: GboxClient) -> None:
        response = client.v1.boxes.browser.with_raw_response.close(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_close(self, client: GboxClient) -> None:
        with client.v1.boxes.browser.with_streaming_response.close(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert browser is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_close(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.close(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_close_tab(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.close_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BrowserCloseTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_close_tab(self, client: GboxClient) -> None:
        response = client.v1.boxes.browser.with_raw_response.close_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(BrowserCloseTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_close_tab(self, client: GboxClient) -> None:
        with client.v1.boxes.browser.with_streaming_response.close_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(BrowserCloseTabResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_close_tab(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.close_tab(
                tab_id="tabId",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tab_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.close_tab(
                tab_id="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_proxy(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.get_proxy(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BrowserGetProxyResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_proxy(self, client: GboxClient) -> None:
        response = client.v1.boxes.browser.with_raw_response.get_proxy(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(BrowserGetProxyResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_proxy(self, client: GboxClient) -> None:
        with client.v1.boxes.browser.with_streaming_response.get_proxy(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(BrowserGetProxyResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_proxy(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.get_proxy(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_tabs(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.get_tabs(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BrowserGetTabsResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_tabs(self, client: GboxClient) -> None:
        response = client.v1.boxes.browser.with_raw_response.get_tabs(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(BrowserGetTabsResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_tabs(self, client: GboxClient) -> None:
        with client.v1.boxes.browser.with_streaming_response.get_tabs(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(BrowserGetTabsResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_tabs(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.get_tabs(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_open(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.open(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BrowserOpenResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_open_with_all_params(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.open(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            maximize=False,
            show_controls=True,
            size="1024x768",
        )
        assert_matches_type(BrowserOpenResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_open(self, client: GboxClient) -> None:
        response = client.v1.boxes.browser.with_raw_response.open(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(BrowserOpenResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_open(self, client: GboxClient) -> None:
        with client.v1.boxes.browser.with_streaming_response.open(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(BrowserOpenResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_open(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.open(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_open_tab(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.open_tab(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            url="https://www.google.com",
        )
        assert_matches_type(BrowserOpenTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_open_tab(self, client: GboxClient) -> None:
        response = client.v1.boxes.browser.with_raw_response.open_tab(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            url="https://www.google.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(BrowserOpenTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_open_tab(self, client: GboxClient) -> None:
        with client.v1.boxes.browser.with_streaming_response.open_tab(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            url="https://www.google.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(BrowserOpenTabResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_open_tab(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.open_tab(
                box_id="",
                url="https://www.google.com",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_proxy(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.set_proxy(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            http_server="http://127.0.0.1:8080",
            https_server="https://127.0.0.1:8080",
            socks5_server="socks5://127.0.0.1:8080",
        )
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_proxy_with_all_params(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.set_proxy(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            http_server="http://127.0.0.1:8080",
            https_server="https://127.0.0.1:8080",
            socks5_server="socks5://127.0.0.1:8080",
            bypass_list=[
                "127.0.0.1",
                "localhost",
                "example.com",
                "*.example.com",
                "*.example.org",
                "https://x.*.y.com:99",
                "192.168.1.1/16",
                "fefe:13::abc/33",
            ],
            pac_url="http://proxy.company.com/proxy.pac",
        )
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_set_proxy(self, client: GboxClient) -> None:
        response = client.v1.boxes.browser.with_raw_response.set_proxy(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            http_server="http://127.0.0.1:8080",
            https_server="https://127.0.0.1:8080",
            socks5_server="socks5://127.0.0.1:8080",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_set_proxy(self, client: GboxClient) -> None:
        with client.v1.boxes.browser.with_streaming_response.set_proxy(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            http_server="http://127.0.0.1:8080",
            https_server="https://127.0.0.1:8080",
            socks5_server="socks5://127.0.0.1:8080",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert browser is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_set_proxy(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.set_proxy(
                box_id="",
                http_server="http://127.0.0.1:8080",
                https_server="https://127.0.0.1:8080",
                socks5_server="socks5://127.0.0.1:8080",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_switch_tab(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.switch_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BrowserSwitchTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_switch_tab(self, client: GboxClient) -> None:
        response = client.v1.boxes.browser.with_raw_response.switch_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(BrowserSwitchTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_switch_tab(self, client: GboxClient) -> None:
        with client.v1.boxes.browser.with_streaming_response.switch_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(BrowserSwitchTabResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_switch_tab(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.switch_tab(
                tab_id="tabId",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tab_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.switch_tab(
                tab_id="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_tab(self, client: GboxClient) -> None:
        browser = client.v1.boxes.browser.update_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            url="https://www.google.com",
        )
        assert_matches_type(BrowserUpdateTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_tab(self, client: GboxClient) -> None:
        response = client.v1.boxes.browser.with_raw_response.update_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            url="https://www.google.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = response.parse()
        assert_matches_type(BrowserUpdateTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_tab(self, client: GboxClient) -> None:
        with client.v1.boxes.browser.with_streaming_response.update_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            url="https://www.google.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = response.parse()
            assert_matches_type(BrowserUpdateTabResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_tab(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.update_tab(
                tab_id="tabId",
                box_id="",
                url="https://www.google.com",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tab_id` but received ''"):
            client.v1.boxes.browser.with_raw_response.update_tab(
                tab_id="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                url="https://www.google.com",
            )


class TestAsyncBrowser:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cdp_url(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.cdp_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(str, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cdp_url_with_all_params(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.cdp_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            expires_in="120m",
        )
        assert_matches_type(str, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cdp_url(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.browser.with_raw_response.cdp_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(str, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cdp_url(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.browser.with_streaming_response.cdp_url(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(str, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_cdp_url(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.cdp_url(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clear_proxy(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.clear_proxy(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clear_proxy(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.browser.with_raw_response.clear_proxy(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clear_proxy(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.browser.with_streaming_response.clear_proxy(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert browser is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_clear_proxy(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.clear_proxy(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_close(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.close(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_close(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.browser.with_raw_response.close(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_close(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.browser.with_streaming_response.close(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert browser is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_close(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.close(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_close_tab(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.close_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BrowserCloseTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_close_tab(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.browser.with_raw_response.close_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(BrowserCloseTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_close_tab(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.browser.with_streaming_response.close_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(BrowserCloseTabResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_close_tab(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.close_tab(
                tab_id="tabId",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tab_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.close_tab(
                tab_id="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_proxy(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.get_proxy(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BrowserGetProxyResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_proxy(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.browser.with_raw_response.get_proxy(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(BrowserGetProxyResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_proxy(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.browser.with_streaming_response.get_proxy(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(BrowserGetProxyResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_proxy(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.get_proxy(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_tabs(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.get_tabs(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BrowserGetTabsResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_tabs(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.browser.with_raw_response.get_tabs(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(BrowserGetTabsResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_tabs(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.browser.with_streaming_response.get_tabs(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(BrowserGetTabsResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_tabs(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.get_tabs(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_open(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.open(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BrowserOpenResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_open_with_all_params(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.open(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            maximize=False,
            show_controls=True,
            size="1024x768",
        )
        assert_matches_type(BrowserOpenResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_open(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.browser.with_raw_response.open(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(BrowserOpenResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_open(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.browser.with_streaming_response.open(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(BrowserOpenResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_open(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.open(
                box_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_open_tab(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.open_tab(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            url="https://www.google.com",
        )
        assert_matches_type(BrowserOpenTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_open_tab(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.browser.with_raw_response.open_tab(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            url="https://www.google.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(BrowserOpenTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_open_tab(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.browser.with_streaming_response.open_tab(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            url="https://www.google.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(BrowserOpenTabResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_open_tab(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.open_tab(
                box_id="",
                url="https://www.google.com",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_proxy(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.set_proxy(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            http_server="http://127.0.0.1:8080",
            https_server="https://127.0.0.1:8080",
            socks5_server="socks5://127.0.0.1:8080",
        )
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_proxy_with_all_params(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.set_proxy(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            http_server="http://127.0.0.1:8080",
            https_server="https://127.0.0.1:8080",
            socks5_server="socks5://127.0.0.1:8080",
            bypass_list=[
                "127.0.0.1",
                "localhost",
                "example.com",
                "*.example.com",
                "*.example.org",
                "https://x.*.y.com:99",
                "192.168.1.1/16",
                "fefe:13::abc/33",
            ],
            pac_url="http://proxy.company.com/proxy.pac",
        )
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_set_proxy(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.browser.with_raw_response.set_proxy(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            http_server="http://127.0.0.1:8080",
            https_server="https://127.0.0.1:8080",
            socks5_server="socks5://127.0.0.1:8080",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert browser is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_set_proxy(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.browser.with_streaming_response.set_proxy(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            http_server="http://127.0.0.1:8080",
            https_server="https://127.0.0.1:8080",
            socks5_server="socks5://127.0.0.1:8080",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert browser is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_set_proxy(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.set_proxy(
                box_id="",
                http_server="http://127.0.0.1:8080",
                https_server="https://127.0.0.1:8080",
                socks5_server="socks5://127.0.0.1:8080",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_switch_tab(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.switch_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(BrowserSwitchTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_switch_tab(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.browser.with_raw_response.switch_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(BrowserSwitchTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_switch_tab(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.browser.with_streaming_response.switch_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(BrowserSwitchTabResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_switch_tab(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.switch_tab(
                tab_id="tabId",
                box_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tab_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.switch_tab(
                tab_id="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_tab(self, async_client: AsyncGboxClient) -> None:
        browser = await async_client.v1.boxes.browser.update_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            url="https://www.google.com",
        )
        assert_matches_type(BrowserUpdateTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_tab(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.browser.with_raw_response.update_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            url="https://www.google.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        browser = await response.parse()
        assert_matches_type(BrowserUpdateTabResponse, browser, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_tab(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.browser.with_streaming_response.update_tab(
            tab_id="tabId",
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            url="https://www.google.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            browser = await response.parse()
            assert_matches_type(BrowserUpdateTabResponse, browser, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_tab(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.update_tab(
                tab_id="tabId",
                box_id="",
                url="https://www.google.com",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tab_id` but received ''"):
            await async_client.v1.boxes.browser.with_raw_response.update_tab(
                tab_id="",
                box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
                url="https://www.google.com",
            )
