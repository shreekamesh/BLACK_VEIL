#!/bin/bash
echo "📊 BLACK VEIL STATUS"
echo "==================="
echo ""

if pgrep -f "uvicorn inference_api" > /dev/null; then
    echo "✅ API Server (Port 8000): RUNNING"
else
    echo "❌ API Server (Port 8000): STOPPED"
fi

if pgrep -f "api_metrics.py" > /dev/null; then
    echo "✅ Metrics API (Port 8001): RUNNING"
else
    echo "❌ Metrics API (Port 8001): STOPPED"
fi

if pgrep -f "http.server 8080" > /dev/null; then
    echo "✅ Dashboard (Port 8080): RUNNING"
else
    echo "❌ Dashboard (Port 8080): STOPPED"
fi

echo ""
echo "🔗 http://localhost:8000 - API"
echo "🔗 http://localhost:8001/api/metrics - Metrics"
echo "🔗 http://localhost:8080 - Dashboard"
