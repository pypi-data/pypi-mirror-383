# LongSoraGen

English | [简体中文](README-zh.md)

This project provides a full OpenAI-compatible API for generating longer Sora videos by intelligently splitting them into segments and ensuring seamless continuity.

## 1. Overview

LongSoraGen overcomes Sora's duration limitations by breaking down long video generation requests into multiple connected segments. The system uses AI-powered planning to create coherent narratives across segments and maintains visual continuity by using the last frame of each segment as a reference for the next.

Some of the code and idea is from https://github.com/mshumer/sora-extend, thank you for their work.

> ⚠️ **Note**: This codebase has not been fully tested yet because I don't have access to the OpenAI API. It should work well generally. If you encounter any problems and are kind enough to help improve this project, I would really appreciate it.

## 2. How It Works

LongSoraGen's main idea follows mshumer's ideas and operates in three main stages:

1. We segment the total video durations into segmentations, and generate prompt for each segmentation.

2. We use the frame from the last video as the frame reference to generate the following frames. 
3. Finally, we combine all the video segments.

## 3. Installation

[FFmpeg](https://ffmpeg.org/) is needed for video processing, please install it first. 

1. Install from pypi:

We have distributed our library to PyPI, check it out:

```bash
pip install longsora
```

2. Install from scratch:

We highly recommend using the `uv` to install the environments:

```bash
uv sync
```

The environment will be installed in `.venv`. Activate it using:

```bash
source .venv/bin/activate
```

### Set up OpenAI API Key:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

## 4. Quick Start

### Basic Example (Synchronous)

```python
from pathlib import Path
from longsora import OpenAI

output_dir = Path("resources") / "case1"
prompt = "A woman is dancing in a bunch of trees."
model = "sora-2"
seconds_per_segment = 8
num_generations = 3
print(f"the video will be {seconds_per_segment * num_generations} seconds long")

if __name__ == "__main__":
    client = OpenAI()
    client.create_video(
        prompt=prompt,
        model=model,
        seconds_per_segment=seconds_per_segment,
        output_dir=output_dir,
        num_generations=num_generations,
        verbose=True,
        save_segments=True,
        plan_model="gpt-5",
    )
```

### Async Example

```python
import asyncio
from pathlib import Path
from longsora import AsyncOpenAI

output_dir = Path("resources") / "case2"
prompt = "A woman is dancing in a bunch of trees."
seconds_per_segment = 8
model = "sora-2"
num_generations = 2

print(f"the video will be {seconds_per_segment * num_generations} seconds long")

async def main():
    client = AsyncOpenAI()
    await client.create_video(
        prompt=prompt,
        model=model,
        seconds_per_segment=seconds_per_segment,
        output_dir=output_dir,
        num_generations=num_generations,
        verbose=True,
        save_segments=True,
        plan_model="gpt-5",
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. License

MIT License

Copyright (c) 2025 LLinkedlist

See [LICENSE](LICENSE) for details.

## 6. Citation

If you use this project in your research or applications, please cite:

```bibtex
@misc{longsoragen2025,
  author = {linkedlist771},
  title = {LongSoraGen: Extended Video Generation with OpenAI Sora},
  year = {2025},
  url = {https://github.com/linkedlist771/LongSoraGen}
}
```
