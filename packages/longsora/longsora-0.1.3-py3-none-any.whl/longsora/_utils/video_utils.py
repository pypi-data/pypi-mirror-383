from pathlib import Path
from typing import List

import cv2
import ffmpeg


def extract_last_frame(video_path: Path, out_image_path: Path) -> Path:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open {video_path}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    success, frame = False, None

    if total > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, total - 1)
        success, frame = cap.read()
    if not success or frame is None:
        cap.release()
        cap = cv2.VideoCapture(str(video_path))
        while True:
            ret, f = cap.read()
            if not ret:
                break
            frame = f
            success = True
    cap.release()

    if not success or frame is None:
        raise RuntimeError(f"Could not read last frame from {video_path}")

    out_image_path.parent.mkdir(parents=True, exist_ok=True)
    ok = cv2.imwrite(str(out_image_path), frame)
    if not ok:
        raise RuntimeError(f"Failed to write {out_image_path}")
    return out_image_path


def combined_video_segments(segment_paths: List[Path], out_path: Path) -> Path:
    """
    Combine multiple video segments into a single video file using ffmpeg.

    Args:
        segment_paths: List of paths to video segment files to combine
        out_path: Output path for the combined video

    Returns:
        Path to the combined video file
    """
    if not segment_paths:
        raise ValueError("No video segments to combine")

    if len(segment_paths) == 1:
        # If only one segment, just copy it
        import shutil

        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(segment_paths[0], out_path)
        return out_path

    # Create a temporary file list for ffmpeg concat
    out_path.parent.mkdir(parents=True, exist_ok=True)
    concat_file = out_path.parent / "concat_list.txt"

    try:
        # Write the file list in ffmpeg concat format
        with open(concat_file, "w") as f:
            for seg_path in segment_paths:
                # Escape single quotes and wrap path in single quotes
                safe_path = str(seg_path).replace("'", "'\\''")
                f.write(f"file '{safe_path}'\n")

        # Use ffmpeg to concatenate videos
        (
            ffmpeg.input(str(concat_file), format="concat", safe=0)
            .output(str(out_path), c="copy")
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        return out_path

    finally:
        # Clean up temporary concat file
        if concat_file.exists():
            concat_file.unlink()
