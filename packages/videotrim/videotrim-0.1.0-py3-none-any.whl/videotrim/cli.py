"""Command-line interface for videotrim."""

import sys
from pathlib import Path
from typing import Optional
import click

from videotrim.trim import trim_video, extract_frames, concatenate_videos, TrimMode
from videotrim.utils import (
    get_video_info,
    parse_time_string,
    timestamp_to_frame,
    format_timestamp,
)
from videotrim import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """videotrim: Fast, efficient video trimming and manipulation toolkit.

    \b
    Examples:
        # Trim video by frame range
        videotrim trim input.mp4 output.mp4 --start 100 --end 500

        # Trim video by timestamps
        videotrim trim input.mp4 output.mp4 --start-time 00:10 --end-time 00:30

        # Extract frames to images
        videotrim extract input.mp4 frames/ --start 0 --end 100

        # Get video information
        videotrim info input.mp4

        # Concatenate videos
        videotrim concat output.mp4 part1.mp4 part2.mp4 part3.mp4
    """
    pass


@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--start", "-s", type=int, default=0, help="Start frame (0-based)")
@click.option("--end", "-e", type=int, default=None, help="End frame (exclusive)")
@click.option("--start-time", "-st", type=str, help="Start time (HH:MM:SS or seconds)")
@click.option("--end-time", "-et", type=str, help="End time (HH:MM:SS or seconds)")
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["copy", "encode", "auto"]),
    default="auto",
    help="Trimming mode: copy (fast), encode (accurate), auto (choose)",
)
@click.option(
    "--codec",
    "-c",
    type=str,
    default="libx264",
    help="Video codec for encoding mode",
)
@click.option(
    "--quality",
    "-q",
    type=int,
    default=7,
    help="Quality (0-10, 10=highest) for encoding mode",
)
@click.option(
    "--pixel-format",
    "-pf",
    type=str,
    default="yuv420p",
    help="Pixel format for encoding mode",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def trim(
    input: str,
    output: str,
    start: int,
    end: Optional[int],
    start_time: Optional[str],
    end_time: Optional[str],
    mode: str,
    codec: str,
    quality: int,
    pixel_format: str,
    verbose: bool,
):
    """Trim a video to a specified frame range or time range.

    \b
    Examples:
        # Trim by frame numbers
        videotrim trim input.mp4 output.mp4 --start 100 --end 500

        # Trim by timestamps
        videotrim trim input.mp4 output.mp4 --start-time 00:10 --end-time 00:30

        # Fast copy mode (may not be frame-accurate)
        videotrim trim input.mp4 output.mp4 -s 100 -e 500 --mode copy

        # High quality encode
        videotrim trim input.mp4 output.mp4 -s 100 -e 500 --mode encode -q 10
    """
    try:
        input_path = Path(input)

        # Get video info for time conversions
        from videotrim.io import VideoReader

        with VideoReader(input_path) as reader:
            fps = reader.fps
            total_frames = reader.frame_count

            # Convert time strings to frames if provided
            if start_time:
                start_seconds = parse_time_string(start_time)
                start = timestamp_to_frame(start_seconds, fps)
                if verbose:
                    click.echo(f"Start time {start_time} → frame {start}")

            if end_time:
                end_seconds = parse_time_string(end_time)
                end = timestamp_to_frame(end_seconds, fps)
                if verbose:
                    click.echo(f"End time {end_time} → frame {end}")

            if end is None:
                end = total_frames

            # Show info
            if verbose:
                click.echo(f"Input: {input_path}")
                click.echo(f"Output: {output}")
                click.echo(f"FPS: {fps}")
                click.echo(f"Total frames: {total_frames}")
                click.echo(f"Trimming: frames {start} to {end} ({end - start} frames)")
                click.echo(f"Mode: {mode}")

        # Perform trim
        trim_mode = TrimMode(mode)
        trim_video(
            input_path,
            output,
            start_frame=start,
            end_frame=end,
            mode=trim_mode,
            codec=codec,
            quality=quality,
            pixel_format=pixel_format,
        )

        click.echo(f"✓ Trimmed video saved to {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.argument("output-dir", type=click.Path())
@click.option("--start", "-s", type=int, default=0, help="Start frame (0-based)")
@click.option("--end", "-e", type=int, default=None, help="End frame (exclusive)")
@click.option("--step", type=int, default=1, help="Extract every Nth frame")
@click.option(
    "--format",
    "-f",
    type=str,
    default="png",
    help="Image format (png, jpg, etc.)",
)
@click.option("--prefix", "-p", type=str, default="frame_", help="Filename prefix")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def extract(
    input: str,
    output_dir: str,
    start: int,
    end: Optional[int],
    step: int,
    format: str,
    prefix: str,
    verbose: bool,
):
    """Extract frames from a video as individual images.

    \b
    Examples:
        # Extract all frames as PNG
        videotrim extract input.mp4 frames/

        # Extract every 10th frame
        videotrim extract input.mp4 frames/ --step 10

        # Extract specific range as JPEG
        videotrim extract input.mp4 frames/ -s 100 -e 500 --format jpg
    """
    try:
        if verbose:
            click.echo(f"Extracting frames from {input}")
            click.echo(f"Output directory: {output_dir}")
            click.echo(f"Format: {format}")
            click.echo(f"Step: {step}")

        num_frames = extract_frames(
            input,
            output_dir,
            start_frame=start,
            end_frame=end,
            step=step,
            format=format,
            prefix=prefix,
        )

        click.echo(f"✓ Extracted {num_frames} frames to {output_dir}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def info(input: str, output_json: bool):
    """Display information about a video file.

    \b
    Examples:
        # Show video info
        videotrim info input.mp4

        # Output as JSON
        videotrim info input.mp4 --json
    """
    try:
        video_info = get_video_info(input)

        if output_json:
            import json
            click.echo(json.dumps(video_info, indent=2))
        else:
            click.echo(f"File: {input}")
            click.echo(f"Size: {video_info['size_bytes']:,} bytes")
            click.echo(f"Duration: {format_timestamp(video_info['duration'])}")
            click.echo(f"FPS: {video_info['fps']:.2f}")
            click.echo(f"Frames: {video_info['frame_count']:,}")
            click.echo(
                f"Resolution: {video_info['width']}x{video_info['height']}"
            )
            click.echo(f"Codec: {video_info['codec']}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("output", type=click.Path())
@click.argument("inputs", nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["copy", "encode"]),
    default="copy",
    help="Concatenation mode: copy (fast), encode (compatible)",
)
@click.option(
    "--codec",
    "-c",
    type=str,
    default="libx264",
    help="Video codec for encoding mode",
)
@click.option(
    "--quality",
    "-q",
    type=int,
    default=7,
    help="Quality (0-10, 10=highest) for encoding mode",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def concat(
    output: str,
    inputs: tuple[str, ...],
    mode: str,
    codec: str,
    quality: int,
    verbose: bool,
):
    """Concatenate multiple video files into one.

    \b
    Examples:
        # Fast concatenation with copy
        videotrim concat output.mp4 part1.mp4 part2.mp4 part3.mp4

        # With re-encoding for compatibility
        videotrim concat output.mp4 part1.mp4 part2.mp4 --mode encode
    """
    try:
        if verbose:
            click.echo(f"Concatenating {len(inputs)} videos:")
            for i, inp in enumerate(inputs, 1):
                click.echo(f"  {i}. {inp}")
            click.echo(f"Output: {output}")
            click.echo(f"Mode: {mode}")

        trim_mode = TrimMode.COPY if mode == "copy" else TrimMode.ENCODE
        concatenate_videos(
            list(inputs),
            output,
            mode=trim_mode,
            codec=codec,
            quality=quality,
        )

        click.echo(f"✓ Concatenated video saved to {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
