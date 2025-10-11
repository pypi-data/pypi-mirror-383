from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Mapping, cast

import httpx

from longsora._utils.jobs_utils import (async_poll_until_complete,
                                        poll_until_complete)
from longsora._utils.prompt_utils import (async_plan_prompts_with_ai,
                                          plan_prompts_with_ai)
from longsora._utils.video_duration_utils import validate_duration
from longsora._utils.video_utils import (combined_video_segments,
                                         extract_last_frame)
from longsora.openai import AsyncOpenAI as AsyncOpenAIBase
from longsora.openai import OpenAI as OpenAIBase
from longsora.openai._base_client import make_request_options
from longsora.openai._types import (Body, FileTypes, Headers, NotGiven, Omit,
                                    Query, not_given, omit)
from longsora.openai._utils import (async_maybe_transform, deepcopy_minimal,
                                    extract_files, maybe_transform)
from longsora.openai._utils._logs import logger
from longsora.openai.types import VideoModel, VideoSize, video_create_params
from longsora.openai.types.video import Video
from longsora.openai.types.video_model import VideoModel
from longsora.openai.types.video_size import VideoSize
from longsora.videos import AsyncVideos, Videos


class OpenAI(OpenAIBase):
    @cached_property
    def videos(self) -> Videos:
        return Videos(self)

    def create_video(
        self,
        *,
        prompt: str,
        input_reference: FileTypes | Omit = omit,
        model: VideoModel | Omit = omit,
        seconds_per_segment: int | Omit = omit,
        size: VideoSize | Omit = omit,
        output_dir: Path,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        num_generations: int = 3,
        plan_model: str = "gpt-5",
        verbose: bool = True,
        save_segments: bool = True,
    ):
        # Validate that total seconds can be formed by combining base durations (4, 8, 12)
        # validate_duration(seconds_per_segment)
        output_dir.mkdir(parents=True, exist_ok=True)
        segments_dir = output_dir / "segments"
        if save_segments:
            segments_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "output.mp4"
        #         def plan_prompts_with_ai(
        #     base_prompt: str,
        #     seconds_per_segment: int,
        #     num_generations: int,
        #     client: "OpenAI",
        #     planner_model: str = "gpt-5",
        # ):
        segments = plan_prompts_with_ai(
            prompt, seconds_per_segment, num_generations, self, plan_model
        )
        # 这个必须是线性的。
        segment_paths = []
        for i, seg in enumerate(segments, start=1):
            secs = int(seg["seconds"])
            prompt = seg["prompt"]
            if verbose:
                logger.debug(
                    f"\n=== Generating Segment {i}/{len(segments)} — {secs}s ==="
                )
            video = self.videos.create(
                prompt=prompt,
                input_reference=input_reference,
                model=model,
                seconds=secs,
                size=size,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )
            if verbose:
                logger.debug(f"video:\n{video}")
            completed = poll_until_complete(video, self, verbose)
            if completed:
                seg_path = segments_dir / f"segment_{i:02d}.mp4"
                content = self.videos.download_content(video.id, variant="video")
                content.write_to_file(seg_path)
                segment_paths.append(seg_path)
                frame_path = segments_dir / f"segment_{i:02d}_last.jpg"
                extract_last_frame(seg_path, frame_path)
                input_reference = frame_path
            else:
                logger.error(f"Video generation failed for segment {i}")
                return
        combined_video_segments(segment_paths, output_path)


class AsyncOpenAI(AsyncOpenAIBase):
    @cached_property
    def videos(self) -> AsyncVideos:
        return AsyncVideos(self)

    async def create_video(
        self,
        *,
        prompt: str,
        input_reference: FileTypes | Omit = omit,
        model: VideoModel | Omit = omit,
        seconds_per_segment: int | Omit = omit,
        size: VideoSize | Omit = omit,
        output_dir: Path,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        num_generations: int = 3,
        plan_model: str = "gpt-5",
        verbose: bool = True,
        save_segments: bool = True,
    ):
        # Validate that total seconds can be formed by combining base durations (4, 8, 12)
        # validate_duration(seconds_per_segment)
        output_dir.mkdir(parents=True, exist_ok=True)
        segments_dir = output_dir / "segments"
        if save_segments:
            segments_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "output.mp4"
        segments = await async_plan_prompts_with_ai(
            prompt, seconds_per_segment, num_generations, self, plan_model
        )
        # 这个必须是线性的。
        segment_paths = []
        for i, seg in enumerate(segments, start=1):
            secs = int(seg["seconds"])
            prompt = seg["prompt"]
            if verbose:
                logger.debug(
                    f"\n=== Generating Segment {i}/{len(segments)} — {secs}s ==="
                )
            video = await self.videos.create(
                prompt=prompt,
                input_reference=input_reference,
                model=model,
                seconds=secs,
                size=size,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )
            if verbose:
                logger.debug(f"video:\n{video}")
            completed = await async_poll_until_complete(video, self, verbose)
            if completed:
                seg_path = segments_dir / f"segment_{i:02d}.mp4"
                content = await self.videos.download_content(video.id, variant="video")
                content.write_to_file(seg_path)
                segment_paths.append(seg_path)
                frame_path = segments_dir / f"segment_{i:02d}_last.jpg"
                extract_last_frame(seg_path, frame_path)
                input_reference = frame_path
            else:
                logger.error(f"Video generation failed for segment {i}")
                return
        combined_video_segments(segment_paths, output_path)
