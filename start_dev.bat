@echo off
echo Starting Interview Agent Full Stack Application
echo.

REM Check if backend dependencies are installed
if not exist ".venv\" (
    echo Installing backend dependencies...
    uv sync
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules\" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM Start backend API
echo.
echo Starting FastAPI backend on http://localhost:8000
start "Interview Agent API" cmd /k ".venv\Scripts\activate && python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend dev server
echo.
echo Starting Vite frontend on http://localhost:5173
start "Interview Agent Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Application started!
echo    Backend API: http://localhost:8000
echo    Frontend: http://localhost:5173
echo    API Docs: http://localhost:8000/docs
echo.
echo Close both command windows to stop the services
