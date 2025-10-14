"""CLI for Sora Extend - AI-Planned, Scene-Exact Video Generation with Continuity."""

from pathlib import Path


def _get_typer_app():
    """Lazy load typer app."""
    import typer
    return typer.Typer(
        name="sora-extend",
        help="Generate extended Sora videos with AI-planned continuity",
        add_completion=False,
    )


app = None  # Lazy loaded on first access


def _register_commands():
    """Register CLI commands - called on first access."""
    global app
    import typer
    from openai import OpenAI
    from rich.console import Console
    from rich.panel import Panel
    
    from .pipeline import chain_generate_sora
    from .planner import plan_prompts_with_ai
    from .video_utils import concatenate_segments
    
    app = _get_typer_app()
    console = Console()

    @app.command()
    def generate(
        prompt: str = typer.Argument(..., help="Base prompt describing the video concept"),
        api_key: str = typer.Option(
            None,
            "--api-key",
            "-k",
            envvar="OPENAI_API_KEY",
            help="OpenAI API key (or set OPENAI_API_KEY env var)",
        ),
        seconds_per_segment: int = typer.Option(
            8,
            "--seconds",
            "-s",
            help="Duration of each segment in seconds (4, 8, or 12)",
        ),
        num_segments: int = typer.Option(
            2,
            "--num-segments",
            "-n",
            help="Number of segments to generate",
        ),
        sora_model: str = typer.Option(
            "sora-2",
            "--sora-model",
            help="Sora model to use (sora-2 or sora-2-pro)",
        ),
        planner_model: str = typer.Option(
            "gpt-5",
            "--planner-model",
            help="Planning model to use for generating segment prompts",
        ),
        size: str = typer.Option(
            "1280x720",
            "--size",
            help="Video size (must stay constant across segments)",
        ),
        output_dir: Path = typer.Option(
            Path("sora_ai_planned_chain"),
            "--output-dir",
            "-o",
            help="Output directory for generated videos",
        ),
        no_concatenate: bool = typer.Option(
            False,
            "--no-concatenate",
            help="Skip concatenating segments into final video",
        ),
        quiet: bool = typer.Option(
            False,
            "--quiet",
            "-q",
            help="Suppress progress output",
        ),
    ):
        """
        Generate an extended Sora video with AI-planned continuity.
        
        This tool uses an LLM to plan multiple video segments that maintain
        visual continuity, then generates them using Sora 2 with reference frames.
        
        Example:
            sora-extend generate "Gameplay footage of a futuristic racing game" \\
                --seconds 8 --num-segments 3
        """
        if not api_key:
            console.print(
                "[red]Error:[/red] OpenAI API key is required. "
                "Set OPENAI_API_KEY environment variable or use --api-key flag."
            )
            raise typer.Exit(1)

        if seconds_per_segment not in (4, 8, 12):
            console.print(
                f"[yellow]Warning:[/yellow] Unusual segment duration {seconds_per_segment}s. "
                "Recommended values are 4, 8, or 12 seconds."
            )

        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Step 1: Plan prompts with AI
            if not quiet:
                console.print(
                    Panel.fit(
                        f"[bold cyan]Step 1:[/bold cyan] Planning {num_segments} segments "
                        f"({seconds_per_segment}s each) using {planner_model}",
                        border_style="cyan",
                    )
                )

            segments = plan_prompts_with_ai(
                base_prompt=prompt,
                seconds_per_segment=seconds_per_segment,
                num_generations=num_segments,
                planner_model=planner_model,
                client=client,
                print_progress=not quiet,
            )

            if not quiet:
                console.print("\n[bold green]✓[/bold green] AI-planned segments:\n")
                for i, seg in enumerate(segments, start=1):
                    console.print(
                        f"[bold][{i:02d}][/bold] {seg['seconds']}s — "
                        f"{seg.get('title', '(untitled)')}"
                    )
                    console.print(f"[dim]{seg['prompt'][:150]}...[/dim]\n")

            # Step 2: Generate video segments with continuity
            if not quiet:
                console.print(
                    Panel.fit(
                        f"[bold cyan]Step 2:[/bold cyan] Generating {len(segments)} "
                        f"video segments with {sora_model}",
                        border_style="cyan",
                    )
                )

            segment_paths = chain_generate_sora(
                segments=segments,
                size=size,
                model=sora_model,
                api_key=api_key,
                out_dir=output_dir,
                print_progress=not quiet,
            )

            # Step 3: Concatenate segments
            if not no_concatenate:
                if not quiet:
                    console.print(
                        Panel.fit(
                            "[bold cyan]Step 3:[/bold cyan] Concatenating segments",
                            border_style="cyan",
                        )
                    )

                final_path = output_dir / "combined.mp4"
                concatenate_segments(segment_paths, final_path, print_progress=not quiet)

                if not quiet:
                    console.print(
                        f"\n[bold green]✓ Success![/bold green] "
                        f"Combined video saved to: [cyan]{final_path}[/cyan]"
                    )
                    total_duration = seconds_per_segment * num_segments
                    console.print(
                        f"[dim]Total duration: {total_duration}s "
                        f"({len(segments)} segments)[/dim]"
                    )
            else:
                if not quiet:
                    console.print(
                        f"\n[bold green]✓ Success![/bold green] "
                        f"Generated {len(segment_paths)} segments in: [cyan]{output_dir}[/cyan]"
                    )

        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {e}")
            raise typer.Exit(1)

    @app.command()
    def version():
        """Show version information."""
        console.print("sora-extend v0.1.0")


def main():
    """Entry point for the CLI."""
    global app
    if app is None:
        _register_commands()
    app()


if __name__ == "__main__":
    main()
