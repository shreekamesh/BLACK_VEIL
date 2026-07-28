"""
BLACK VEIL V2 — Entry Point
Temporal Trust Recovery and Adaptive Cyber Deception Framework
IEEE Research Project — Multi-Agent AI Systems

Usage:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
import logging
import os
import sys

import uvicorn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.app import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/blackveil.log"),
    ],
)

logger = logging.getLogger("blackveil")
app = create_app()

if __name__ == "__main__":
    host = os.getenv("BV_HOST", "0.0.0.0")
    port = int(os.getenv("BV_PORT", "8000"))
    reload = os.getenv("BV_RELOAD", "false").lower() == "true"
    logger.info(f"Starting BLACK VEIL V2 on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=reload, log_level="info")
