#!/bin/bash

# Start both Node.js frontend and Python backend

echo "╔═══════════════════════════════════════╗"
echo "║                                       ║"
echo "║          🚀 AlphaWealth 🚀            ║"
echo "║                                       ║"
echo "║   The World's Best AI Financial       ║"
echo "║        Wealth Manager                 ║"
echo "║                                       ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f "python_backend/.env" ]; then
    echo "⚠️  No .env file found in python_backend/"
    echo "   Creating from .env.example..."
    cp python_backend/.env.example python_backend/.env
    echo ""
    echo "⚠️  IMPORTANT: Edit python_backend/.env and add your API keys:"
    echo "   - OPENAI_API_KEY (required)"
    echo "   - FINANCIAL_DATASETS_API_KEY (optional, will use mock data)"
    echo "   - EXA_API_KEY (optional, will use mock data)"
    echo ""
    echo "Press Enter to continue..."
    read
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "👋 Shutting down AlphaWealth..."
    kill $NODE_PID $PYTHON_PID 2>/dev/null
    exit
}

trap cleanup INT TERM

# Start Node.js server (frontend + original API)
echo "🌐 Starting Node.js server (port 8787)..."
node server/index.js &
NODE_PID=$!

sleep 2

# Start Python backend (AI agents)
echo "🤖 Starting Python backend (port 8788)..."
cd python_backend
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
python main.py &
PYTHON_PID=$!
cd ..

echo ""
echo "✅ AlphaWealth is running!"
echo ""
echo "   Frontend:      http://localhost:8787"
echo "   Python API:    http://localhost:8788"
echo "   API Docs:      http://localhost:8788/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait

