# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.boxes import proxy_set_params
from ....types.v1.boxes.proxy_get_response import ProxyGetResponse
from ....types.v1.boxes.proxy_set_response import ProxySetResponse

__all__ = ["ProxyResource", "AsyncProxyResource"]


class ProxyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProxyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return ProxyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProxyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return ProxyResourceWithStreamingResponse(self)

    def clear(
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
        Clears the HTTP proxy for the box

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
            f"/boxes/{box_id}/proxy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProxyGetResponse:
        """Retrieves the HTTP proxy settings for a specific box.

        Use this endpoint to route
        traffic through the box's network.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/proxy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProxyGetResponse,
        )

    def set(
        self,
        box_id: str,
        *,
        host: str,
        port: float,
        auth: proxy_set_params.Auth | Omit = omit,
        excludes: SequenceNotStr[str] | Omit = omit,
        pac_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProxySetResponse:
        """Configures the HTTP proxy settings for a specific box.

        Use this endpoint when
        you need the box's outbound network traffic to pass through a proxy server.

        Args:
          host: The host address of the proxy server

          port: The port number of the proxy server

          auth: Box Proxy Auth

          excludes: List of IP addresses and domains that should bypass the proxy. These addresses
              will be accessed directly without going through the proxy server. Default is
              ['127.0.0.1', 'localhost']

          pac_url: PAC (Proxy Auto-Configuration) URL.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._post(
            f"/boxes/{box_id}/proxy",
            body=maybe_transform(
                {
                    "host": host,
                    "port": port,
                    "auth": auth,
                    "excludes": excludes,
                    "pac_url": pac_url,
                },
                proxy_set_params.ProxySetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProxySetResponse,
        )


class AsyncProxyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProxyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncProxyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProxyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return AsyncProxyResourceWithStreamingResponse(self)

    async def clear(
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
        Clears the HTTP proxy for the box

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
            f"/boxes/{box_id}/proxy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProxyGetResponse:
        """Retrieves the HTTP proxy settings for a specific box.

        Use this endpoint to route
        traffic through the box's network.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/proxy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProxyGetResponse,
        )

    async def set(
        self,
        box_id: str,
        *,
        host: str,
        port: float,
        auth: proxy_set_params.Auth | Omit = omit,
        excludes: SequenceNotStr[str] | Omit = omit,
        pac_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProxySetResponse:
        """Configures the HTTP proxy settings for a specific box.

        Use this endpoint when
        you need the box's outbound network traffic to pass through a proxy server.

        Args:
          host: The host address of the proxy server

          port: The port number of the proxy server

          auth: Box Proxy Auth

          excludes: List of IP addresses and domains that should bypass the proxy. These addresses
              will be accessed directly without going through the proxy server. Default is
              ['127.0.0.1', 'localhost']

          pac_url: PAC (Proxy Auto-Configuration) URL.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._post(
            f"/boxes/{box_id}/proxy",
            body=await async_maybe_transform(
                {
                    "host": host,
                    "port": port,
                    "auth": auth,
                    "excludes": excludes,
                    "pac_url": pac_url,
                },
                proxy_set_params.ProxySetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProxySetResponse,
        )


class ProxyResourceWithRawResponse:
    def __init__(self, proxy: ProxyResource) -> None:
        self._proxy = proxy

        self.clear = to_raw_response_wrapper(
            proxy.clear,
        )
        self.get = to_raw_response_wrapper(
            proxy.get,
        )
        self.set = to_raw_response_wrapper(
            proxy.set,
        )


class AsyncProxyResourceWithRawResponse:
    def __init__(self, proxy: AsyncProxyResource) -> None:
        self._proxy = proxy

        self.clear = async_to_raw_response_wrapper(
            proxy.clear,
        )
        self.get = async_to_raw_response_wrapper(
            proxy.get,
        )
        self.set = async_to_raw_response_wrapper(
            proxy.set,
        )


class ProxyResourceWithStreamingResponse:
    def __init__(self, proxy: ProxyResource) -> None:
        self._proxy = proxy

        self.clear = to_streamed_response_wrapper(
            proxy.clear,
        )
        self.get = to_streamed_response_wrapper(
            proxy.get,
        )
        self.set = to_streamed_response_wrapper(
            proxy.set,
        )


class AsyncProxyResourceWithStreamingResponse:
    def __init__(self, proxy: AsyncProxyResource) -> None:
        self._proxy = proxy

        self.clear = async_to_streamed_response_wrapper(
            proxy.clear,
        )
        self.get = async_to_streamed_response_wrapper(
            proxy.get,
        )
        self.set = async_to_streamed_response_wrapper(
            proxy.set,
        )
