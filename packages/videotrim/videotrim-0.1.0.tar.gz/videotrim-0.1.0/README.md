# videotrim

A fast, efficient video trimming and manipulation toolkit built on Python.

## Features

- **Fast Video I/O**: Efficient video reading and writing with `imageio` and PyAV backends
- **Frame-Accurate Trimming**: Precise frame-level control with re-encoding support
- **Lossless Copy Mode**: Ultra-fast trimming using ffmpeg's copy mode (when frame accuracy isn't critical)
- **Frame Extraction**: Export individual frames as images
- **Video Concatenation**: Merge multiple videos into one
- **Flexible CLI**: Powerful command-line interface with timestamp and frame-based operations
- **Python API**: Full-featured library for programmatic video manipulation

## Quick Start

### Run without installation (using uv)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run videotrim directly
uvx --from videotrim videotrim --help

# Trim a video (frames 100-500)
uvx --from videotrim videotrim trim input.mp4 output.mp4 --start 100 --end 500

# Trim by timestamps
uvx --from videotrim videotrim trim input.mp4 output.mp4 --start-time 00:10 --end-time 00:30
```

### Install as a tool

```bash
# Install videotrim as a tool
uv tool install videotrim

# Run directly
videotrim --help
videotrim info input.mp4
videotrim trim input.mp4 output.mp4 -s 100 -e 500

# Update to latest version
uv tool upgrade videotrim
```

## Installation

### Install from PyPI (when published)

```bash
# Using pip
pip install videotrim

# Or using uv
uv pip install videotrim
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/talmolab/videotrim.git
cd videotrim

# Install with uv
uv pip install -e .

# Or with dev dependencies
uv pip install -e ".[dev]"
```

## Command Line Usage

### Get video information

```bash
videotrim info input.mp4
```

Output:
```
File: input.mp4
Size: 1,234,567 bytes
Duration: 00:01:23.456
FPS: 30.00
Frames: 2,504
Resolution: 1920x1080
Codec: h264
```

### Trim videos

```bash
# Trim by frame range (frame-accurate with re-encoding)
videotrim trim input.mp4 output.mp4 --start 100 --end 500

# Trim by timestamps (skip first 30 seconds, save next 5 seconds)
videotrim trim input.mp4 output.mp4 --start-time 00:30 --end-time 00:35 --mode encode

# Trim by timestamps with shorthand
videotrim trim input.mp4 output.mp4 --start-time 00:10 --end-time 00:30

# Fast copy mode (no re-encoding, may not be frame-accurate)
videotrim trim input.mp4 output.mp4 -s 100 -e 500 --mode copy

# High quality encode
videotrim trim input.mp4 output.mp4 -s 100 -e 500 --mode encode --quality 10

# Auto mode (automatically choose copy or encode)
videotrim trim input.mp4 output.mp4 -s 100 -e 500 --mode auto
```

### Extract frames

```bash
# Extract all frames as PNG
videotrim extract input.mp4 frames/

# Extract specific range
videotrim extract input.mp4 frames/ --start 100 --end 500

# Extract every 10th frame
videotrim extract input.mp4 frames/ --step 10

# Extract as JPEG with custom prefix
videotrim extract input.mp4 frames/ --format jpg --prefix frame_
```

### Concatenate videos

```bash
# Fast concatenation (copy mode)
videotrim concat output.mp4 part1.mp4 part2.mp4 part3.mp4

# With re-encoding for compatibility
videotrim concat output.mp4 part1.mp4 part2.mp4 --mode encode
```

## Python API

### Basic trimming

```python
from videotrim import trim_video, TrimMode

# Trim with frame-accurate encoding
trim_video(
    "input.mp4",
    "output.mp4",
    start_frame=100,
    end_frame=500,
    mode=TrimMode.ENCODE
)

# Fast copy mode
trim_video(
    "input.mp4",
    "output.mp4",
    start_frame=100,
    end_frame=500,
    mode=TrimMode.COPY
)
```

### Video I/O

```python
from videotrim import VideoReader, VideoWriter

# Read video
with VideoReader("input.mp4") as reader:
    print(f"FPS: {reader.fps}")
    print(f"Frames: {reader.frame_count}")
    print(f"Resolution: {reader.width}x{reader.height}")

    # Read specific frame
    frame = reader.read_frame(42)

    # Read frame range
    frames = reader.read_frames(100, 200)

    # Iterate through all frames
    for frame in reader:
        process_frame(frame)

# Write video
with VideoWriter("output.mp4", fps=30.0, quality=8) as writer:
    for frame in frames:
        writer.write_frame(frame)
```

### Frame extraction

```python
from videotrim import extract_frames

# Extract all frames
num_frames = extract_frames("input.mp4", "frames/")

# Extract every 10th frame
num_frames = extract_frames(
    "input.mp4",
    "frames/",
    step=10,
    format="png"
)
```

### Video concatenation

```python
from videotrim import concatenate_videos, TrimMode

# Concatenate multiple videos
concatenate_videos(
    ["part1.mp4", "part2.mp4", "part3.mp4"],
    "full.mp4",
    mode=TrimMode.COPY
)
```

### Utility functions

```python
from videotrim.utils import (
    get_video_info,
    frame_to_timestamp,
    timestamp_to_frame,
    parse_time_string,
    format_timestamp
)

# Get video metadata
info = get_video_info("input.mp4")
print(info)

# Convert between frames and timestamps
timestamp = frame_to_timestamp(150, fps=30.0)  # 5.0 seconds
frame = timestamp_to_frame(5.0, fps=30.0)  # 150

# Parse time strings
seconds = parse_time_string("01:23:45.5")  # 5025.5

# Format timestamps
time_str = format_timestamp(5025.5)  # "01:23:45.500"
```

## Development

### Running from Source

```bash
# Clone and enter directory
git clone https://github.com/talmolab/videotrim.git
cd videotrim

# Install in development mode with dev dependencies
uv pip install -e ".[dev]"

# Run the CLI
python -m videotrim --help
videotrim --help  # After installation
```

### Running Tests

```bash
# Install dev dependencies if not already installed
uv pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=videotrim --cov-report=html

# Run specific test file
pytest tests/test_io.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format and lint with ruff
ruff check src/ tests/
ruff format src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

## Requirements

- Python e 3.12
- numpy
- imageio
- imageio-ffmpeg
- av (PyAV)
- click

Optional:
- ffmpeg (for fast copy mode trimming and concatenation)

## Architecture

videotrim is built with a modular architecture:

- **`videotrim.io`**: Core video I/O with `VideoReader` and `VideoWriter` classes
- **`videotrim.trim`**: Trimming operations with multiple modes (copy/encode/auto)
- **`videotrim.utils`**: Utility functions for time/frame conversions and validation
- **`videotrim.cli`**: Command-line interface built with Click

The library uses `imageio` with PyAV backend for frame-accurate video operations, and optionally uses `ffmpeg` directly for ultra-fast copy mode operations.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
