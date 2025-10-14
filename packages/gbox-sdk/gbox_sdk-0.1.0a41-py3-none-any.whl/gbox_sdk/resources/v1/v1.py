# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .devices import (
    DevicesResource,
    AsyncDevicesResource,
    DevicesResourceWithRawResponse,
    AsyncDevicesResourceWithRawResponse,
    DevicesResourceWithStreamingResponse,
    AsyncDevicesResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .boxes.boxes import (
    BoxesResource,
    AsyncBoxesResource,
    BoxesResourceWithRawResponse,
    AsyncBoxesResourceWithRawResponse,
    BoxesResourceWithStreamingResponse,
    AsyncBoxesResourceWithStreamingResponse,
)

__all__ = ["V1Resource", "AsyncV1Resource"]


class V1Resource(SyncAPIResource):
    @cached_property
    def devices(self) -> DevicesResource:
        return DevicesResource(self._client)

    @cached_property
    def boxes(self) -> BoxesResource:
        return BoxesResource(self._client)

    @cached_property
    def with_raw_response(self) -> V1ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return V1ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> V1ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return V1ResourceWithStreamingResponse(self)


class AsyncV1Resource(AsyncAPIResource):
    @cached_property
    def devices(self) -> AsyncDevicesResource:
        return AsyncDevicesResource(self._client)

    @cached_property
    def boxes(self) -> AsyncBoxesResource:
        return AsyncBoxesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncV1ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncV1ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncV1ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return AsyncV1ResourceWithStreamingResponse(self)


class V1ResourceWithRawResponse:
    def __init__(self, v1: V1Resource) -> None:
        self._v1 = v1

    @cached_property
    def devices(self) -> DevicesResourceWithRawResponse:
        return DevicesResourceWithRawResponse(self._v1.devices)

    @cached_property
    def boxes(self) -> BoxesResourceWithRawResponse:
        return BoxesResourceWithRawResponse(self._v1.boxes)


class AsyncV1ResourceWithRawResponse:
    def __init__(self, v1: AsyncV1Resource) -> None:
        self._v1 = v1

    @cached_property
    def devices(self) -> AsyncDevicesResourceWithRawResponse:
        return AsyncDevicesResourceWithRawResponse(self._v1.devices)

    @cached_property
    def boxes(self) -> AsyncBoxesResourceWithRawResponse:
        return AsyncBoxesResourceWithRawResponse(self._v1.boxes)


class V1ResourceWithStreamingResponse:
    def __init__(self, v1: V1Resource) -> None:
        self._v1 = v1

    @cached_property
    def devices(self) -> DevicesResourceWithStreamingResponse:
        return DevicesResourceWithStreamingResponse(self._v1.devices)

    @cached_property
    def boxes(self) -> BoxesResourceWithStreamingResponse:
        return BoxesResourceWithStreamingResponse(self._v1.boxes)


class AsyncV1ResourceWithStreamingResponse:
    def __init__(self, v1: AsyncV1Resource) -> None:
        self._v1 = v1

    @cached_property
    def devices(self) -> AsyncDevicesResourceWithStreamingResponse:
        return AsyncDevicesResourceWithStreamingResponse(self._v1.devices)

    @cached_property
    def boxes(self) -> AsyncBoxesResourceWithStreamingResponse:
        return AsyncBoxesResourceWithStreamingResponse(self._v1.boxes)
