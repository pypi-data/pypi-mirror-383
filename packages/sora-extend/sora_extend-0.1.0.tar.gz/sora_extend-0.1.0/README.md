# Sora Extend

**AI-Planned, Scene-Exact Video Generation with Continuity using Sora 2**

Built by [Matt Shumer](https://x.com/mattshumer_). CLI package conversion by Mason Hall.

## Overview

Sora Extend enables you to generate extended videos (>12s) using Sora 2 by:

1. **AI Planning**: Using an LLM (e.g., GPT-5) to intelligently plan N scene prompts from a base idea, optimized for continuity
2. **Chained Generation**: Rendering each segment with Sora 2, passing the prior segment's final frame as `input_reference` for seamless transitions
3. **Automatic Concatenation**: Combining all segments into a single MP4

This approach allows you to create videos much longer than Sora's standard 12-second limit while maintaining visual continuity across segments.

## Installation

### Using pip

```bash
pip install -e .
```

### Using uv (recommended)

```bash
uv pip install -e .
```

## Prerequisites

- Python 3.12 or higher
- OpenAI API key with access to:
  - Sora 2 (video generation)
  - A reasoning model for planning (e.g., GPT-5, or fallback to gpt-4)

## Usage

### Basic Command

```bash
sora-extend generate "Your video description here"
```

### Full Example

```bash
export OPENAI_API_KEY="your-api-key-here"

sora-extend generate \
  "Gameplay footage of a game releasing in 2027, a car driving through a futuristic city" \
  --seconds 8 \
  --num-segments 3 \
  --output-dir ./my_video
```

This will create a 24-second video (3 segments × 8 seconds each).

### Command-Line Options

```
sora-extend generate PROMPT [OPTIONS]

Arguments:
  PROMPT  Base prompt describing the video concept [required]

Options:
  -k, --api-key TEXT           OpenAI API key (or set OPENAI_API_KEY env var)
  -s, --seconds INTEGER        Duration of each segment in seconds (4, 8, or 12) [default: 8]
  -n, --num-segments INTEGER   Number of segments to generate [default: 2]
  --sora-model TEXT           Sora model to use (sora-2 or sora-2-pro) [default: sora-2]
  --planner-model TEXT        Planning model for generating prompts [default: gpt-5]
  --size TEXT                 Video size (must stay constant) [default: 1280x720]
  -o, --output-dir PATH       Output directory for generated videos [default: sora_ai_planned_chain]
  --no-concatenate            Skip concatenating segments into final video
  -q, --quiet                 Suppress progress output
  --help                      Show this message and exit
```

### Examples

**Create a 16-second video (2 × 8s segments):**
```bash
sora-extend generate "A drone flying over a cyberpunk city at night"
```

**Create a 48-second video using 12-second segments:**
```bash
sora-extend generate "A nature documentary about arctic foxes" \
  --seconds 12 \
  --num-segments 4
```

**Generate segments without concatenating:**
```bash
sora-extend generate "Product showcase for a new smartphone" \
  --seconds 8 \
  --num-segments 3 \
  --no-concatenate
```

**Use Sora 2 Pro model:**
```bash
sora-extend generate "High-quality cinematic scene" \
  --sora-model sora-2-pro \
  --seconds 12 \
  --num-segments 2
```

## How It Works

### 1. AI Planning Phase

The planner model (default: GPT-5) receives your base prompt and generates detailed, scene-specific prompts for each segment. These prompts include:

- **Context sections**: Guidance for the AI about what came before
- **Continuity instructions**: Explicit directions to start from the previous segment's final frame
- **Visual consistency**: Maintained lighting, style, and subject identity across segments

### 2. Chained Video Generation

For each segment:
1. Generate video using Sora 2 with the planned prompt
2. Extract the final frame from the generated video
3. Use that frame as the `input_reference` for the next segment

This creates smooth transitions between segments.

### 3. Concatenation

All segments are concatenated into a single MP4 file using MoviePy, preserving the framerate and quality.

## Output Structure

```
sora_ai_planned_chain/
├── segment_01.mp4        # First video segment
├── segment_01_last.jpg   # Last frame of first segment
├── segment_02.mp4        # Second video segment
├── segment_02_last.jpg   # Last frame of second segment
├── ...
└── combined.mp4          # Final concatenated video
```

## API Usage

You can also use Sora Extend as a Python library:

```python
from openai import OpenAI
from pathlib import Path
from sora_extend import plan_prompts_with_ai, chain_generate_sora, concatenate_segments

client = OpenAI(api_key="your-api-key")
output_dir = Path("./output")
output_dir.mkdir(exist_ok=True)

# Plan segments
segments = plan_prompts_with_ai(
    base_prompt="A journey through space",
    seconds_per_segment=8,
    num_generations=3,
    planner_model="gpt-5",
    client=client,
)

# Generate videos
segment_paths = chain_generate_sora(
    segments=segments,
    size="1280x720",
    model="sora-2",
    api_key="your-api-key",
    out_dir=output_dir,
)

# Concatenate
final_video = concatenate_segments(segment_paths, output_dir / "final.mp4")
print(f"Video saved to: {final_video}")
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Supported Video Sizes

- `1280x720` (default)
- `1920x1080`
- `1080x1920` (vertical)
- Other sizes supported by Sora 2

### Segment Durations

Recommended values: 4, 8, or 12 seconds

The total video duration will be: `seconds_per_segment × num_segments`

## Tips for Best Results

1. **Clear Base Prompts**: Be specific about the setting, style, and mood
2. **Consistent Style**: Mention visual style in your base prompt (e.g., "cinematic", "documentary style")
3. **Subject Continuity**: If featuring a character/object, describe them clearly
4. **Reasonable Segment Count**: Start with 2-3 segments to test, then scale up
5. **Check Planner Output**: Review the AI-planned prompts before generation (use `--quiet` to see them)

## Troubleshooting

**"Planner returned no text"**
- Try a different planner model: `--planner-model gpt-4o`

**"Create video failed"**
- Check your API key has Sora 2 access
- Verify your prompt doesn't violate content policies

**Discontinuities between segments**
- Try shorter segments (e.g., 4s instead of 12s)
- Make your base prompt more specific about visual style

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is based on the original Jupyter notebook by Matt Shumer.

## Credits

- Original concept and notebook: [Matt Shumer](https://x.com/mattshumer_)
- CLI package conversion: Mason Hall


