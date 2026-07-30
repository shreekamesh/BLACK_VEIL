#!/bin/bash
echo "🛑 Stopping BLACK VEIL..."
pkill -f "uvicorn inference_api" 2>/dev/null
pkill -f "gunicorn" 2>/dev/null
pkill -f "python3 -m http.server 8080" 2>/dev/null
pkill -f "api_metrics.py" 2>/dev/null
echo "✅ All services stopped!"
