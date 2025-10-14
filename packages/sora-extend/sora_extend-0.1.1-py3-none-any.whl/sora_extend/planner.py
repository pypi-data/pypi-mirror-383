"""AI-powered video segment planning."""

import json
import re
from typing import TYPE_CHECKING

from .constants import PLANNER_SYSTEM_INSTRUCTIONS

if TYPE_CHECKING:
    from openai import OpenAI


def plan_prompts_with_ai(
    base_prompt: str,
    seconds_per_segment: int,
    num_generations: int,
    planner_model: str,
    client: "OpenAI",
    print_progress: bool = True,
) -> list[dict]:
    """
    Use an LLM to plan video segment prompts with continuity.

    Args:
        base_prompt: High-level description of the video concept
        seconds_per_segment: Duration of each segment in seconds
        num_generations: Number of segments to generate
        planner_model: Name of the planning model to use
        client: Configured OpenAI client
        print_progress: Whether to print progress updates

    Returns:
        List of segment dicts with 'title', 'seconds', and 'prompt' keys
    """
    if print_progress:
        from rich.console import Console
        from rich.panel import Panel
        from rich.padding import Padding
        console = Console()
        console.print(Padding(Panel.fit("[bold cyan]Step 1.1:[/bold cyan] Preparing planning request", border_style="cyan"), (0, 0, 0, 4)))
    
    user_input = f"""
BASE PROMPT: {base_prompt}

GENERATION LENGTH (seconds): {seconds_per_segment}
TOTAL GENERATIONS: {num_generations}

Return exactly {num_generations} segments.
""".strip()

    if print_progress:
        console.print(Padding(Panel.fit(f"[bold cyan]Step 1.2:[/bold cyan] Calling {planner_model} for segment planning", border_style="cyan"), (0, 0, 0, 4)))
    
    # Call the Responses API
    resp = client.responses.create(
        model=planner_model,
        instructions=PLANNER_SYSTEM_INSTRUCTIONS,
        input=user_input,
    )

    if print_progress:
        console.print(Padding(Panel.fit("[bold cyan]Step 1.3:[/bold cyan] Parsing AI response", border_style="cyan"), (0, 0, 0, 4)))
    
    text = getattr(resp, "output_text", None) or ""
    if not text:
        # Fallback: collect from structured blocks if needed
        try:
            text = json.dumps(resp.to_dict())
        except Exception:
            raise RuntimeError("Planner returned no text; try changing PLANNER_MODEL.")

    # Extract the first JSON object found in the response text
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError(
            "Planner did not return JSON. Inspect response and adjust instructions."
        )
    data = json.loads(m.group(0))

    if print_progress:
        console.print(Padding(Panel.fit("[bold cyan]Step 1.4:[/bold cyan] Validating and formatting segments", border_style="cyan"), (0, 0, 0, 4)))
    
    # Basic validation and enforcement
    segments = data.get("segments", [])
    if len(segments) != num_generations:
        segments = segments[:num_generations]

    # Force durations to the requested number
    for seg in segments:
        seg["seconds"] = int(seconds_per_segment)

    return segments
