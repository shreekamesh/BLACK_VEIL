#!/bin/bash

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                    🛡️ BLACK VEIL - STARTUP                              ║"
echo "║                    Autonomous Cognitive Cyber Defense                   ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

cd /home/eroz/Documents/black_veil

# Activate venv
source venv/bin/activate 2>/dev/null

# Kill old processes
pkill -f "uvicorn inference_api" 2>/dev/null
pkill -f "gunicorn" 2>/dev/null
pkill -f "python3 -m http.server 8080" 2>/dev/null
pkill -f "api_metrics.py" 2>/dev/null

# Start API Server
echo -e "${BLUE}🚀 Starting API Server...${NC}"
nohup uvicorn inference_api:app --host 0.0.0.0 --port 8000 --reload > api_server.log 2>&1 &
echo -e "${GREEN}✅ API Server started (Port 8000)${NC}"

sleep 2

# Start Metrics API
echo -e "${BLUE}📊 Starting Metrics API...${NC}"
nohup python3 api_metrics.py > metrics_api.log 2>&1 &
echo -e "${GREEN}✅ Metrics API started (Port 8001)${NC}"

sleep 1

# Start Dashboard
echo -e "${BLUE}🖥️ Starting Dashboard...${NC}"
cd dashboard
nohup python3 -m http.server 8080 > dashboard.log 2>&1 &
echo -e "${GREEN}✅ Dashboard started (Port 8080)${NC}"
cd ..

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ BLACK VEIL IS RUNNING!                             ║"
echo "╠═══════════════════════════════════════════════════════════════════════════╣"
echo "║                                                                          ║"
echo -e "║  🔗 API Server:    ${GREEN}http://localhost:8000${NC}                                          ║"
echo -e "║  📊 Metrics API:   ${GREEN}http://localhost:8001/api/metrics${NC}                                ║"
echo -e "║  🖥️ Dashboard:     ${GREEN}http://localhost:8080${NC}                                          ║"
echo "║                                                                          ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

xdg-open http://localhost:8080 2>/dev/null || echo "Open http://localhost:8080"
