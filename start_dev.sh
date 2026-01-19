#!/bin/bash

echo "🚀 Starting Interview Agent Full Stack Application"
echo ""

# Check if backend dependencies are installed
if [ ! -d ".venv" ]; then
    echo "📦 Installing backend dependencies..."
    uv sync
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start backend API
echo ""
echo "🔧 Starting FastAPI backend on http://localhost:8000"
source .venv/bin/activate
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend dev server
echo ""
echo "🎨 Starting Vite frontend on http://localhost:5173"
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Application started!"
echo "   Backend API: http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C and kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for both processes
wait
