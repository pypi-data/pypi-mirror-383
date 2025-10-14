"""Video I/O operations using imageio-ffmpeg backend."""

from pathlib import Path
from typing import Optional, Tuple, Union
import numpy as np
import imageio.v3 as iio


class VideoReader:
    """Read video files frame-by-frame with efficient seeking.

    This class provides a high-level interface for reading video files,
    with support for frame extraction, metadata access, and efficient
    random access to frames.

    Args:
        path: Path to the video file

    Attributes:
        path: Path to the video file
        fps: Frames per second
        frame_count: Total number of frames
        duration: Duration in seconds
        width: Frame width in pixels
        height: Frame height in pixels
        codec: Video codec name

    Example:
        >>> with VideoReader("input.mp4") as reader:
        ...     for frame in reader:
        ...         process_frame(frame)
    """

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Video file not found: {self.path}")

        # Get video properties using FFMPEG plugin
        props = iio.improps(str(self.path), plugin="FFMPEG")
        metadata = iio.immeta(str(self.path), plugin="FFMPEG")

        # Extract metadata (immeta has fps, duration, codec)
        self._fps = metadata.get("fps", 30.0)
        self._duration = metadata.get("duration", 0.0)
        self._codec = metadata.get("codec", "unknown")

        # Calculate frame count from fps * duration
        # Note: improps returns n_images=inf for videos, so we calculate it
        self._frame_count = int(self._fps * self._duration)

        # Get shape from props (n_frames, height, width, channels)
        # Note: props.shape[0] is inf for videos, so we use our calculated frame_count
        self._shape = (self._frame_count, props.shape[1], props.shape[2], props.shape[3])

        self._reader = None
        self._current_frame = 0

    @property
    def fps(self) -> float:
        """Frames per second."""
        return self._fps

    @property
    def frame_count(self) -> int:
        """Total number of frames."""
        return self._frame_count

    @property
    def duration(self) -> float:
        """Duration in seconds."""
        return self._duration

    @property
    def width(self) -> int:
        """Frame width in pixels."""
        return self._shape[2]

    @property
    def height(self) -> int:
        """Frame height in pixels."""
        return self._shape[1]

    @property
    def codec(self) -> str:
        """Video codec name."""
        return self._codec

    @property
    def shape(self) -> Tuple[int, int, int]:
        """Frame shape (height, width, channels)."""
        return (self._shape[1], self._shape[2], self._shape[3])

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __iter__(self):
        """Iterate over all frames."""
        self._reader = iio.imiter(str(self.path), plugin="FFMPEG")
        self._current_frame = 0
        return self

    def __next__(self) -> np.ndarray:
        """Get next frame."""
        if self._reader is None:
            raise StopIteration

        try:
            frame = next(self._reader)
            self._current_frame += 1
            return frame
        except StopIteration:
            self._reader = None
            raise

    def read_frame(self, index: int) -> np.ndarray:
        """Read a specific frame by index.

        Args:
            index: Frame index (0-based)

        Returns:
            Frame as numpy array with shape (height, width, channels)

        Raises:
            IndexError: If frame index is out of bounds
        """
        if index < 0 or index >= self.frame_count:
            raise IndexError(
                f"Frame index {index} out of bounds [0, {self.frame_count})"
            )

        return iio.imread(str(self.path), index=index, plugin="FFMPEG")

    def read_frames(
        self, start: int = 0, end: Optional[int] = None, step: int = 1
    ) -> np.ndarray:
        """Read a range of frames.

        Args:
            start: Starting frame index (inclusive)
            end: Ending frame index (exclusive), None for end of video
            step: Frame step size

        Returns:
            Array of frames with shape (n_frames, height, width, channels)
        """
        if end is None:
            end = self.frame_count

        if start < 0 or start >= self.frame_count:
            raise IndexError(
                f"Start frame {start} out of bounds [0, {self.frame_count})"
            )
        if end < 0 or end > self.frame_count:
            raise IndexError(
                f"End frame {end} out of bounds [0, {self.frame_count}]"
            )
        if start >= end:
            raise ValueError(f"Start frame {start} must be less than end frame {end}")

        indices = list(range(start, end, step))
        frames = []

        for idx in indices:
            frames.append(self.read_frame(idx))

        return np.stack(frames)

    def close(self):
        """Close the video reader."""
        if self._reader is not None:
            self._reader = None


class VideoWriter:
    """Write video files frame-by-frame with customizable encoding.

    This class provides a high-level interface for writing video files,
    with support for various codecs, quality settings, and pixel formats.

    Note: This implementation collects frames in memory and writes them all
    at once using imwrite(), as imageio's streaming write mode has issues
    with FPS and frame timing.

    Args:
        path: Output path for the video file
        fps: Frames per second
        codec: Video codec (default: "libx264")
        quality: Quality setting, 0-10 where 10 is highest (default: 7)
        pixel_format: Pixel format (default: "yuv420p")
        macro_block_size: Macro block size, dimensions must be divisible by this
        **kwargs: Additional ffmpeg output arguments

    Example:
        >>> with VideoWriter("output.mp4", fps=30) as writer:
        ...     for frame in frames:
        ...         writer.write_frame(frame)
    """

    def __init__(
        self,
        path: Union[str, Path],
        fps: float,
        codec: str = "libx264",
        quality: int = 7,
        pixel_format: str = "yuv420p",
        macro_block_size: int = 2,
        **kwargs,
    ):
        self.path = Path(path)
        self.fps = fps
        self.codec = codec
        self.quality = quality
        self.pixel_format = pixel_format
        self.macro_block_size = macro_block_size
        self._kwargs = kwargs

        # Collect frames in memory
        self._frames = []
        self._shape = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def write_frame(self, frame: np.ndarray):
        """Write a single frame to the video.

        Args:
            frame: Frame as numpy array with shape (height, width, channels)

        Raises:
            ValueError: If frame shape doesn't match previous frames
        """
        if self._shape is None:
            self._shape = frame.shape
            height, width, channels = frame.shape

            # Ensure dimensions are divisible by macro block size
            if height % self.macro_block_size != 0:
                raise ValueError(
                    f"Height {height} must be divisible by {self.macro_block_size}"
                )
            if width % self.macro_block_size != 0:
                raise ValueError(
                    f"Width {width} must be divisible by {self.macro_block_size}"
                )

        if frame.shape != self._shape:
            raise ValueError(
                f"Frame shape {frame.shape} doesn't match initialized shape {self._shape}"
            )

        # Collect frame in memory
        self._frames.append(frame.copy())

    def write_frames(self, frames: np.ndarray):
        """Write multiple frames to the video.

        Args:
            frames: Array of frames with shape (n_frames, height, width, channels)
        """
        for frame in frames:
            self.write_frame(frame)

    @property
    def frame_count(self) -> int:
        """Number of frames written so far."""
        return len(self._frames)

    def close(self):
        """Close the video writer and write all frames to disk."""
        if len(self._frames) > 0:
            # Stack frames into 4D array
            frames_array = np.stack(self._frames)

            # Prepare output parameters
            output_params = {
                "fps": self.fps,
                "codec": self.codec,
                "quality": self.quality,
                "pixelformat": self.pixel_format,
                "macro_block_size": self.macro_block_size,
                **self._kwargs,
            }

            # Write all frames at once using imwrite
            iio.imwrite(
                str(self.path),
                frames_array,
                plugin="FFMPEG",
                extension=self.path.suffix,
                **output_params,
            )

            # Clear frames from memory
            self._frames = []
