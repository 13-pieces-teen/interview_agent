# Web Interface Setup Guide

This guide will help you set up and run the Interview Agent web application.

## Prerequisites

### Required Software

1. **Python 3.10 or higher**
   - Check version: `python --version`
   - Download: https://www.python.org/downloads/

2. **Node.js 18 or higher**
   - Check version: `node --version`
   - Download: https://nodejs.org/

3. **npm** (comes with Node.js)
   - Check version: `npm --version`

4. **uv** (Python package manager)
   - Install: `pip install uv`
   - Or follow: https://github.com/astral-sh/uv

### API Key

You'll need a SiliconFlow API key:
- Sign up at: https://siliconflow.cn/
- Get your API key from the dashboard

## Installation Steps

### Step 1: Clone and Navigate

```bash
cd interview_agent
```

### Step 2: Install Backend Dependencies

```bash
# Install Python dependencies using uv
uv sync

# This creates a virtual environment and installs:
# - FastAPI
# - LangChain
# - Pydantic
# - And other dependencies
```

### Step 3: Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# This installs:
# - React
# - TypeScript
# - Vite
# - Tailwind CSS
# - And other dependencies

# Return to root directory
cd ..
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# On Windows: notepad .env
# On Mac/Linux: nano .env
```

Add your API key:
```
SILICONFLOW_API_KEY=your_actual_api_key_here
```

## Running the Application

### Option 1: Use Development Scripts (Easiest)

#### Windows
```bash
start_dev.bat
```

This will:
1. Activate Python virtual environment
2. Start FastAPI backend on port 8000
3. Start Vite dev server on port 5173
4. Open two command windows

#### Linux/Mac
```bash
chmod +x start_dev.sh
./start_dev.sh
```

This will:
1. Activate Python virtual environment
2. Start both servers in the background
3. Display status messages

### Option 2: Manual Start (Separate Terminals)

#### Terminal 1 - Backend
```bash
# Activate virtual environment
source .venv/bin/activate  # Mac/Linux
# OR
.venv\Scripts\activate     # Windows

# Start FastAPI server
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend
```bash
# Navigate to frontend
cd frontend

# Start dev server
npm run dev
```

## Accessing the Application

Once both servers are running:

- **Web Interface**: http://localhost:5173
- **API Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## Using the Web Interface

1. **Open your browser** to http://localhost:5173

2. **Choose input method**:
   - Click "Text Input" to paste interview text
   - Click "Image Upload" to upload interview screenshots

3. **Configure options**:
   - Toggle "Generate AI answers" if you want missing answers filled in

4. **Submit**:
   - For text: Click "Process Interview Experience"
   - For image: Drag & drop or click to select file

5. **View results**:
   - See structured interview data
   - Browse questions and answers
   - View tags and classifications

6. **Download exports**:
   - Click download buttons for JSON or Markdown files

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find and kill the process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

**Module not found errors:**
```bash
# Reinstall dependencies
uv sync --force
```

**API key errors:**
- Check your `.env` file has the correct key
- Ensure no extra spaces around the key
- Restart the backend server after changing `.env`

### Frontend Issues

**Port 5173 already in use:**
```bash
# The dev server will automatically try port 5174, 5175, etc.
# Or kill the process:
# Mac/Linux:
lsof -ti:5173 | xargs kill -9
```

**Module not found errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Build errors:**
```bash
cd frontend
npm run build -- --debug
```

### Connection Issues

**Frontend can't reach backend:**
1. Ensure both servers are running
2. Check backend is on port 8000: http://localhost:8000/health
3. Clear browser cache
4. Check browser console for CORS errors

**CORS errors:**
- The backend is configured for localhost:5173 and localhost:3000
- If using a different port, update `src/api/app.py`:
  ```python
  allow_origins=["http://localhost:YOUR_PORT"]
  ```

## Development Tips

### Hot Reload

Both servers support hot reload:
- **Backend**: Automatically reloads on Python file changes
- **Frontend**: Automatically reloads on any source file changes

### Viewing Logs

**Backend logs:**
- Shown in the terminal running uvicorn
- Look for request logs, errors, and stack traces

**Frontend logs:**
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for API calls

### API Testing

Use the built-in API docs:
1. Go to http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Fill in parameters
4. Click "Execute"
5. View response

## Next Steps

- Read the [main README](../README.md) for architecture details
- Check [frontend README](frontend/README.md) for frontend specifics
- Explore the API at http://localhost:8000/docs
- Try processing sample interview content

## Common Workflows

### Testing Text Processing
1. Open web interface
2. Select "Text Input"
3. Paste this sample:
   ```
   公司：科技有限公司
   职位：Python工程师
   一面技术面试

   问题1：介绍一下Python的GIL
   答：全局解释器锁...
   ```
4. Click "Process Interview Experience"

### Testing Image Processing
1. Take a screenshot of interview questions
2. Open web interface
3. Select "Image Upload"
4. Drag & drop your screenshot
5. Wait for OCR and processing

### Downloading Results
1. After processing completes
2. Scroll to "Export Files" section
3. Click JSON or MD download buttons
4. Files are saved to `output/` directory

## Production Deployment

For production deployment:

### Backend
```bash
# Install production dependencies
uv sync --no-dev

# Run with Gunicorn
gunicorn src.api.app:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
```bash
cd frontend

# Build for production
npm run build

# Serve the dist/ folder with nginx, Apache, or any static server
```

See deployment guides for specific platforms (Vercel, Railway, Docker, etc.)
