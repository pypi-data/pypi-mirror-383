"""Sora Extend - AI-Planned, Scene-Exact Video Generation with Continuity."""

from .pipeline import chain_generate_sora
from .planner import plan_prompts_with_ai
from .sora_api import (
    create_video,
    download_video_content,
    poll_until_complete,
    retrieve_video,
)
from .video_utils import concatenate_segments, extract_last_frame

__version__ = "0.1.0"

__all__ = [
    "chain_generate_sora",
    "concatenate_segments",
    "create_video",
    "download_video_content",
    "extract_last_frame",
    "plan_prompts_with_ai",
    "poll_until_complete",
    "retrieve_video",
]
