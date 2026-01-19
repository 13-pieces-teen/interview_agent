# Interview Agent

AI-powered interview experience processor that transforms unstructured interview content into organized, tagged knowledge base.

## Features

- **Multi-modal input support** - Process text and images
- **Web Interface** - Modern React UI with drag & drop
- **REST API** - FastAPI backend with automatic docs
- **Automatic extraction** - Structured interview details
- **Intelligent tagging** - AI-powered classification
- **Answer generation** - AI generates missing answers
- **Export formats** - JSON and Markdown

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd interview_agent

# Install backend dependencies
uv sync

# Install frontend dependencies
cd frontend
npm install
cd ..
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

### 3. Run the Application

#### Web Interface (Recommended)

**Windows:**
```bash
start_dev.bat
```

**Linux/Mac:**
```bash
chmod +x start_dev.sh
./start_dev.sh
```

This will start both:
- Backend API at `http://localhost:8000`
- Frontend UI at `http://localhost:5173`

#### CLI Mode

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the CLI agent
python src/main.py
```

#### API Only

```bash
source .venv/bin/activate
python -m uvicorn src.api.app:app --reload --port 8000

# Access API docs at http://localhost:8000/docs
```

## Project Structure

```
interview_agent/
├── src/
│   ├── api/             # FastAPI web server
│   ├── agents/          # Core processor agent
│   ├── handlers/        # Input handlers (text, image)
│   ├── exporters/       # Export functionality (JSON, Markdown)
│   ├── models/          # Data models (Pydantic schemas)
│   ├── prompts/         # LLM prompts
│   ├── utils/           # Utilities (config, LLM client)
│   └── main.py          # CLI entry point
├── frontend/            # React + TypeScript web UI
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API client
│   │   └── types/       # TypeScript types
│   └── package.json
├── tests/               # Unit tests
├── output/              # Generated output files
├── data/                # Data storage
├── start_dev.bat        # Windows dev script
├── start_dev.sh         # Linux/Mac dev script
├── .env.example         # Example environment variables
├── pyproject.toml       # Python dependencies
└── README.md            # This file
```

## Usage

### Web Interface

1. Open `http://localhost:5173` in your browser
2. Choose between text input or image upload
3. Optionally enable AI answer generation
4. Submit your interview experience
5. View structured results and download exports

### CLI Mode

Run `python src/main.py` and follow the prompts:

1. Paste text content or provide an image path
2. Choose whether to generate missing answers
3. View the processed results

### API Endpoints

The REST API provides the following endpoints:

- `GET /` - Health check
- `POST /api/process/text` - Process text content
- `POST /api/process/image` - Process image file
- `GET /api/files` - List output files
- `GET /api/download/{filename}` - Download file
- `GET /docs` - Interactive API documentation

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

The system follows a modern full-stack architecture:

### Backend (Python)
1. **Input Handler** - Detects input type and performs OCR if needed
2. **Core Processor Agent** - Single agent using DeepSeek-V3.2:
   - Structured extraction
   - Content cleaning
   - Tag classification
   - Answer enhancement
3. **Exporter** - Saves results to JSON and/or Markdown
4. **FastAPI Server** - REST API with automatic documentation

### Frontend (React)
1. **Upload Zone** - Drag & drop interface for text/images
2. **Results View** - Structured display of interview data
3. **Export Panel** - Download processed files
4. **API Client** - Axios-based HTTP client with TypeScript types

## Technology Stack

### Backend
- **Python 3.10+** - Core language
- **FastAPI** - Modern async web framework
- **Pydantic** - Data validation
- **LangChain** - LLM orchestration
- **DeepSeek-V3.2** - Text processing
- **GLM-4.6V** - Image OCR

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Dropzone** - File uploads
- **Lucide React** - Icons

## Development

### Backend Development

```bash
# Run tests
uv run pytest

# Code formatting
uv run black src/
uv run ruff check src/

# Start API server with reload
python -m uvicorn src.api.app:app --reload
```

### Frontend Development

```bash
cd frontend

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Full Stack Development

Use the provided development scripts to run both backend and frontend simultaneously:

**Windows:** `start_dev.bat`
**Linux/Mac:** `./start_dev.sh`

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
