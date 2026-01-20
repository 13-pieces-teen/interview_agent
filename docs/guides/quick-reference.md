# Interview Agent - Quick Reference

## 🚀 Quick Start (30 seconds)

```bash
# 1. Install dependencies
uv sync && cd frontend && npm install && cd ..

# 2. Set API key
echo "SILICONFLOW_API_KEY=your_key_here" > .env

# 3. Start everything
start_dev.bat  # Windows
./start_dev.sh # Mac/Linux
```

**Open**: http://localhost:5173

---

## 📁 Project Structure

```
interview_agent/
├── src/api/          → FastAPI backend
├── frontend/src/     → React UI
├── output/           → Generated files
└── .env             → API keys (create this!)
```

---

## 🔧 Common Commands

### Backend
```bash
# Start API server
python -m uvicorn src.api.app:app --reload

# Run tests
uv run pytest

# Format code
uv run black src/
```

### Frontend
```bash
cd frontend

# Start dev server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

---

## 🌐 URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Web UI |
| **Backend** | http://localhost:8000 | API Server |
| **API Docs** | http://localhost:8000/docs | Interactive docs |

---

## 📡 API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Process text
curl -X POST http://localhost:8000/api/process/text \
  -H "Content-Type: application/json" \
  -d '{"content": "面试内容...", "generate_answers": false}'

# List files
curl http://localhost:8000/api/files

# Download file
curl http://localhost:8000/api/download/output_xxx.json
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000 (backend)
# Windows: taskkill /PID (from netstat -ano | findstr :8000) /F
# Mac/Linux: lsof -ti:8000 | xargs kill -9

# Kill process on port 5173 (frontend)
# Windows: taskkill /PID (from netstat -ano | findstr :5173) /F
# Mac/Linux: lsof -ti:5173 | xargs kill -9
```

### Module Not Found
```bash
# Backend
uv sync --force

# Frontend
cd frontend && rm -rf node_modules && npm install
```

### CORS Errors
Check `src/api/app.py` - ensure your frontend URL is in `allow_origins`

---

## 🎯 Usage Flow

### Text Input
1. Open http://localhost:5173
2. Click **"Text Input"**
3. Paste interview content
4. Toggle **"Generate AI answers"** (optional)
5. Click **"Process Interview Experience"**
6. View results and download exports

### Image Input
1. Open http://localhost:5173
2. Click **"Image Upload"**
3. Drag & drop screenshot
4. Wait for OCR + processing
5. View results and download exports

---

## 📦 Tech Stack

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- Axios (HTTP client)

### Backend
- FastAPI (async web framework)
- Python 3.10+
- Pydantic (validation)
- LangChain (LLM orchestration)

### AI Models
- **DeepSeek-V3.2**: Text processing
- **GLM-4.6V**: Image OCR

---

## 📝 Environment Variables

Create `.env` file:
```bash
# Required
SILICONFLOW_API_KEY=sk-xxx

# Optional (with defaults)
SILICONFLOW_API_BASE=https://api.siliconflow.cn/v1
DEEPSEEK_MODEL=Pro/deepseek-ai/DeepSeek-V3.2
GLM_VISION_MODEL=zai-org/GLM-4.6V
OUTPUT_DIR=output
DATA_DIR=data
```

---

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `src/api/app.py` | FastAPI server |
| `src/main.py` | CLI entry point |
| `frontend/src/App.tsx` | Main React app |
| `frontend/src/services/api.ts` | API client |
| `.env` | Environment config |
| `pyproject.toml` | Python dependencies |
| `frontend/package.json` | Node dependencies |

---

## 🎨 UI Components

- **UploadZone**: Text/image input with drag & drop
- **ResultsView**: Structured interview display
- **ExportPanel**: Download JSON/Markdown
- **ErrorMessage**: User-friendly error display

---

## 📊 Data Models

### InterviewExperience
```typescript
{
  source_type: string
  company_name?: string
  company_scale?: string
  position?: string
  interview_stage?: string
  interview_experience?: string
  questions: Question[]
  tags: string[]
  raw_content: string
}
```

### Question
```typescript
{
  question: string
  answer?: string
  has_original_answer: boolean
  tags: string[]
}
```

---

## 🔄 Development Workflow

1. Make changes to code
2. See instant updates (hot reload)
3. Test in browser
4. Check console/terminal for errors
5. Commit when ready

Both frontend and backend support **hot reload** - changes appear instantly!

---

## 📚 Documentation

- [README.md](README.md) - Overview & quick start
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [frontend/README.md](frontend/README.md) - Frontend docs
- **This file** - Quick reference

---

## 💡 Tips

- Use **API Docs** (http://localhost:8000/docs) to test endpoints
- Check **browser console** (F12) for frontend errors
- Check **terminal** for backend errors
- Generated files go to `output/` directory
- Temp files cleaned automatically after processing

---

## 🎓 Example Interview Content

```
公司：阿里巴巴
职位：高级Python工程师
阶段：技术一面

面试体验：
面试官很专业，问题由浅入深。主要围绕Python和系统设计。

问题：
1. 介绍一下Python的GIL及其影响
答：全局解释器锁，保证同一时刻只有一个线程执行Python字节码...

2. 设计一个URL短链接系统
答：使用哈希算法，数据库存储映射关系...
```

---

## 🔗 Useful Links

- Python: https://python.org
- Node.js: https://nodejs.org
- uv: https://github.com/astral-sh/uv
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- Vite: https://vite.dev
- Tailwind: https://tailwindcss.com

---

## 📞 Support

- **Issues**: Check GitHub issues
- **Docs**: Read the detailed guides
- **Logs**: Check terminal output
- **API**: Use /docs endpoint for API testing

---

**Made with ❤️ using DeepSeek-V3.2 and GLM-4.6V**
