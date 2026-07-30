#!/bin/bash
echo "========================================"
echo "   BLACK VEIL - Cyber Defense System"
echo "========================================"
echo ""
source venv/bin/activate
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi
echo "Virtual environment activated!"
echo ""
echo "Starting BLACK VEIL API Server..."
echo "Server will run on http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop the server"
echo "========================================"
echo ""
uvicorn inference_api:app --host 0.0.0.0 --port 8000 --reload
