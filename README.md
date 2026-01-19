# Interview Agent

AI-powered interview experience processor that transforms unstructured interview content into organized, tagged knowledge base.

## Features

- Multi-modal input support (text, images)
- Automatic structured extraction of interview details
- Intelligent tagging and classification
- Answer generation for questions without responses
- Export to JSON and Markdown formats

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd interview_agent

# Install dependencies using uv
uv sync
```

### 2. Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your SiliconFlow API key:

```
SILICONFLOW_API_KEY=your_actual_api_key_here
```

### 3. Run

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the agent
python src/main.py
```

## Project Structure

```
interview_agent/
├── src/
│   ├── agents/          # Core processor agent
│   ├── handlers/        # Input handlers (text, image)
│   ├── exporters/       # Export functionality (JSON, Markdown)
│   ├── models/          # Data models (Pydantic schemas)
│   ├── prompts/         # LLM prompts
│   ├── utils/           # Utilities (config, LLM client)
│   └── main.py          # Main entry point
├── tests/               # Unit tests
├── output/              # Generated output files
├── data/                # Data storage
├── .env.example         # Example environment variables
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

## Usage

### Interactive Mode

Run `python src/main.py` and follow the prompts:

1. Paste text content or provide an image path
2. Choose whether to generate missing answers
3. View the processed results

### Programmatic Usage

```python
from src.main import InterviewAgent
from src.utils.config import Config

# Load configuration
config = Config.from_env()

# Initialize agent
agent = InterviewAgent(config)

# Process interview experience
result = agent.process(
    input_data="<your interview text or image path>",
    generate_answers=False,
    export_format="both",  # "json", "markdown", or "both"
)

if result.success:
    print(f"Processed successfully in {result.processing_time:.2f}s")
    print(f"Extracted {len(result.experience.questions)} questions")
else:
    print(f"Error: {result.error}")
```

## Configuration

Environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `SILICONFLOW_API_KEY` | SiliconFlow API key | (required) |
| `SILICONFLOW_API_BASE` | API base URL | `https://api.siliconflow.cn/v1` |
| `DEEPSEEK_MODEL` | Model for text processing | `Pro/deepseek-ai/DeepSeek-V3.2` |
| `GLM_VISION_MODEL` | Model for image OCR | `zai-org/GLM-4.6V` |
| `OUTPUT_DIR` | Output directory | `output` |
| `DATA_DIR` | Data directory | `data` |

## Architecture

The system follows a simplified 3-step workflow:

1. **Input Handler** - Detects input type and performs OCR if needed
2. **Core Processor Agent** - Single agent that performs all processing using DeepSeek-V3.2:
   - Structured extraction
   - Content cleaning
   - Tag classification
   - Answer enhancement
3. **Exporter** - Saves results to JSON and/or Markdown

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black src/
uv run ruff check src/
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
