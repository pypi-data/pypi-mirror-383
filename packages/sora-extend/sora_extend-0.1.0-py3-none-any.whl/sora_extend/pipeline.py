"""Main video generation pipeline."""

from pathlib import Path

from .sora_api import (
    create_video,
    download_video_content,
    poll_until_complete,
)
from .video_utils import extract_last_frame


def chain_generate_sora(
    segments: list[dict],
    size: str,
    model: str,
    api_key: str,
    out_dir: Path,
    poll_interval: float = 2,
    print_progress: bool = True,
) -> list[Path]:
    """
    Generate video segments in a chain with continuity.

    Args:
        segments: List of segment dicts with 'title', 'seconds', and 'prompt'
        size: Video size (e.g., "1280x720")
        model: Sora model name
        api_key: OpenAI API key
        out_dir: Output directory for segments
        poll_interval: Seconds between status checks
        print_progress: Whether to print progress

    Returns:
        List of paths to generated video segments
    """
    input_ref = None
    segment_paths = []

    for i, seg in enumerate(segments, start=1):
        secs = int(seg["seconds"])
        prompt = seg["prompt"]

        if print_progress:
            print(f"\n=== Generating Segment {i}/{len(segments)} — {secs}s ===")

        job = create_video(
            prompt=prompt,
            size=size,
            seconds=secs,
            model=model,
            api_key=api_key,
            input_reference=input_ref,
        )

        if print_progress:
            print("Started job:", job["id"], "| status:", job["status"])

        completed = poll_until_complete(
            job, api_key, poll_interval=poll_interval, print_progress=print_progress
        )

        seg_path = out_dir / f"segment_{i:02d}.mp4"
        download_video_content(completed["id"], seg_path, api_key, variant="video")

        if print_progress:
            print("Saved", seg_path)
        segment_paths.append(seg_path)

        # Prepare input reference (final frame) for the next segment
        frame_path = out_dir / f"segment_{i:02d}_last.jpg"
        extract_last_frame(seg_path, frame_path)

        if print_progress:
            print("Extracted last frame ->", frame_path)
        input_ref = frame_path

    return segment_paths
