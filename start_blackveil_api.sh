#!/bin/bash
echo "🛡️ Starting BLACK VEIL API Server..."
cd /home/eroz/Documents/black_veil
source venv/bin/activate

# Kill old processes
pkill -f "uvicorn" 2>/dev/null
pkill -f "blackveil_api" 2>/dev/null
sleep 2

# Start server
nohup uvicorn blackveil_api_with_metrics:app --host 0.0.0.0 --port 8000 --reload > api_server.log 2>&1 &
sleep 5

# Check if running
echo ""
echo "🔍 Verifying..."
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "✅ API Server running on http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "📊 Metrics: http://localhost:9090/metrics"
echo ""
echo "📝 Logs: tail -f api_server.log"
