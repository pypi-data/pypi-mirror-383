"""Video trimming operations."""

from enum import Enum
from pathlib import Path
from typing import Optional, Union
import subprocess
import shutil

from videotrim.io import VideoReader, VideoWriter
from videotrim.utils import validate_frame_range, frame_to_timestamp


class TrimMode(Enum):
    """Trimming mode selection.

    COPY: Fast lossless copy without re-encoding (may not be frame-accurate)
    ENCODE: Frame-accurate trimming with re-encoding (slower but precise)
    AUTO: Automatically choose based on codec and accuracy requirements
    """

    COPY = "copy"
    ENCODE = "encode"
    AUTO = "auto"


def trim_video(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    start_frame: int = 0,
    end_frame: Optional[int] = None,
    mode: TrimMode = TrimMode.AUTO,
    codec: str = "libx264",
    quality: int = 7,
    pixel_format: str = "yuv420p",
    **kwargs,
) -> None:
    """Trim a video to a specified frame range.

    Args:
        input_path: Path to input video file
        output_path: Path to output video file
        start_frame: Starting frame (inclusive, 0-based)
        end_frame: Ending frame (exclusive), None for end of video
        mode: Trimming mode (COPY for fast, ENCODE for accurate, AUTO to choose)
        codec: Video codec for encoding mode (default: "libx264")
        quality: Quality setting for encoding mode, 0-10 (default: 7)
        pixel_format: Pixel format for encoding mode (default: "yuv420p")
        **kwargs: Additional arguments for VideoWriter

    Example:
        >>> # Trim frames 100-500 with fast copy
        >>> trim_video("input.mp4", "output.mp4", 100, 500, mode=TrimMode.COPY)
        >>>
        >>> # Trim with frame-accurate encoding
        >>> trim_video("input.mp4", "output.mp4", 100, 500, mode=TrimMode.ENCODE)

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If frame range is invalid
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input video not found: {input_path}")

    # Read video info
    with VideoReader(input_path) as reader:
        total_frames = reader.frame_count
        fps = reader.fps

        # Validate frame range
        if end_frame is None:
            end_frame = total_frames
        start_frame, end_frame = validate_frame_range(start_frame, end_frame, total_frames)

        # Decide on trimming mode
        actual_mode = mode
        if mode == TrimMode.AUTO:
            # Use COPY for full-second boundaries, ENCODE otherwise
            start_time = frame_to_timestamp(start_frame, fps)
            end_time = frame_to_timestamp(end_frame, fps)
            if start_time == int(start_time) and end_time == int(end_time):
                actual_mode = TrimMode.COPY
            else:
                actual_mode = TrimMode.ENCODE

        # Perform trimming
        if actual_mode == TrimMode.COPY:
            _trim_copy(input_path, output_path, start_frame, end_frame, fps)
        else:
            _trim_encode(
                reader,
                output_path,
                start_frame,
                end_frame,
                codec,
                quality,
                pixel_format,
                **kwargs,
            )


def _trim_copy(
    input_path: Path,
    output_path: Path,
    start_frame: int,
    end_frame: int,
    fps: float,
) -> None:
    """Trim video using fast copy mode (no re-encoding).

    This uses ffmpeg's copy mode for very fast trimming, but may not be
    frame-accurate due to keyframe constraints.

    Args:
        input_path: Path to input video
        output_path: Path to output video
        start_frame: Starting frame (inclusive)
        end_frame: Ending frame (exclusive)
        fps: Frames per second
    """
    # Check if ffmpeg is available
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "ffmpeg not found. Install ffmpeg or use mode=TrimMode.ENCODE"
        )

    # Convert frames to timestamps
    start_time = frame_to_timestamp(start_frame, fps)
    duration = frame_to_timestamp(end_frame - start_frame, fps)

    # Build ffmpeg command
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-ss", str(start_time),  # Start time
        "-i", str(input_path),  # Input file
        "-t", str(duration),  # Duration
        "-c", "copy",  # Copy codec (no re-encoding)
        "-avoid_negative_ts", "make_zero",  # Fix timestamp issues
        str(output_path),
    ]

    # Run ffmpeg
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed with code {result.returncode}:\n{result.stderr}"
        )


def _trim_encode(
    reader: VideoReader,
    output_path: Path,
    start_frame: int,
    end_frame: int,
    codec: str,
    quality: int,
    pixel_format: str,
    **kwargs,
) -> None:
    """Trim video using encoding mode (frame-accurate).

    This reads and re-encodes the video for perfect frame accuracy,
    but is slower than copy mode.

    Args:
        reader: VideoReader instance for input video
        output_path: Path to output video
        start_frame: Starting frame (inclusive)
        end_frame: Ending frame (exclusive)
        codec: Video codec
        quality: Quality setting 0-10
        pixel_format: Pixel format
        **kwargs: Additional VideoWriter arguments
    """
    # Read frames
    frames = reader.read_frames(start_frame, end_frame)

    # Write to output
    with VideoWriter(
        output_path,
        fps=reader.fps,
        codec=codec,
        quality=quality,
        pixel_format=pixel_format,
        **kwargs,
    ) as writer:
        writer.write_frames(frames)


def extract_frames(
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    start_frame: int = 0,
    end_frame: Optional[int] = None,
    step: int = 1,
    format: str = "png",
    prefix: str = "frame_",
) -> int:
    """Extract individual frames from a video as images.

    Args:
        input_path: Path to input video file
        output_dir: Directory to save extracted frames
        start_frame: Starting frame (inclusive, 0-based)
        end_frame: Ending frame (exclusive), None for end of video
        step: Extract every Nth frame
        format: Image format (png, jpg, etc.)
        prefix: Filename prefix for extracted frames

    Returns:
        Number of frames extracted

    Example:
        >>> # Extract all frames as PNG
        >>> extract_frames("video.mp4", "frames/")
        >>>
        >>> # Extract every 10th frame
        >>> extract_frames("video.mp4", "frames/", step=10)
    """
    import imageio.v3 as iio

    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with VideoReader(input_path) as reader:
        if end_frame is None:
            end_frame = reader.frame_count

        start_frame, end_frame = validate_frame_range(
            start_frame, end_frame, reader.frame_count
        )

        frame_indices = list(range(start_frame, end_frame, step))
        num_digits = len(str(end_frame))

        for i, frame_idx in enumerate(frame_indices):
            frame = reader.read_frame(frame_idx)
            filename = f"{prefix}{frame_idx:0{num_digits}d}.{format}"
            output_path = output_dir / filename
            iio.imwrite(output_path, frame)

        return len(frame_indices)


def concatenate_videos(
    input_paths: list[Union[str, Path]],
    output_path: Union[str, Path],
    mode: TrimMode = TrimMode.COPY,
    codec: str = "libx264",
    quality: int = 7,
    **kwargs,
) -> None:
    """Concatenate multiple video files into one.

    Args:
        input_paths: List of input video file paths
        output_path: Path to output video file
        mode: Concatenation mode (COPY for fast, ENCODE for compatibility)
        codec: Video codec for encoding mode
        quality: Quality setting for encoding mode
        **kwargs: Additional VideoWriter arguments

    Example:
        >>> # Fast concatenation
        >>> concatenate_videos(["part1.mp4", "part2.mp4"], "full.mp4")
        >>>
        >>> # With re-encoding for compatibility
        >>> concatenate_videos(
        ...     ["part1.mp4", "part2.mp4"],
        ...     "full.mp4",
        ...     mode=TrimMode.ENCODE
        ... )
    """
    input_paths = [Path(p) for p in input_paths]
    output_path = Path(output_path)

    if not input_paths:
        raise ValueError("No input videos provided")

    for path in input_paths:
        if not path.exists():
            raise FileNotFoundError(f"Input video not found: {path}")

    if mode == TrimMode.COPY:
        _concatenate_copy(input_paths, output_path)
    else:
        _concatenate_encode(input_paths, output_path, codec, quality, **kwargs)


def _concatenate_copy(input_paths: list[Path], output_path: Path) -> None:
    """Concatenate videos using fast copy mode."""
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "ffmpeg not found. Install ffmpeg or use mode=TrimMode.ENCODE"
        )

    # Create concat file list
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        concat_file = Path(f.name)
        for path in input_paths:
            f.write(f"file '{path.absolute()}'\n")

    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path),
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"ffmpeg failed with code {result.returncode}:\n{result.stderr}"
            )
    finally:
        concat_file.unlink()


def _concatenate_encode(
    input_paths: list[Path],
    output_path: Path,
    codec: str,
    quality: int,
    **kwargs,
) -> None:
    """Concatenate videos with re-encoding."""
    # Read first video to get properties
    with VideoReader(input_paths[0]) as reader:
        fps = reader.fps

    # Open writer
    with VideoWriter(
        output_path,
        fps=fps,
        codec=codec,
        quality=quality,
        **kwargs,
    ) as writer:
        # Process each input video
        for input_path in input_paths:
            with VideoReader(input_path) as reader:
                for frame in reader:
                    writer.write_frame(frame)
