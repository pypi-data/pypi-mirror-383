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

    if print_progress:
        from rich.console import Console
        from rich.panel import Panel
        from rich.padding import Padding
        console = Console()
    
    for i, seg in enumerate(segments, start=1):
        secs = int(seg["seconds"])
        prompt = seg["prompt"]

        if print_progress:
            console.print()  # Empty line for spacing
            console.print(Panel.fit(
                f"[bold cyan]Generating Segment {i}/{len(segments)} — {secs}s[/bold cyan]",
                border_style="cyan"
            ))

        if print_progress:
            console.print(Padding(Panel.fit(f"[bold cyan]Step 2.{i}.1:[/bold cyan] Creating video generation job", border_style="cyan"), (0, 0, 0, 4)))
        
        job = create_video(
            prompt=prompt,
            size=size,
            seconds=secs,
            model=model,
            api_key=api_key,
            input_reference=input_ref,
        )

        if print_progress:
            console.print(Padding(Panel.fit(f"[bold cyan]Step 2.{i}.2:[/bold cyan] Job started: {job['id']} | status: {job['status']}", border_style="cyan"), (0, 0, 0, 4)))
            console.print(Padding(Panel.fit(f"[bold cyan]Step 2.{i}.3:[/bold cyan] Polling for completion", border_style="cyan"), (0, 0, 0, 4)))

        completed = poll_until_complete(
            job, api_key, poll_interval=poll_interval, print_progress=print_progress
        )

        if print_progress:
            console.print(Padding(Panel.fit(f"[bold cyan]Step 2.{i}.4:[/bold cyan] Downloading video segment", border_style="cyan"), (0, 0, 0, 4)))
        
        seg_path = out_dir / f"segment_{i:02d}.mp4"
        download_video_content(completed["id"], seg_path, api_key, variant="video")

        if print_progress:
            console.print(Padding(Panel.fit(f"[bold cyan]Step 2.{i}.5:[/bold cyan] Saved to {seg_path}", border_style="cyan"), (0, 0, 0, 4)))
        segment_paths.append(seg_path)

        if print_progress:
            console.print(Padding(Panel.fit(f"[bold cyan]Step 2.{i}.6:[/bold cyan] Extracting last frame for continuity", border_style="cyan"), (0, 0, 0, 4)))
        
        # Prepare input reference (final frame) for the next segment
        frame_path = out_dir / f"segment_{i:02d}_last.jpg"
        extract_last_frame(seg_path, frame_path)

        if print_progress:
            console.print(Padding(Panel.fit(f"[bold cyan]Step 2.{i}.7:[/bold cyan] Saved reference frame → {frame_path.name}", border_style="cyan"), (0, 0, 0, 4)))
        input_ref = frame_path

    return segment_paths
