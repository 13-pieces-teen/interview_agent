# Interview Agent

🎯 **AI-Powered Interview Experience Management System**

Transform unstructured interview content (text or images) into organized, searchable knowledge with intelligent tagging, answer generation, and multi-format export capabilities.

## 🌟 Key Features

### Core Capabilities
- 📝 **Multi-modal Input** - Process text and images with advanced OCR
- 🤖 **AI-Powered Processing** - Automatic extraction, tagging, and answer generation
- 💾 **Persistent Storage** - SQLite database with full CRUD operations
- 🔄 **Async Processing** - Background task queue for large-scale operations
- 📦 **Batch Processing** - Process multiple files with progress tracking
- 🔍 **Smart Search** - Filter by company, tags, dates, and more

### Export Options
- 📄 **JSON** - Structured data export
- 📝 **Markdown** - Two modes (by interview or by question)
- 📊 **Excel** - Spreadsheet format with filtering

### Web Interface
- 🎨 **Modern React UI** - Clean, responsive design with dark mode
- 📤 **Drag & Drop** - Easy file upload and batch processing
- 📊 **Gallery View** - Browse and manage saved experiences
- ✏️ **In-place Editing** - Edit experiences directly in the UI
- 📈 **Real-time Progress** - Task queue monitoring and status tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- uv
- Node.js 18+
- SiliconFlow API key ([Get one here](https://cloud.siliconflow.cn/i/AlhX2oWk))

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

**Required Configuration:**

```env
# SiliconFlow API (Required)
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
```

**Optional Configuration:**

```env
# API Settings (defaults shown)
SILICONFLOW_API_BASE=https://api.siliconflow.cn/v1
DEEPSEEK_MODEL=Pro/deepseek-ai/DeepSeek-V3.2
GLM_VISION_MODEL=zai-org/GLM-4.6V

# Storage Directories
OUTPUT_DIR=output
DATA_DIR=data


### 3. Run the Application

#### 🎯 Web Interface (Recommended)

**Windows:**
```bash
start_dev.bat
```

**Linux/Mac:**
```bash
chmod +x start_dev.sh
./start_dev.sh
```

This starts:
- 🔧 Backend API: http://localhost:8000
- 🎨 Frontend UI: http://localhost:5173

#### 🖥️ CLI Mode

```bash
# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Run the CLI agent
python src/main.py
```

#### 🔌 API Only

```bash
source .venv/bin/activate
python -m uvicorn src.api.app:app --reload --port 8000

# Access interactive API docs at http://localhost:8000/docs
```

## 📖 Usage Guide

### Web Interface Workflow

1. **Process Interview Content**
   - Navigate to http://localhost:5173
   - Choose text input or drag & drop images
   - Optionally enable AI answer generation
   - Submit and view real-time results

2. **Manage Experiences**
   - Visit the Gallery page to view all saved interviews
   - Filter by company, tags, or date range
   - Edit or delete experiences inline
   - View grouped questions across multiple interviews

3. **Export Data**
   - Use the Export modal to choose format and filters
   - Download JSON, Markdown, or Excel files
   - Batch export with automatic indexing

### CLI Workflow

```bash
python src/main.py
```

Follow the interactive prompts:
1. Paste text or provide image path
2. Choose whether to generate AI answers
3. View processed results in terminal

### API Usage

#### Process Text
```bash
curl -X POST "http://localhost:8000/api/process/text" \
  -H "Content-Type: application/json" \
  -d '{"content": "your interview text here", "generate_answers": false}'
```

#### Process Image
```bash
curl -X POST "http://localhost:8000/api/process/image" \
  -F "file=@interview_screenshot.png" \
  -F "generate_answers=false"
```

#### List Experiences
```bash
curl "http://localhost:8000/api/experiences?company=Google&limit=10"
```


### Programmatic Usage

```python
from src.main import InterviewAgent
from src.utils.config import Config

# Initialize
config = Config.from_env()
agent = InterviewAgent(config)

# Process interview
result = agent.process(
    input_data="Your interview experience text...",
    generate_answers=True,
    export_format="both"
)

if result.success:
    print(f"✅ Processed in {result.processing_time:.2f}s")
    print(f"📝 {len(result.experience.questions)} questions extracted")
    print(f"🏢 Company: {result.experience.company_name}")
else:
    print(f"❌ Error: {result.error}")
```

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌──────────┬──────────────┬──────────────┬──────────────┐  │
│  │   Home   │   Gallery    │   Detail     │   Export     │  │
│  │   Page   │    Page      │    Page      │    Modal     │  │
│  └──────────┴──────────────┴──────────────┴──────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API
┌──────────────────────────┴──────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Layer (70+ endpoints)                           │   │
│  │  • Processing (sync/async)  • CRUD operations        │   │
│  │  • Batch tasks              • Export services        │   │
│  │  • Answer generation        • Configuration          │   │
│  └─────┬─────────────┬────────────────┬──────────────┬──┘   │
│        │             │                │              │       │
│  ┌─────▼──┐    ┌────▼─────┐    ┌─────▼─────┐  ┌────▼────┐ │
│  │ Input  │    │   Core   │    │  Answer   │  │ Export  │ │
│  │Handler │    │Processor │    │Generator  │  │Services │ │
│  └────────┘    └──────────┘    └───────────┘  └─────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Infrastructure Layer                                │   │
│  │  • Database (SQLite)      • Task Queue (Async)       │   │
│  │  • LLM Client             • Batch Processor          │   │
│  │  • Feishu Exporter        • Configuration Manager    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Processing Pipeline

```
Input (Text/Image)
    │
    ├─ Image? → OCR (GLM-4.6V) → Extract Text
    │
    ▼
DeepSeek-V3.2 Agent
    ├─ Extract structured data (company, position, questions)
    ├─ Clean and normalize content
    ├─ Generate intelligent tags
    └─ Optional: Generate missing answers
    │
    ▼
Save to Database
    │
    ▼
Export Options
    ├─ JSON (structured data)
    ├─ Markdown (interview/question grouped)
    ├─ Excel (spreadsheet)
    └─ Feishu (cloud documents)
```

## 📂 Project Structure

```
interview_agent/
├── src/                          # Backend source code
│   ├── api/
│   │   └── app.py               # FastAPI application (70+ endpoints)
│   ├── agents/
│   │   ├── core_processor.py    # Main extraction agent
│   │   └── answer_generator.py  # Answer generation agent
│   ├── exporters/
│   │   ├── exporter.py          # JSON/Markdown exporter
│   │   └── feishu_exporter.py   # Feishu cloud exporter
│   ├── handlers/
│   │   └── input_handler.py     # Text/Image input handler
│   ├── models/
│   │   └── schema.py            # Pydantic data models
│   ├── prompts/
│   │   └── prompts.py           # LLM prompts
│   ├── services/
│   │   └── export_service.py    # Export orchestration
│   ├── utils/
│   │   ├── async_task_queue.py  # Async task queue system
│   │   ├── batch_processor.py   # Batch processing engine
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # SQLite database layer
│   │   └── llm_client.py        # SiliconFlow API client
│   └── main.py                  # CLI entry point
│
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.tsx              # Main processing UI
│   │   │   ├── GalleryPage.tsx           # Experience gallery
│   │   │   └── ExperienceDetailPage.tsx  # Detail viewer
│   │   ├── components/
│   │   │   ├── UploadZone.tsx            # File upload
│   │   │   ├── ResultsView.tsx           # Results display
│   │   │   ├── ExportModal.tsx           # Export dialog
│   │   │   ├── ApiKeyConfig.tsx          # API configuration
│   │   │   ├── TaskQueue.tsx             # Task monitoring
│   │   │   └── QuestionGroupView.tsx     # Question grouping
│   │   ├── services/
│   │   │   └── api.ts                    # API client
│   │   ├── types/                        # TypeScript types
│   │   └── App.tsx                       # Main app + routing
│   └── package.json
│
├── tests/                        # Unit tests
│   ├── test_feishu_export.py
│   └── ...
│
├── docs/                         # Documentation
│   ├── FEISHU_EXPORT.md         # Feishu setup guide
│   ├── FEISHU_QUICKSTART.md     # Quick start guide
│   └── ...
│
├── data/                         # SQLite database
│   └── interviews.db
│
├── output/                       # Generated exports
│
├── .env.example                  # Environment template
├── pyproject.toml               # Python dependencies
├── start_dev.bat                # Windows dev script
├── start_dev.sh                 # Linux/Mac dev script
└── README.md                    # This file
```

## 🔌 API Endpoints

### Processing (8 endpoints)
- `POST /api/process/text` - Process text content (sync)
- `POST /api/process/image` - Process single image (sync)
- `POST /api/process/images` - Process multiple images (sync)
- `POST /api/process/text/async` - Process text (async)
- `POST /api/process/images/async` - Process images (async)
- `POST /api/validate` - Validate content quality
- `POST /api/process/batch` - Create batch processing task
- `GET /api/batch/{task_id}` - Get batch task status

### Database CRUD (10 endpoints)
- `GET /api/experiences` - List with filters & pagination
- `GET /api/experiences/{id}` - Get specific experience
- `PUT /api/experiences/{id}` - Update experience
- `DELETE /api/experiences/{id}` - Delete experience
- `GET /api/tags` - Get all unique tags
- `GET /api/companies` - Get all companies
- `GET /api/stats` - Database statistics
- `GET /api/questions/grouped` - Group identical questions

### Export (6 endpoints)
- `POST /api/export` - Export to Markdown
- `POST /api/export/excel` - Export to Excel
- `POST /api/export/feishu` - Batch export to Feishu
- `POST /api/experiences/{id}/export/feishu` - Single to Feishu
- `GET /api/feishu/status` - Check Feishu connection
- `GET /api/download/{filename}` - Download file

### Answer Generation (3 endpoints)
- `POST /api/experiences/{id}/generate-answers` - Start generation
- `GET /api/tasks/answer-generation/{task_id}` - Get status
- `GET /api/tasks/answer-generation` - List all tasks

### Task Queue (3 endpoints)
- `GET /api/tasks/async` - List async tasks
- `GET /api/tasks/async/{task_id}` - Get task status
- `GET /api/tasks/queue/info` - Queue statistics

### Configuration (2 endpoints)
- `GET /api/config` - Get API configuration (masked)
- `PUT /api/config` - Update API configuration

### Utility (2 endpoints)
- `GET /` - Health check
- `GET /health` - Health check

📚 **Full API Documentation**: http://localhost:8000/docs (when running)

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Core language |
| **FastAPI** | Modern async web framework |
| **Pydantic** | Data validation and serialization |
| **SQLite** | Persistent data storage |
| **LangChain** | LLM orchestration framework |
| **DeepSeek-V3.2** | Text processing and extraction |
| **GLM-4.6V** | Image OCR and vision |
| **OpenPyXL** | Excel file generation |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI library |
| **TypeScript** | Type-safe JavaScript |
| **Vite** | Fast build tool |
| **Tailwind CSS** | Utility-first CSS framework |
| **React Router** | Client-side routing |
| **Axios** | HTTP client |
| **React Dropzone** | File upload component |
| **Lucide React** | Icon library |

## 📊 Database Schema

### Experiences Table
```sql
CREATE TABLE experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT,
    company_scale TEXT,
    interview_stage TEXT,
    questions TEXT,              -- JSON array
    tags TEXT,                   -- JSON array
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_company ON experiences(company_name);
CREATE INDEX idx_scale ON experiences(company_scale);
CREATE INDEX idx_created ON experiences(created_at);
```

## 🎯 Advanced Features

### 1. Async Processing
Process large batches in the background without blocking:
```python
# Start async task
response = requests.post('/api/process/text/async', json={
    'content': large_text,
    'generate_answers': True
})
task_id = response.json()['task_id']

# Check status
status = requests.get(f'/api/tasks/async/{task_id}')
```

### 2. Batch Processing
Process multiple files sequentially with progress tracking:
```python
files = ['interview1.png', 'interview2.png', 'interview3.png']
response = requests.post('/api/process/batch', files=files)
batch_id = response.json()['task_id']

# Monitor progress
progress = requests.get(f'/api/batch/{batch_id}')
print(f"Progress: {progress.json()['current']}/{progress.json()['total']}")
```

### 3. Question Grouping
Find recurring interview questions:
```python
# Get grouped questions
grouped = requests.get('/api/questions/grouped', params={
    'company': 'Google',
    'min_occurrences': 2
})

for group in grouped.json()['groups']:
    print(f"Question: {group['question_text']}")
    print(f"Asked {group['occurrence_count']} times")
```

### 4. Smart Filtering
Filter experiences with complex queries:
```python
experiences = requests.get('/api/experiences', params={
    'company': 'Google',
    'scale': '大型企业',
    'stage': '技术一面',
    'tags': '算法,系统设计',
    'start_date': '2025-01-01',
    'limit': 20
})
```

### 5. Feishu Integration
Export to cloud with one click:
```python
# Check Feishu connection
status = requests.get('/api/feishu/status')

# Export all experiences
result = requests.post('/api/export/feishu', json={
    'folder_token': 'your_folder_token',
    'create_index': True
})
```

## 🔧 Development

### Backend Development

```bash
# Run tests
uv run pytest

# Code formatting
uv run black src/
uv run ruff check src/

# Start API with auto-reload
python -m uvicorn src.api.app:app --reload --port 8000

# Run specific test
uv run pytest tests/test_feishu_export.py -v
```

### Frontend Development

```bash
cd frontend

# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Type check
npm run type-check
```

### Full Stack Development

Run both backend and frontend simultaneously:

**Windows:**
```bash
start_dev.bat
```

**Linux/Mac:**
```bash
./start_dev.sh
```

## 🐛 Troubleshooting

### Common Issues

**1. API Key Error**
```
Error: SILICONFLOW_API_KEY not found
```
Solution: Add your API key to `.env` file

**2. Database Locked**
```
Error: database is locked
```
Solution: Close other connections or restart the backend

**3. Feishu Export Failed**
```
Error: Feishu credentials not configured
```
Solution: Add `FEISHU_APP_ID` and `FEISHU_APP_SECRET` to `.env`

**4. Frontend Build Errors**
```
Error: Cannot find module 'vite'
```
Solution: Run `npm install` in the `frontend/` directory

## 📝 Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SILICONFLOW_API_KEY` | ✅ Yes | - | SiliconFlow API authentication |
| `SILICONFLOW_API_BASE` | ❌ No | `https://api.siliconflow.cn/v1` | API base URL |
| `DEEPSEEK_MODEL` | ❌ No | `Pro/deepseek-ai/DeepSeek-V3.2` | Text processing model |
| `GLM_VISION_MODEL` | ❌ No | `zai-org/GLM-4.6V` | Image OCR model |
| `OUTPUT_DIR` | ❌ No | `output` | Export output directory |
| `DATA_DIR` | ❌ No | `data` | Database directory |
| `FEISHU_APP_ID` | ❌ No | - | Feishu app ID (for export) |
| `FEISHU_APP_SECRET` | ❌ No | - | Feishu app secret (for export) |
| `FEISHU_API_BASE` | ❌ No | `https://open.feishu.cn/open-apis` | Feishu API base URL |

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Write tests for new features
- Update documentation as needed

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **DeepSeek** - For the powerful V3.2 language model
- **SiliconFlow** - For providing LLM API infrastructure
- **Feishu (Lark)** - For document collaboration platform
- **FastAPI** - For the amazing web framework
- **React** - For the excellent UI library

## 📞 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)

---

**Built with ❤️ using AI-powered technology**
