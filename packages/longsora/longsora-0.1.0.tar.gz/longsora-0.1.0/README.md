# LongSoraGen

This project provides a full OpenAI-compatible API for generating longer Sora videos by intelligently splitting them into segments and ensuring seamless continuity.

## 1. Overview

LongSoraGen overcomes Sora's duration limitations by breaking down long video generation requests into multiple connected segments. The system uses AI-powered planning to create coherent narratives across segments and maintains visual continuity by using the last frame of each segment as a reference for the next.

### Key Features

- **Extended Duration Support**: Generate videos longer than Sora's standard limits
- **AI-Powered Segmentation**: Uses GPT models to intelligently plan segment transitions
- **Visual Continuity**: Automatically extracts last frames as reference images for seamless transitions
- **OpenAI-Compatible API**: Drop-in replacement for standard OpenAI client
- **Async Support**: Full async/await support for better performance
- **Flexible Duration Planning**: Validates and combines base durations (4s, 8s, 12s) to achieve target length

## 2. How It Works

LongSoraGen operates in three main stages:

1. **AI Planning**: Uses the OpenAI Responses API with GPT models to break down your base prompt into `N` coherent segments, each with its own refined prompt that maintains narrative continuity.

2. **Sequential Generation**: Generates each video segment in order:
   - Creates the first segment using the original prompt
   - Extracts the last frame from each completed segment
   - Uses that frame as `input_reference` for the next segment to ensure visual consistency

3. **Video Combination**: Automatically combines all segments into a single output video using FFmpeg.

The duration validation uses dynamic programming to ensure your requested total duration can be formed from Sora's base durations (4, 8, 12 seconds). For example:
- 16 seconds = 12 + 4 or 8 + 8 or 4 + 4 + 4 + 4
- 24 seconds = 12 + 12 or 12 + 8 + 4
- 20 seconds = 12 + 8 or 12 + 4 + 4

## 3. Installation

We highly recommend using `uv` to manage the environment:

### Install dependencies:
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
total_seconds = 24

if __name__ == "__main__":
    client = OpenAI()
    client.create_video(
        prompt=prompt,
        model=model,
        seconds=total_seconds,
        output_dir=output_dir,
        num_generations=3,
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

async def main():
    client = AsyncOpenAI()
    await client.create_video(
        prompt="A woman is dancing in a bunch of trees.",
        model="sora-2",
        seconds=16,
        output_dir=Path("resources") / "case2",
        num_generations=2,
        verbose=True,
        save_segments=True,
        plan_model="gpt-5",
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. API Reference

### `client.create_video()`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | `str` | ✓ | - | Base prompt for video generation |
| `model` | `str` | ✗ | `"sora-2"` | Sora model to use |
| `seconds` | `int` | ✓ | - | Total video duration (must be formable from 4, 8, 12) |
| `output_dir` | `Path` | ✓ | - | Directory to save output and segments |
| `num_generations` | `int` | ✗ | `3` | Number of segments to split the video into |
| `plan_model` | `str` | ✗ | `"gpt-5"` | GPT model for segment planning |
| `verbose` | `bool` | ✗ | `True` | Enable detailed logging |
| `save_segments` | `bool` | ✗ | `True` | Save individual segments to disk |
| `size` | `str` | ✗ | - | Video resolution (e.g., "1080x1920") |
| `input_reference` | `FileTypes` | ✗ | - | Initial reference image/video |

**Output:**

The final combined video is saved as `output.mp4` in the specified `output_dir`. If `save_segments=True`, individual segments are saved in `output_dir/segments/`:
- `segment_01.mp4`, `segment_02.mp4`, etc.
- `segment_01_last.jpg`, `segment_02_last.jpg`, etc. (last frame extractions)

## 6. Examples

### Generate a 24-second video with 3 segments (8 seconds each)

```python
from pathlib import Path
from longsora import OpenAI

client = OpenAI()
client.create_video(
    prompt="A sunset over the ocean with waves crashing",
    seconds=24,
    output_dir=Path("outputs/sunset"),
    num_generations=3,  # Will create 3×8s segments
)
```

### Generate a 20-second video with custom model

```python
client.create_video(
    prompt="A futuristic cityscape at night",
    model="sora-2",
    seconds=20,
    output_dir=Path("outputs/city"),
    num_generations=5,  # Will create 5×4s segments
    plan_model="gpt-4o",  # Use GPT-4 for planning
)
```

## 7. Technical Details

### Segment Planning

LongSoraGen uses the OpenAI Responses API to create intelligent segment prompts. The AI planner:
- Analyzes your base prompt
- Generates `num_generations` segment prompts that tell a cohesive story
- Ensures each segment flows naturally into the next
- Returns structured JSON with prompts and durations

### Visual Continuity

To ensure smooth transitions between segments:
1. After generating each segment, the last frame is extracted using OpenCV
2. This frame becomes the `input_reference` for the next segment
3. Sora uses this reference to maintain visual consistency

### Duration Validation

The system validates that your requested duration can be formed by combining Sora's base durations using a dynamic programming algorithm (coin change problem).

**Valid durations include:**
- 4, 8, 12 (base durations)
- 16, 20, 24, 28, 32... (combinations)

**Invalid durations:**
- 1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15...

## 8. Dependencies

The project uses:
- **OpenAI SDK**: For Sora and GPT API access
- **FFmpeg**: For video processing and combination
- **OpenCV**: For frame extraction
- **httpx**: For async HTTP requests
- **Pydantic**: For data validation

See `pyproject.toml` for full dependency list.

## 9. License

MIT License

Copyright (c) 2025 LLinkedlist

See [LICENSE](LICENSE) for details.

## 10. Acknowledgments

- **OpenAI** for the Sora and GPT APIs
- **mshumer/sora-extend** for inspiration on the prompt planning approach
- **FFmpeg** for video processing capabilities

## 11. Citation

If you use this project in your research or applications, please cite:

```bibtex
@misc{longsoragen2025,
  author = {linkedlist771},
  title = {LongSoraGen: Extended Video Generation with OpenAI Sora},
  year = {2025},
  url = {https://github.com/linkedlist771/LongSoraGen}
}
```

## 12. Troubleshooting

### Invalid Duration Error

If you get a `ValueError` about invalid duration:
- Ensure your `seconds` parameter can be formed from 4, 8, and 12
- Example: 15 seconds is invalid (cannot be formed), but 16 seconds is valid (12+4)

### API Key Issues

Make sure your `OPENAI_API_KEY` environment variable is set:
```bash
export OPENAI_API_KEY='sk-...'
```

### FFmpeg Not Found

Install FFmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## 13. Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 14. Roadmap

- [ ] Add support for custom segment duration distributions
- [ ] Implement parallel segment generation where possible
- [ ] Add video quality/style consistency controls
- [ ] Support for audio continuation across segments
- [ ] Web UI for easier interaction
