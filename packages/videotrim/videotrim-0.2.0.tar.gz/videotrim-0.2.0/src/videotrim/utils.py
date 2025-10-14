"""Utility functions for video processing."""

from pathlib import Path
from typing import Dict, Union, Tuple
import imageio.v3 as iio


def get_video_info(path: Union[str, Path]) -> Dict[str, Union[int, float, str]]:
    """Get comprehensive video file information.

    Args:
        path: Path to the video file

    Returns:
        Dictionary containing video metadata:
            - fps: Frames per second
            - frame_count: Total number of frames
            - duration: Duration in seconds
            - width: Frame width in pixels
            - height: Frame height in pixels
            - codec: Video codec name
            - size_bytes: File size in bytes

    Example:
        >>> info = get_video_info("video.mp4")
        >>> print(f"Video has {info['frame_count']} frames at {info['fps']} fps")
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {path}")

    # Get properties
    props = iio.improps(str(path), plugin="FFMPEG")
    metadata = iio.immeta(str(path), plugin="FFMPEG")

    # Extract fps and duration from metadata (immeta, not improps)
    fps = metadata.get("fps", 30.0)
    duration = metadata.get("duration", 0.0)
    frame_count = int(fps * duration)

    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration": duration,
        "width": props.shape[2],
        "height": props.shape[1],
        "channels": props.shape[3],
        "codec": metadata.get("codec", "unknown"),
        "size_bytes": path.stat().st_size,
    }


def frame_to_timestamp(frame: int, fps: float) -> float:
    """Convert frame index to timestamp in seconds.

    Args:
        frame: Frame index (0-based)
        fps: Frames per second

    Returns:
        Timestamp in seconds

    Example:
        >>> frame_to_timestamp(150, 30.0)
        5.0
    """
    return frame / fps


def timestamp_to_frame(timestamp: float, fps: float, round_method: str = "round") -> int:
    """Convert timestamp in seconds to frame index.

    Args:
        timestamp: Timestamp in seconds
        fps: Frames per second
        round_method: Rounding method - "round", "floor", or "ceil"

    Returns:
        Frame index (0-based)

    Example:
        >>> timestamp_to_frame(5.0, 30.0)
        150
    """
    frame_float = timestamp * fps

    if round_method == "round":
        return round(frame_float)
    elif round_method == "floor":
        return int(frame_float)
    elif round_method == "ceil":
        import math
        return math.ceil(frame_float)
    else:
        raise ValueError(f"Invalid round_method: {round_method}")


def parse_time_string(time_str: str) -> float:
    """Parse time string in various formats to seconds.

    Supported formats:
        - Seconds: "42" or "42.5"
        - MM:SS: "1:23"
        - HH:MM:SS: "1:23:45"
        - HH:MM:SS.mmm: "1:23:45.678"

    Args:
        time_str: Time string in supported format

    Returns:
        Time in seconds

    Example:
        >>> parse_time_string("1:23:45.5")
        5025.5
    """
    parts = time_str.split(":")

    if len(parts) == 1:
        # Just seconds
        return float(parts[0])
    elif len(parts) == 2:
        # MM:SS
        minutes, seconds = parts
        return float(minutes) * 60 + float(seconds)
    elif len(parts) == 3:
        # HH:MM:SS
        hours, minutes, seconds = parts
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    else:
        raise ValueError(f"Invalid time format: {time_str}")


def format_timestamp(seconds: float, include_ms: bool = True) -> str:
    """Format seconds as HH:MM:SS or HH:MM:SS.mmm string.

    Args:
        seconds: Time in seconds
        include_ms: Include milliseconds in output

    Returns:
        Formatted time string

    Example:
        >>> format_timestamp(5025.5)
        '01:23:45.500'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    if include_ms:
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    else:
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d}"


def validate_frame_range(
    start: int, end: int, total_frames: int
) -> Tuple[int, int]:
    """Validate and normalize frame range.

    Args:
        start: Start frame (inclusive)
        end: End frame (exclusive)
        total_frames: Total number of frames in video

    Returns:
        Validated (start, end) tuple

    Raises:
        ValueError: If range is invalid
    """
    if start < 0:
        raise ValueError(f"Start frame must be >= 0, got {start}")
    if end > total_frames:
        raise ValueError(
            f"End frame {end} exceeds total frames {total_frames}"
        )
    if start >= end:
        raise ValueError(
            f"Start frame {start} must be less than end frame {end}"
        )

    return start, end
