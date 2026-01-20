# Interview Agent - Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   React Frontend                          │ │
│  │                 (http://localhost:5173)                   │ │
│  │                                                           │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐ │ │
│  │  │ Upload Zone │  │ Results View │  │  Export Panel   │ │ │
│  │  │             │  │              │  │                 │ │ │
│  │  │ • Text      │  │ • Company    │  │ • JSON Download │ │ │
│  │  │ • Image     │  │ • Questions  │  │ • MD Download   │ │ │
│  │  │ • Drag&Drop │  │ • Tags       │  │                 │ │ │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│                      FastAPI Backend                              │
│                   (http://localhost:8000)                         │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   API Endpoints                             │ │
│  │                                                             │ │
│  │  POST /api/process/text    - Process text content          │ │
│  │  POST /api/process/image   - Process image files           │ │
│  │  GET  /api/files           - List output files             │ │
│  │  GET  /api/download/:file  - Download results              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Interview Agent Core                        │ │
│  │                                                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │ │
│  │  │   Input      │  │     Core     │  │    Exporters     │ │ │
│  │  │   Handler    │─▶│   Processor  │─▶│                  │ │ │
│  │  │              │  │    Agent     │  │  • JSON Export   │ │ │
│  │  │ • Detect     │  │              │  │  • MD Export     │ │ │
│  │  │   Type       │  │ • Extract    │  │                  │ │ │
│  │  │ • OCR (img)  │  │ • Clean      │  │                  │ │ │
│  │  │              │  │ • Tag        │  │                  │ │ │
│  │  └──────────────┘  │ • Enhance    │  └──────────────────┘ │ │
│  │                    └──────────────┘                        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
                              │
                              │ LLM API Calls
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│                    SiliconFlow API                                │
│                  (api.siliconflow.cn)                             │
│                                                                   │
│  ┌────────────────────┐              ┌─────────────────────────┐ │
│  │  DeepSeek-V3.2     │              │     GLM-4.6V            │ │
│  │                    │              │                         │ │
│  │  • Text Processing │              │  • Image OCR            │ │
│  │  • Extraction      │              │  • Vision Analysis      │ │
│  │  • Answer Gen      │              │                         │ │
│  └────────────────────┘              └─────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Text Input Flow

```
User Input (Text)
    │
    ├─▶ Frontend: UploadZone Component
    │       │
    │       └─▶ API Call: POST /api/process/text
    │               │
    ├─▶ Backend: FastAPI Endpoint
    │       │
    │       └─▶ InterviewAgent.process()
    │               │
    │               ├─▶ InputHandler (detect type: text)
    │               │
    │               ├─▶ CoreProcessorAgent
    │               │       │
    │               │       └─▶ DeepSeek-V3.2 LLM
    │               │           • Extract structure
    │               │           • Classify tags
    │               │           • Generate answers (optional)
    │               │
    │               └─▶ Exporter
    │                       │
    │                       ├─▶ JSON file → output/
    │                       └─▶ Markdown file → output/
    │
    └─▶ Frontend: ResultsView Component
            │
            └─▶ Display results + Export links
```

### Image Input Flow

```
User Input (Image)
    │
    ├─▶ Frontend: UploadZone Component (Drag & Drop)
    │       │
    │       └─▶ API Call: POST /api/process/image (multipart/form-data)
    │               │
    ├─▶ Backend: FastAPI Endpoint
    │       │
    │       ├─▶ Save temp file
    │       │
    │       └─▶ InterviewAgent.process()
    │               │
    │               ├─▶ InputHandler
    │               │       │
    │               │       ├─▶ Detect type: image
    │               │       │
    │               │       └─▶ GLM-4.6V Vision Model
    │               │           • Perform OCR
    │               │           • Extract text from image
    │               │
    │               ├─▶ CoreProcessorAgent
    │               │       │
    │               │       └─▶ DeepSeek-V3.2 LLM
    │               │           • Same as text flow
    │               │
    │               └─▶ Exporter
    │                       │
    │                       ├─▶ JSON file → output/
    │                       └─▶ Markdown file → output/
    │
    ├─▶ Clean up temp file
    │
    └─▶ Frontend: ResultsView Component
            │
            └─▶ Display results + Export links
```

## Technology Stack

### Frontend Layer
- **Framework**: React 18.3 with TypeScript
- **Build Tool**: Vite 6.0 (fast HMR, optimized builds)
- **Styling**: Tailwind CSS 3.4 (utility-first CSS)
- **HTTP Client**: Axios 1.7 (promise-based HTTP)
- **File Upload**: React Dropzone 14.3 (drag & drop)
- **Icons**: Lucide React 0.468 (modern icon set)
- **State**: React Hooks (useState, useCallback)

### Backend Layer
- **Framework**: FastAPI 0.115 (async, auto-docs)
- **Server**: Uvicorn 0.32 (ASGI server)
- **Validation**: Pydantic 2.0 (type safety)
- **LLM Framework**: LangChain 0.3 (LLM orchestration)
- **HTTP Client**: httpx 0.27 (async HTTP)
- **Vision**: Pillow 10.0 (image processing)

### AI/LLM Layer
- **Text Model**: DeepSeek-V3.2 (via SiliconFlow)
  - Structured extraction
  - Content analysis
  - Answer generation

- **Vision Model**: GLM-4.6V (via SiliconFlow)
  - OCR capabilities
  - Image understanding
  - Text extraction

## Key Features

### 1. Multi-Modal Input
- **Text**: Paste directly into text area
- **Image**: Drag & drop or file select
- **Auto-detection**: System automatically detects input type

### 2. AI Processing
- **Structured Extraction**: Company, position, stage
- **Question Parsing**: Identify questions and answers
- **Tag Classification**: Auto-tag by topic/category
- **Answer Enhancement**: Generate missing answers with AI

### 3. Export Options
- **JSON**: Machine-readable structured data
- **Markdown**: Human-readable formatted text
- **Download**: Direct browser downloads

### 4. Real-time Feedback
- **Processing Status**: Loading indicators
- **Progress Updates**: Visual feedback
- **Error Handling**: Clear error messages

## API Endpoints

### Health Check
```http
GET /
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2026-01-19T08:00:00",
  "version": "0.1.0"
}
```

### Process Text
```http
POST /api/process/text
Content-Type: application/json

Body:
{
  "content": "interview text...",
  "generate_answers": false,
  "export_format": "both"
}

Response:
{
  "success": true,
  "processing_time": 2.5,
  "experience": { ... },
  "output_files": ["output_xxx.json", "output_xxx.md"]
}
```

### Process Image
```http
POST /api/process/image
Content-Type: multipart/form-data

Body:
  file: <image file>
  generate_answers: false
  export_format: both

Response: Same as process text
```

### List Files
```http
GET /api/files

Response:
{
  "files": [
    {
      "filename": "output_xxx.json",
      "size": 1234,
      "created_at": "2026-01-19T08:00:00",
      "modified_at": "2026-01-19T08:00:00"
    }
  ]
}
```

### Download File
```http
GET /api/download/{filename}

Response: File download (application/json or text/markdown)
```

## Security Considerations

### CORS
- Configured for localhost:5173 (Vite default)
- Configured for localhost:3000 (Next.js default)
- Update for production domains

### File Upload
- Temporary files cleaned after processing
- File type validation (images only)
- Size limits (configured by FastAPI)

### API Keys
- Stored in `.env` file (git-ignored)
- Never exposed to frontend
- Server-side only

## Performance

### Frontend
- **Vite**: Lightning-fast HMR (~20-50ms)
- **Code Splitting**: Automatic route-based splitting
- **Tree Shaking**: Remove unused code
- **Lazy Loading**: Components loaded on demand

### Backend
- **Async/Await**: Non-blocking I/O
- **Connection Pooling**: Reuse HTTP connections
- **Caching**: LLM client connection reuse
- **Streaming**: Support for large responses

### Expected Response Times
- **Text Processing**: 2-5 seconds
- **Image Processing**: 5-10 seconds (includes OCR)
- **File Download**: <100ms
- **API Health Check**: <10ms

## Deployment Architecture

### Development
```
Vite Dev Server (5173) ←→ User Browser
        ↓
FastAPI Server (8000) ←→ SiliconFlow API
        ↓
Local File System (output/)
```

### Production (Example)
```
Vercel/Netlify (Frontend) ←→ User Browser
        ↓
Railway/Render (Backend) ←→ SiliconFlow API
        ↓
S3/Cloud Storage (output/)
```

## Error Handling

### Frontend
- API call errors caught and displayed
- Network timeout handling
- User-friendly error messages
- Dismiss error notifications

### Backend
- Try/catch blocks around LLM calls
- Temp file cleanup in finally blocks
- HTTP exception handling
- Detailed error responses

## Future Enhancements

Potential improvements:
- [ ] User authentication
- [ ] Database storage (PostgreSQL)
- [ ] Search functionality
- [ ] Batch processing
- [ ] Real-time WebSocket updates
- [ ] Answer quality rating
- [ ] Export to more formats (PDF, CSV)
- [ ] Interview statistics dashboard
- [ ] Multi-language support
