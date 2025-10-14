# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Mapping, cast

import httpx

from ...._types import (
    Body,
    Omit,
    Query,
    Headers,
    NoneType,
    NotGiven,
    FileTypes,
    SequenceNotStr,
    omit,
    not_given,
)
from ...._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    to_custom_raw_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v1.boxes import media_create_album_params, media_update_album_params
from ....types.v1.boxes.media_album import MediaAlbum
from ....types.v1.boxes.media_get_media_response import MediaGetMediaResponse
from ....types.v1.boxes.media_list_media_response import MediaListMediaResponse
from ....types.v1.boxes.media_list_albums_response import MediaListAlbumsResponse
from ....types.v1.boxes.media_get_media_support_response import MediaGetMediaSupportResponse

__all__ = ["MediaResource", "AsyncMediaResource"]


class MediaResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MediaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return MediaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MediaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return MediaResourceWithStreamingResponse(self)

    def create_album(
        self,
        box_id: str,
        *,
        name: str,
        media: SequenceNotStr[FileTypes] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaAlbum:
        """
        Create a new album with media files

        Args:
          name: Name of the album to create

          media: Media files to include in the album (max size: 512MB per file)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        body = deepcopy_minimal(
            {
                "name": name,
                "media": media,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["media", "<array>"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            f"/boxes/{box_id}/media/albums",
            body=maybe_transform(body, media_create_album_params.MediaCreateAlbumParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=MediaAlbum,
        )

    def delete_album(
        self,
        album_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete an album and all its media files

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/boxes/{box_id}/media/albums/{album_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=NoneType,
        )

    def delete_media(
        self,
        media_name: str,
        *,
        box_id: str,
        album_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a specific media file from an album

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        if not media_name:
            raise ValueError(f"Expected a non-empty value for `media_name` but received {media_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/boxes/{box_id}/media/albums/{album_name}/media/{media_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=NoneType,
        )

    def download_media(
        self,
        media_name: str,
        *,
        box_id: str,
        album_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BinaryAPIResponse:
        """
        Download a specific media file from an album

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        if not media_name:
            raise ValueError(f"Expected a non-empty value for `media_name` but received {media_name!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return self._get(
            f"/boxes/{box_id}/media/albums/{album_name}/media/{media_name}/download",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=BinaryAPIResponse,
        )

    def get_album_detail(
        self,
        album_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaAlbum:
        """
        Get detailed information about a specific album including its media files

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        return self._get(
            f"/boxes/{box_id}/media/albums/{album_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=MediaAlbum,
        )

    def get_media(
        self,
        media_name: str,
        *,
        box_id: str,
        album_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaGetMediaResponse:
        """
        Get detailed information about a specific media file

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        if not media_name:
            raise ValueError(f"Expected a non-empty value for `media_name` but received {media_name!r}")
        return cast(
            MediaGetMediaResponse,
            self._get(
                f"/boxes/{box_id}/media/albums/{album_name}/media/{media_name}",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                ),
                cast_to=cast(
                    Any, MediaGetMediaResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def get_media_support(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaGetMediaSupportResponse:
        """
        Get supported media file extensions for photos and videos

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/media/support",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=MediaGetMediaSupportResponse,
        )

    def list_albums(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaListAlbumsResponse:
        """
        Get a list of albums in the box

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return self._get(
            f"/boxes/{box_id}/media/albums",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=MediaListAlbumsResponse,
        )

    def list_media(
        self,
        album_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaListMediaResponse:
        """
        Get a list of media files in a specific album

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        return self._get(
            f"/boxes/{box_id}/media/albums/{album_name}/media",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=MediaListMediaResponse,
        )

    def update_album(
        self,
        album_name: str,
        *,
        box_id: str,
        media: SequenceNotStr[FileTypes],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaAlbum:
        """
        Add media files to an existing album

        Args:
          media: Media files to add to the album (max size: 512MB per file)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        body = deepcopy_minimal({"media": media})
        files = extract_files(cast(Mapping[str, object], body), paths=[["media", "<array>"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._patch(
            f"/boxes/{box_id}/media/albums/{album_name}",
            body=maybe_transform(body, media_update_album_params.MediaUpdateAlbumParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=MediaAlbum,
        )


class AsyncMediaResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMediaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncMediaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMediaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/babelcloud/gbox-sdk-py#with_streaming_response
        """
        return AsyncMediaResourceWithStreamingResponse(self)

    async def create_album(
        self,
        box_id: str,
        *,
        name: str,
        media: SequenceNotStr[FileTypes] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaAlbum:
        """
        Create a new album with media files

        Args:
          name: Name of the album to create

          media: Media files to include in the album (max size: 512MB per file)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        body = deepcopy_minimal(
            {
                "name": name,
                "media": media,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["media", "<array>"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            f"/boxes/{box_id}/media/albums",
            body=await async_maybe_transform(body, media_create_album_params.MediaCreateAlbumParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=MediaAlbum,
        )

    async def delete_album(
        self,
        album_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete an album and all its media files

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/boxes/{box_id}/media/albums/{album_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=NoneType,
        )

    async def delete_media(
        self,
        media_name: str,
        *,
        box_id: str,
        album_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a specific media file from an album

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        if not media_name:
            raise ValueError(f"Expected a non-empty value for `media_name` but received {media_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/boxes/{box_id}/media/albums/{album_name}/media/{media_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=NoneType,
        )

    async def download_media(
        self,
        media_name: str,
        *,
        box_id: str,
        album_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncBinaryAPIResponse:
        """
        Download a specific media file from an album

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        if not media_name:
            raise ValueError(f"Expected a non-empty value for `media_name` but received {media_name!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return await self._get(
            f"/boxes/{box_id}/media/albums/{album_name}/media/{media_name}/download",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def get_album_detail(
        self,
        album_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaAlbum:
        """
        Get detailed information about a specific album including its media files

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        return await self._get(
            f"/boxes/{box_id}/media/albums/{album_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=MediaAlbum,
        )

    async def get_media(
        self,
        media_name: str,
        *,
        box_id: str,
        album_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaGetMediaResponse:
        """
        Get detailed information about a specific media file

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        if not media_name:
            raise ValueError(f"Expected a non-empty value for `media_name` but received {media_name!r}")
        return cast(
            MediaGetMediaResponse,
            await self._get(
                f"/boxes/{box_id}/media/albums/{album_name}/media/{media_name}",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                ),
                cast_to=cast(
                    Any, MediaGetMediaResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def get_media_support(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaGetMediaSupportResponse:
        """
        Get supported media file extensions for photos and videos

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/media/support",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=MediaGetMediaSupportResponse,
        )

    async def list_albums(
        self,
        box_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaListAlbumsResponse:
        """
        Get a list of albums in the box

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        return await self._get(
            f"/boxes/{box_id}/media/albums",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=MediaListAlbumsResponse,
        )

    async def list_media(
        self,
        album_name: str,
        *,
        box_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaListMediaResponse:
        """
        Get a list of media files in a specific album

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        return await self._get(
            f"/boxes/{box_id}/media/albums/{album_name}/media",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=MediaListMediaResponse,
        )

    async def update_album(
        self,
        album_name: str,
        *,
        box_id: str,
        media: SequenceNotStr[FileTypes],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MediaAlbum:
        """
        Add media files to an existing album

        Args:
          media: Media files to add to the album (max size: 512MB per file)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not box_id:
            raise ValueError(f"Expected a non-empty value for `box_id` but received {box_id!r}")
        if not album_name:
            raise ValueError(f"Expected a non-empty value for `album_name` but received {album_name!r}")
        body = deepcopy_minimal({"media": media})
        files = extract_files(cast(Mapping[str, object], body), paths=[["media", "<array>"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._patch(
            f"/boxes/{box_id}/media/albums/{album_name}",
            body=await async_maybe_transform(body, media_update_album_params.MediaUpdateAlbumParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=MediaAlbum,
        )


class MediaResourceWithRawResponse:
    def __init__(self, media: MediaResource) -> None:
        self._media = media

        self.create_album = to_raw_response_wrapper(
            media.create_album,
        )
        self.delete_album = to_raw_response_wrapper(
            media.delete_album,
        )
        self.delete_media = to_raw_response_wrapper(
            media.delete_media,
        )
        self.download_media = to_custom_raw_response_wrapper(
            media.download_media,
            BinaryAPIResponse,
        )
        self.get_album_detail = to_raw_response_wrapper(
            media.get_album_detail,
        )
        self.get_media = to_raw_response_wrapper(
            media.get_media,
        )
        self.get_media_support = to_raw_response_wrapper(
            media.get_media_support,
        )
        self.list_albums = to_raw_response_wrapper(
            media.list_albums,
        )
        self.list_media = to_raw_response_wrapper(
            media.list_media,
        )
        self.update_album = to_raw_response_wrapper(
            media.update_album,
        )


class AsyncMediaResourceWithRawResponse:
    def __init__(self, media: AsyncMediaResource) -> None:
        self._media = media

        self.create_album = async_to_raw_response_wrapper(
            media.create_album,
        )
        self.delete_album = async_to_raw_response_wrapper(
            media.delete_album,
        )
        self.delete_media = async_to_raw_response_wrapper(
            media.delete_media,
        )
        self.download_media = async_to_custom_raw_response_wrapper(
            media.download_media,
            AsyncBinaryAPIResponse,
        )
        self.get_album_detail = async_to_raw_response_wrapper(
            media.get_album_detail,
        )
        self.get_media = async_to_raw_response_wrapper(
            media.get_media,
        )
        self.get_media_support = async_to_raw_response_wrapper(
            media.get_media_support,
        )
        self.list_albums = async_to_raw_response_wrapper(
            media.list_albums,
        )
        self.list_media = async_to_raw_response_wrapper(
            media.list_media,
        )
        self.update_album = async_to_raw_response_wrapper(
            media.update_album,
        )


class MediaResourceWithStreamingResponse:
    def __init__(self, media: MediaResource) -> None:
        self._media = media

        self.create_album = to_streamed_response_wrapper(
            media.create_album,
        )
        self.delete_album = to_streamed_response_wrapper(
            media.delete_album,
        )
        self.delete_media = to_streamed_response_wrapper(
            media.delete_media,
        )
        self.download_media = to_custom_streamed_response_wrapper(
            media.download_media,
            StreamedBinaryAPIResponse,
        )
        self.get_album_detail = to_streamed_response_wrapper(
            media.get_album_detail,
        )
        self.get_media = to_streamed_response_wrapper(
            media.get_media,
        )
        self.get_media_support = to_streamed_response_wrapper(
            media.get_media_support,
        )
        self.list_albums = to_streamed_response_wrapper(
            media.list_albums,
        )
        self.list_media = to_streamed_response_wrapper(
            media.list_media,
        )
        self.update_album = to_streamed_response_wrapper(
            media.update_album,
        )


class AsyncMediaResourceWithStreamingResponse:
    def __init__(self, media: AsyncMediaResource) -> None:
        self._media = media

        self.create_album = async_to_streamed_response_wrapper(
            media.create_album,
        )
        self.delete_album = async_to_streamed_response_wrapper(
            media.delete_album,
        )
        self.delete_media = async_to_streamed_response_wrapper(
            media.delete_media,
        )
        self.download_media = async_to_custom_streamed_response_wrapper(
            media.download_media,
            AsyncStreamedBinaryAPIResponse,
        )
        self.get_album_detail = async_to_streamed_response_wrapper(
            media.get_album_detail,
        )
        self.get_media = async_to_streamed_response_wrapper(
            media.get_media,
        )
        self.get_media_support = async_to_streamed_response_wrapper(
            media.get_media_support,
        )
        self.list_albums = async_to_streamed_response_wrapper(
            media.list_albums,
        )
        self.list_media = async_to_streamed_response_wrapper(
            media.list_media,
        )
        self.update_album = async_to_streamed_response_wrapper(
            media.update_album,
        )
