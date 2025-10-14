"""Video content detection algorithms.

This module provides automatic detection of video content transitions,
such as identifying when a video starts after initial "hand at start" frames.
"""

from pathlib import Path
from typing import Optional, Union, Dict, Any
import numpy as np
import cv2

from videotrim.io import VideoReader


def detect_start_frame(
    video_path: Union[str, Path],
    coarse_samples: int = 10,
    downsample_factor: int = 4,
    binary_search_samples_per_iteration: int = 5,
    final_window_size: int = 10,
    verbose: bool = False,
) -> int:
    """Automatically detect the start frame of video content using motion detection.

    This function uses a hierarchical motion-based detection approach to identify
    when a video's actual content begins, useful for removing initial frames where
    a hand or object obstructs the view.

    The algorithm works in three phases:
    1. Coarse sampling: Sample frames uniformly across the video
    2. Region identification: Find the region with highest motion change
    3. Binary search: Refine detection within that region

    This approach is highly efficient, sampling only ~1-2% of total frames.

    Args:
        video_path: Path to input video file
        coarse_samples: Number of initial uniform samples across video (default: 10)
        downsample_factor: Spatial downsampling factor for speed (default: 4)
        binary_search_samples_per_iteration: Samples per refinement iteration (default: 5)
        final_window_size: Stop binary search when window smaller than this (default: 10)
        verbose: Print detection progress (default: False)

    Returns:
        Detected start frame number (0-based)

    Example:
        >>> # Basic usage
        >>> start_frame = detect_start_frame("video.mp4")
        >>> print(f"Content starts at frame {start_frame}")
        >>>
        >>> # With custom parameters for more aggressive search
        >>> start_frame = detect_start_frame(
        ...     "video.mp4",
        ...     coarse_samples=15,
        ...     downsample_factor=2
        ... )

    Note:
        Based on empirical testing, this method achieves ~25 frame accuracy
        (typically <1 second error) for "hand at start" videos.
    """
    video_path = Path(video_path)

    if verbose:
        print(f"{'='*70}")
        print("AUTO START DETECTION: Motion-Based Hierarchical Search")
        print(f"{'='*70}")
        print(f"Video: {video_path.name}")
        print(f"Parameters:")
        print(f"  Coarse samples: {coarse_samples}")
        print(f"  Downsample factor: {downsample_factor}")
        print(f"  Binary search samples: {binary_search_samples_per_iteration}")
        print(f"  Final window size: {final_window_size}")

    # Phase 1: Coarse sampling
    sample_frames, motion_scores = _coarse_sampling(
        video_path, coarse_samples, downsample_factor, verbose
    )

    # Phase 2: Find transition region
    start_frame, end_frame = _find_transition_region(
        sample_frames, motion_scores, verbose
    )

    # Phase 3: Binary search refinement
    detected_frame, _ = _binary_search_transition(
        video_path,
        start_frame,
        end_frame,
        binary_search_samples_per_iteration,
        final_window_size,
        downsample_factor,
        verbose,
    )

    if verbose:
        print(f"\n{'='*70}")
        print(f"DETECTED START FRAME: {detected_frame}")
        print(f"{'='*70}")

    return detected_frame


