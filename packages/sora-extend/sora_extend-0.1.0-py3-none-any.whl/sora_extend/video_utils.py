"""Video processing utilities."""

from pathlib import Path

import cv2

try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips
except ImportError:
    # MoviePy 2.0+ uses different import structure
    try:
        from moviepy import VideoFileClip, concatenate_videoclips
    except ImportError:
        raise ImportError(
            "MoviePy is required but not properly installed. "
            "Please install it with: pip install moviepy>=2.0.0"
        )


def extract_last_frame(video_path: Path, out_image_path: Path) -> Path:
    """
    Extract the last frame from a video file.

    Args:
        video_path: Path to input video
        out_image_path: Path to save extracted frame

    Returns:
        Path to saved frame image
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open {video_path}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    success, frame = False, None

    if total > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, total - 1)
        success, frame = cap.read()
    if not success or frame is None:
        cap.release()
        cap = cv2.VideoCapture(str(video_path))
        while True:
            ret, f = cap.read()
            if not ret:
                break
            frame = f
            success = True
    cap.release()

    if not success or frame is None:
        raise RuntimeError(f"Could not read last frame from {video_path}")

    out_image_path.parent.mkdir(parents=True, exist_ok=True)
    ok = cv2.imwrite(str(out_image_path), frame)
    if not ok:
        raise RuntimeError(f"Failed to write {out_image_path}")
    return out_image_path


def concatenate_segments(segment_paths: list[Path], out_path: Path) -> Path:
    """
    Concatenate multiple video segments into one file.

    Args:
        segment_paths: List of paths to video segments
        out_path: Path for output combined video

    Returns:
        Path to combined video file
    """
    clips = [VideoFileClip(str(p)) for p in segment_paths]
    target_fps = clips[0].fps or 24
    result = concatenate_videoclips(clips, method="compose")
    result.write_videofile(
        str(out_path),
        codec="libx264",
        audio_codec="aac",
        fps=target_fps,
        preset="medium",
        threads=0,
    )
    for c in clips:
        c.close()
    return out_path
