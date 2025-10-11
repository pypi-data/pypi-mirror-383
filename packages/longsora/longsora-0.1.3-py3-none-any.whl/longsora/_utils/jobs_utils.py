import asyncio
import sys
import time
from typing import TYPE_CHECKING

from loguru import logger

from longsora.openai import OpenAI
from longsora.openai.types.video import Video

if TYPE_CHECKING:
    from longsora._client import AsyncOpenAI


def poll_until_complete(video: Video, client: OpenAI, verbose: bool = True) -> bool:
    # from https://platform.openai.com/docs/guides/video-generation?lang=python
    progress = getattr(video, "progress", 0)
    bar_length = 30
    while video.status in ("in_progress", "queued"):
        # Refresh status
        video = client.videos.retrieve(video.id)
        progress = getattr(video, "progress", 0)
        filled_length = int((progress / 100) * bar_length)
        bar = "=" * filled_length + "-" * (bar_length - filled_length)
        status_text = "Queued" if video.status == "queued" else "Processing"
        if verbose:
            sys.stdout.write(f"\r{status_text}: [{bar}] {progress:.1f}%")
            sys.stdout.flush()
        time.sleep(2)
    if video.status == "failed":
        message = getattr(
            getattr(video, "error", None), "message", "Video generation failed"
        )
        logger.error(f"video:{video}")
        logger.error(message)
        return False
    return True
    # return


async def async_poll_until_complete(
    video: Video, client: "AsyncOpenAI", verbose: bool = True
) -> bool:
    # Async version from https://platform.openai.com/docs/guides/video-generation?lang=python
    progress = getattr(video, "progress", 0)
    bar_length = 30
    while video.status in ("in_progress", "queued"):
        # Refresh status
        video = await client.videos.retrieve(video.id)
        progress = getattr(video, "progress", 0)
        filled_length = int((progress / 100) * bar_length)
        bar = "=" * filled_length + "-" * (bar_length - filled_length)
        status_text = "Queued" if video.status == "queued" else "Processing"
        if verbose:
            sys.stdout.write(f"\r{status_text}: [{bar}] {progress:.1f}%")
            sys.stdout.flush()
        await asyncio.sleep(2)
    if video.status == "failed":
        message = getattr(
            getattr(video, "error", None), "message", "Video generation failed"
        )
        logger.error(message)
        return False
    return True
