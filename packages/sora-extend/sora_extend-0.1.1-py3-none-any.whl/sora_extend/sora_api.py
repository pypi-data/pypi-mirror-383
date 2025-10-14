"""Sora API interaction functions."""

import mimetypes
import time
from pathlib import Path

import requests

from .constants import API_BASE, DEFAULT_POLL_INTERVAL_SEC


def guess_mime(path: Path) -> str:
    """Guess MIME type from file path."""
    t = mimetypes.guess_type(str(path))[0]
    return t or "application/octet-stream"


def _dump_error(resp: requests.Response) -> str:
    """Format error response for logging."""
    rid = resp.headers.get("x-request-id", "<none>")
    try:
        body = resp.json()
    except Exception:
        body = resp.text
    return f"HTTP {resp.status_code} (request-id: {rid})\n{body}"


def create_video(
    prompt: str,
    size: str,
    seconds: int,
    model: str,
    api_key: str,
    input_reference: Path | None = None,
) -> dict:
    """
    Create a video generation job with Sora API.

    Args:
        prompt: Video generation prompt
        size: Video size (e.g., "1280x720")
        seconds: Duration in seconds
        model: Sora model name
        api_key: OpenAI API key
        input_reference: Optional reference image for continuity

    Returns:
        API response dict with job details
    """
    headers = {"Authorization": f"Bearer {api_key}"}

    files = {
        "model": (None, model),
        "prompt": (None, prompt),
        "seconds": (None, str(seconds)),
    }
    if size:
        files["size"] = (None, size)

    if input_reference is not None:
        mime = guess_mime(input_reference)
        files["input_reference"] = (
            Path(input_reference).name,
            open(input_reference, "rb"),
            mime,
        )

    r = requests.post(f"{API_BASE}/videos", headers=headers, files=files, timeout=300)
    if r.status_code >= 400:
        raise RuntimeError("Create video failed:\n" + _dump_error(r))
    return r.json()


def retrieve_video(video_id: str, api_key: str) -> dict:
    """
    Retrieve video generation job status.

    Args:
        video_id: Video job ID
        api_key: OpenAI API key

    Returns:
        API response dict with job status
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    r = requests.get(f"{API_BASE}/videos/{video_id}", headers=headers, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError("Retrieve video failed:\n" + _dump_error(r))
    return r.json()


def download_video_content(
    video_id: str, out_path: Path, api_key: str, variant: str = "video"
) -> Path:
    """
    Download completed video content.

    Args:
        video_id: Video job ID
        out_path: Output path for video file
        api_key: OpenAI API key
        variant: Content variant to download

    Returns:
        Path to downloaded video file
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    with requests.get(
        f"{API_BASE}/videos/{video_id}/content",
        headers=headers,
        params={"variant": variant},
        stream=True,
        timeout=600,
    ) as r:
        if r.status_code >= 400:
            raise RuntimeError("Download failed:\n" + _dump_error(r))
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return out_path


def poll_until_complete(
    job: dict,
    api_key: str,
    poll_interval: float = DEFAULT_POLL_INTERVAL_SEC,
    print_progress: bool = True,
) -> dict:
    """
    Poll video generation job until completion.

    Args:
        job: Initial job response dict
        api_key: OpenAI API key
        poll_interval: Seconds between status checks
        print_progress: Whether to print progress bar

    Returns:
        Completed job response dict
    """
    video = job
    vid = video["id"]

    def bar(pct: float, width: int = 30) -> str:
        filled = int(max(0.0, min(100.0, pct)) / 100 * width)
        return "=" * filled + "-" * (width - filled)

    while video.get("status") in ("queued", "in_progress"):
        if print_progress:
            pct = float(video.get("progress", 0) or 0)
            status_text = "Queued" if video["status"] == "queued" else "Processing"
            print(f"\r{status_text}: [{bar(pct)}] {pct:5.1f}%", end="")
        time.sleep(poll_interval)
        video = retrieve_video(vid, api_key)

    if print_progress:
        print()

    if video.get("status") != "completed":
        msg = (video.get("error") or {}).get("message", f"Job {vid} failed")
        raise RuntimeError(msg)
    return video
