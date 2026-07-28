#!/bin/bash
cd /home/eroz/Documents/black_veil
source venv/bin/activate

echo "📊 Starting BLACK VEIL Metrics Server..."

# Kill old metrics
pkill -f "prometheus_metrics" 2>/dev/null

# Start new metrics
nohup python3 -c "
from prometheus_metrics import start_metrics_server
start_metrics_server(9090)
import time
while True:
    time.sleep(1)
" > metrics_server.log 2>&1 &

sleep 2

# Verify
if curl -s http://localhost:9090/metrics > /dev/null; then
    echo "✅ Metrics server running on port 9090"
    echo "📊 Metrics URL: http://localhost:9090/metrics"
    echo ""
    echo "Sample metrics:"
    curl -s http://localhost:9090/metrics | grep -E "blackveil|python" | head -5
else
    echo "❌ Metrics server failed to start"
    echo "Check logs: tail -f metrics_server.log"
fi
