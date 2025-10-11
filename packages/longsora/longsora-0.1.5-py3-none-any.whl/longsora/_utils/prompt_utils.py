import json
import re
from typing import TYPE_CHECKING

from longsora._utils.prompts import PLANNER_SYSTEM_INSTRUCTIONS

if TYPE_CHECKING:
    from longsora._client import AsyncOpenAI, OpenAI


def plan_prompts_with_ai(
    base_prompt: str,
    seconds_per_segment: int,
    num_generations: int,
    client: "OpenAI",
    planner_model: str = "gpt-5",
):
    # This is from  https://github.com/mshumer/sora-extend
    """
    Calls the Responses API to produce a JSON object:
    {
      "segments": [
        {"title": "...", "seconds": <int>, "prompt": "<full prompt block>"},
        ...
      ]
    }
    """
    # Compose a single plain-text input with the variables:
    user_input = f"""
BASE PROMPT: {base_prompt}

GENERATION LENGTH (seconds): {seconds_per_segment}
TOTAL GENERATIONS: {num_generations}

Return exactly {num_generations} segments.
""".strip()

    # Minimal Responses API call; see docs & library readme for details.
    # (If your account lacks the requested model, change PLANNER_MODEL accordingly.)
    resp = client.responses.create(
        model=planner_model,
        instructions=PLANNER_SYSTEM_INSTRUCTIONS,
        input=user_input,
    )

    text = getattr(resp, "output_text", None) or ""
    if not text:
        # Fallback: collect from structured blocks if needed
        # (Different SDK versions may put text in resp.output or in content items.)
        try:
            # Attempt to reconstruct from generic fields
            text = json.dumps(resp.to_dict())
        except Exception:
            raise RuntimeError("Planner returned no text; try changing PLANNER_MODEL.")

    # Extract the first JSON object found in the response text.
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError(
            "Planner did not return JSON. Inspect response and adjust instructions."
        )
    data = json.loads(m.group(0))

    # Basic validation and enforcement
    segments = data.get("segments", [])
    if len(segments) != num_generations:
        segments = segments[:num_generations]
        # or pad/adjust; here we simply clamp.

    # Force durations to the requested number (some models might deviate)
    for seg in segments:
        seg["seconds"] = int(seconds_per_segment)

    return segments


async def async_plan_prompts_with_ai(
    base_prompt: str,
    seconds_per_segment: int,
    num_generations: int,
    client: "AsyncOpenAI",
    planner_model: str = "gpt-5",
):
    # This is from  https://github.com/mshumer/sora-extend
    """
    Async version: Calls the Responses API to produce a JSON object:
    {
      "segments": [
        {"title": "...", "seconds": <int>, "prompt": "<full prompt block>"},
        ...
      ]
    }
    """
    # Compose a single plain-text input with the variables:
    user_input = f"""
BASE PROMPT: {base_prompt}

GENERATION LENGTH (seconds): {seconds_per_segment}
TOTAL GENERATIONS: {num_generations}

Return exactly {num_generations} segments.
""".strip()

    # Minimal Responses API call; see docs & library readme for details.
    # (If your account lacks the requested model, change PLANNER_MODEL accordingly.)
    resp = await client.responses.create(
        model=planner_model,
        instructions=PLANNER_SYSTEM_INSTRUCTIONS,
        input=user_input,
    )

    text = getattr(resp, "output_text", None) or ""
    if not text:
        # Fallback: collect from structured blocks if needed
        # (Different SDK versions may put text in resp.output or in content items.)
        try:
            # Attempt to reconstruct from generic fields
            text = json.dumps(resp.to_dict())
        except Exception:
            raise RuntimeError("Planner returned no text; try changing PLANNER_MODEL.")

    # Extract the first JSON object found in the response text.
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError(
            "Planner did not return JSON. Inspect response and adjust instructions."
        )
    data = json.loads(m.group(0))

    # Basic validation and enforcement
    segments = data.get("segments", [])
    if len(segments) != num_generations:
        segments = segments[:num_generations]
        # or pad/adjust; here we simply clamp.

    # Force durations to the requested number (some models might deviate)
    for seg in segments:
        seg["seconds"] = int(seconds_per_segment)

    return segments


# segments_plan = plan_prompts_with_ai(BASE_PROMPT, SECONDS_PER_SEGMENT, NUM_GENERATIONS)

# print("AI‑planned segments:\n")
# for i, seg in enumerate(segments_plan, start=1):
#     print(f"[{i:02d}] {seg['seconds']}s — {seg.get('title','(untitled)')}")
#     print(seg["prompt"])
#     print("-" * 80)
