"""Sora Extend - AI-Planned, Scene-Exact Video Generation with Continuity."""

__version__ = "0.1.2"

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

# Lazy loading map
_LAZY_IMPORTS = {
    "chain_generate_sora": ".pipeline",
    "plan_prompts_with_ai": ".planner",
    "create_video": ".sora_api",
    "download_video_content": ".sora_api",
    "poll_until_complete": ".sora_api",
    "retrieve_video": ".sora_api",
    "concatenate_segments": ".video_utils",
    "extract_last_frame": ".video_utils",
}


def __getattr__(name):
    """Lazy import attributes on first access."""
    if name in _LAZY_IMPORTS:
        from importlib import import_module

        module = import_module(_LAZY_IMPORTS[name], package=__name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
