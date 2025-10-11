from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, cast

import httpx

from longsora.openai._base_client import make_request_options
from longsora.openai._types import (Body, FileTypes, Headers, NotGiven, Omit,
                                    Query, not_given, omit)
from longsora.openai._utils import (async_maybe_transform, deepcopy_minimal,
                                    extract_files, maybe_transform)
from longsora.openai.resources.videos import AsyncVideos as AsyncVideosBase
from longsora.openai.resources.videos import Videos as VideosBase
from longsora.openai.types import (VideoModel, VideoSeconds, VideoSize,
                                   video_create_params)
from longsora.openai.types.video import Video
from longsora.openai.types.video_model import VideoModel
from longsora.openai.types.video_seconds import VideoSeconds
from longsora.openai.types.video_size import VideoSize


class Videos(VideosBase):
    def create(
        self,
        *,
        prompt: str,
        input_reference: FileTypes | Omit = omit,
        model: VideoModel | Omit = omit,
        seconds: VideoSeconds | Omit = omit,
        size: VideoSize | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """
        Create a video

        Args:
          prompt: Text prompt that describes the video to generate.

          input_reference: Optional image reference that guides generation.

          model: The video generation model to use. Defaults to `sora-2`.

          seconds: Clip duration in seconds. Defaults to 4 seconds.

          size: Output resolution formatted as width x height. Defaults to 720x1280.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "prompt": prompt,
                "input_reference": input_reference,
                "model": model,
                "seconds": seconds,
                "size": size,
            }
        )
        files = extract_files(
            cast(Mapping[str, object], body), paths=[["input_reference"]]
        )
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {
                "Content-Type": "multipart/form-data",
                **(extra_headers or {}),
            }
        return self._post(
            "/videos",
            body=maybe_transform(body, video_create_params.VideoCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=Video,
        )


class AsyncVideos(AsyncVideosBase):
    async def create(
        self,
        *,
        prompt: str,
        input_reference: FileTypes | Omit = omit,
        model: VideoModel | Omit = omit,
        seconds: VideoSeconds | Omit = omit,
        size: VideoSize | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """
        Create a video

        Args:
          prompt: Text prompt that describes the video to generate.

          input_reference: Optional image reference that guides generation.

          model: The video generation model to use. Defaults to `sora-2`.

          seconds: Clip duration in seconds. Defaults to 4 seconds.

          size: Output resolution formatted as width x height. Defaults to 720x1280.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "prompt": prompt,
                "input_reference": input_reference,
                "model": model,
                "seconds": seconds,
                "size": size,
            }
        )
        files = extract_files(
            cast(Mapping[str, object], body), paths=[["input_reference"]]
        )
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {
                "Content-Type": "multipart/form-data",
                **(extra_headers or {}),
            }
        return await self._post(
            "/videos",
            body=await async_maybe_transform(
                body, video_create_params.VideoCreateParams
            ),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=Video,
        )
