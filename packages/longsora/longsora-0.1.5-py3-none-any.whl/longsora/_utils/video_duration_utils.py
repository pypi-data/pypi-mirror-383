"""
Video duration validation utilities.

Uses dynamic programming to check if a total duration can be formed
by combining allowed base durations (coin change problem).
"""

from typing import get_args

from longsora.openai.types.video_seconds import VideoSeconds


def can_form_duration(total_seconds: int) -> bool:
    """
    Check if total_seconds can be formed by combining allowed VideoSeconds values.

    Uses dynamic programming (coin change approach) to determine if the total
    can be formed using the base durations: 4, 8, 12 seconds.

    Args:
        total_seconds: Total duration to validate

    Returns:
        True if the duration can be formed, False otherwise

    Examples:
        >>> can_form_duration(4)   # 4
        True
        >>> can_form_duration(8)   # 8 or 4+4
        True
        >>> can_form_duration(12)  # 12 or 8+4 or 4+4+4
        True
        >>> can_form_duration(16)  # 12+4 or 8+8 or 4+4+4+4
        True
        >>> can_form_duration(20)  # 12+8 or 12+4+4
        True
        >>> can_form_duration(3)   # Cannot be formed
        False
        >>> can_form_duration(5)   # Cannot be formed
        False
    """
    if total_seconds <= 0:
        return False

    # Get base durations from VideoSeconds type
    allowed_str = get_args(VideoSeconds)  # ("4", "8", "12")
    base_durations = [int(s) for s in allowed_str]

    # Dynamic programming: dp[i] = True if we can form duration i
    dp = [False] * (total_seconds + 1)
    dp[0] = True  # Base case: 0 seconds can always be formed (use nothing)

    # For each duration from 1 to total_seconds
    for i in range(1, total_seconds + 1):
        # Try each base duration
        for base in base_durations:
            if i >= base and dp[i - base]:
                dp[i] = True
                break

    return dp[total_seconds]


def validate_duration(total_seconds: int) -> None:
    """
    Validate that total_seconds can be formed by combining allowed VideoSeconds values.

    Args:
        total_seconds: Total duration to validate

    Raises:
        ValueError: If the duration cannot be formed from base durations

    Examples:
        >>> validate_duration(16)  # OK
        >>> validate_duration(5)   # Raises ValueError
    """
    if not can_form_duration(total_seconds):
        allowed_str = get_args(VideoSeconds)
        base_durations = [int(s) for s in allowed_str]
        raise ValueError(
            f"Duration {total_seconds} seconds cannot be formed by combining "
            f"base durations {base_durations}. "
            f"Valid examples: 4, 8, 12, 16 (12+4), 20 (12+8), 24 (12+12), etc."
        )
