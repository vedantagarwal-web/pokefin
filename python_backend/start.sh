#!/bin/bash

# AlphaWealth Startup Script

echo "🚀 Starting AlphaWealth..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - FINANCIAL_DATASETS_API_KEY (optional)"
    echo "   - EXA_API_KEY (optional)"
    echo ""
fi

# Start the server
echo "✅ Starting AlphaWealth backend on port 8788..."
echo ""
python main.py