def _get_frame_motion(
    reader: VideoReader,
    frame_num: int,
    prev_frame_num: Optional[int] = None,
    downsample: int = 4,
) -> float:
    """Calculate motion between two frames.

    Args:
        reader: VideoReader instance
        frame_num: Current frame number
        prev_frame_num: Previous frame number (if None, use frame_num-1)
        downsample: Spatial downsampling factor for speed

    Returns:
        Motion score (average pixel difference)
    """
    if prev_frame_num is None:
        prev_frame_num = max(0, frame_num - 1)

    # Read both frames
    frame1 = reader.read_frame(prev_frame_num)
    frame2 = reader.read_frame(frame_num)

    # Convert to grayscale and downsample
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    if downsample > 1:
        h, w = gray1.shape
        gray1 = cv2.resize(gray1, (w // downsample, h // downsample))
        gray2 = cv2.resize(gray2, (w // downsample, h // downsample))

    # Compute motion as mean absolute difference
    motion = np.mean(np.abs(gray1.astype(float) - gray2.astype(float)))

    return float(motion)


def _coarse_sampling(
    video_path: Path,
    n_samples: int,
    downsample: int,
    verbose: bool,
) -> tuple[np.ndarray, np.ndarray]:
    """Sample frames uniformly across video to get coarse motion profile.

    Args:
        video_path: Path to video file
        n_samples: Number of uniform samples
        downsample: Spatial downsampling factor
        verbose: Print progress

    Returns:
        Tuple of (frame_numbers, motion_scores)
    """
    if verbose:
        print(f"\n{'='*70}")
        print("PHASE 1: COARSE SAMPLING")
        print(f"{'='*70}")

    with VideoReader(str(video_path)) as reader:
        total_frames = reader.frame_count

        # Sample uniformly across video (ensure indices are valid)
        sample_indices = np.linspace(0, total_frames - 2, n_samples, dtype=int)
        sample_indices = np.unique(sample_indices)  # Remove duplicates

        if verbose:
            print(f"Total frames: {total_frames}")
            print(f"Sampling {n_samples} frames uniformly...")

        motion_scores = []

        for i in range(len(sample_indices)):
            frame_num = sample_indices[i]

            if i == 0:
                # First sample, no previous frame
                motion_scores.append(0.0)
            else:
                prev_frame = sample_indices[i - 1]
                motion = _get_frame_motion(reader, frame_num, prev_frame, downsample)
                motion_scores.append(motion)
                if verbose:
                    print(f"  Frames {prev_frame} → {frame_num}: motion = {motion:.2f}")

        return sample_indices, np.array(motion_scores)


def _find_transition_region(
    sample_frames: np.ndarray,
    motion_scores: np.ndarray,
    verbose: bool,
) -> tuple[int, int]:
    """Find the region with highest motion change.

    Args:
        sample_frames: Array of sampled frame numbers
        motion_scores: Motion scores for each sample
        verbose: Print progress

    Returns:
        Tuple of (start_frame, end_frame) defining search region
    """
    if verbose:
        print(f"\n{'='*70}")
        print("PHASE 2: IDENTIFY TRANSITION REGION")
        print(f"{'='*70}")

    # Find the sample interval with highest motion
    max_motion_idx = int(np.argmax(motion_scores))

    if verbose:
        print(f"Maximum motion at sample {max_motion_idx}: {motion_scores[max_motion_idx]:.2f}")

    # Define search region (between this sample and previous)
    if max_motion_idx > 0:
        start_frame = int(sample_frames[max_motion_idx - 1])
        end_frame = int(sample_frames[max_motion_idx])
    else:
        start_frame = 0
        end_frame = int(sample_frames[1])

    if verbose:
        print(f"Search region: frames {start_frame} to {end_frame}")
        print(f"Region size: {end_frame - start_frame} frames")

    return start_frame, end_frame


def _binary_search_transition(
    video_path: Path,
    start_frame: int,
    end_frame: int,
    samples_per_iteration: int,
    final_window_size: int,
    downsample: int,
    verbose: bool,
) -> tuple[int, list[Dict[str, Any]]]:
    """Binary search within region to find exact transition frame.

    Uses iterative refinement by sampling within progressively smaller windows.

    Args:
        video_path: Path to video file
        start_frame: Start of search region
        end_frame: End of search region
        samples_per_iteration: Number of samples per iteration
        final_window_size: Stop when window smaller than this
        downsample: Spatial downsampling factor
        verbose: Print progress

    Returns:
        Tuple of (detected_frame, search_history)
    """
    if verbose:
        print(f"\n{'='*70}")
        print("PHASE 3: BINARY SEARCH FOR EXACT FRAME")
        print(f"{'='*70}")

    current_start = start_frame
    current_end = end_frame
    iteration = 1

    search_history = []

    with VideoReader(str(video_path)) as reader:
        while (current_end - current_start) > final_window_size:
            if verbose:
                print(f"\nIteration {iteration}:")
                print(f"  Search window: {current_start} to {current_end} "
                      f"({current_end - current_start} frames)")

            # Sample within current window
            sample_frames = np.linspace(
                current_start, current_end, samples_per_iteration, dtype=int
            )

            motion_scores = []
            for i in range(len(sample_frames)):
                if i == 0:
                    motion_scores.append(0.0)
                else:
                    motion = _get_frame_motion(
                        reader, int(sample_frames[i]), int(sample_frames[i - 1]), downsample
                    )
                    motion_scores.append(motion)

            # Find max motion in this window
            max_idx = int(np.argmax(motion_scores))
            if verbose:
                print(f"  Max motion at frame {sample_frames[max_idx]}: "
                      f"{motion_scores[max_idx]:.2f}")

            # Record this iteration
            search_history.append({
                'iteration': iteration,
                'frames': sample_frames.copy(),
                'motion': np.array(motion_scores),
                'detected': int(sample_frames[max_idx])
            })

            # Narrow window around max motion
            if max_idx > 0 and max_idx < len(sample_frames) - 1:
                current_start = int(sample_frames[max_idx - 1])
                current_end = int(sample_frames[max_idx + 1])
            elif max_idx == 0:
                current_start = int(sample_frames[0])
                current_end = int(sample_frames[min(2, len(sample_frames) - 1)])
            else:
                current_start = int(sample_frames[max(-2, max_idx - 1)])
                current_end = int(sample_frames[max_idx])

            iteration += 1

        # Final detailed scan
        if verbose:
            print(f"\nFinal scan: {current_start} to {current_end}")

        final_frames = np.arange(current_start, current_end + 1)
        final_motion = []

        for i in range(len(final_frames)):
            if i == 0:
                final_motion.append(0.0)
            else:
                motion = _get_frame_motion(
                    reader, int(final_frames[i]), int(final_frames[i - 1]), downsample
                )
                final_motion.append(motion)

        final_motion_array = np.array(final_motion)
        detected_frame = int(final_frames[np.argmax(final_motion_array)])

        search_history.append({
            'iteration': iteration,
            'frames': final_frames,
            'motion': final_motion_array,
            'detected': detected_frame
        })

        if verbose:
            print(f"\nFinal detected frame: {detected_frame}")

        return detected_frame, search_history
