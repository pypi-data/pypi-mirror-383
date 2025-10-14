"""videotrim: A fast, efficient video trimming and manipulation toolkit."""

from videotrim.io import VideoReader, VideoWriter
from videotrim.trim import trim_video, TrimMode
from videotrim.utils import get_video_info, frame_to_timestamp, timestamp_to_frame
from videotrim.detection import detect_start_frame

__version__ = "0.1.0"

__all__ = [
    "VideoReader",
    "VideoWriter",
    "trim_video",
    "TrimMode",
    "get_video_info",
    "frame_to_timestamp",
    "timestamp_to_frame",
    "detect_start_frame",
]


def main() -> None:
    """CLI entry point."""
    from videotrim.cli import main as cli_main
    cli_main()
