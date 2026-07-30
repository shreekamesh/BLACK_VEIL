from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psutil
import time
import random
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

start_time = time.time()

@app.get("/api/metrics")
async def get_metrics():
    cpu_percent = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()
    memory_gb = mem.used / (1024**3)
    memory_total_gb = mem.total / (1024**3)
    trust = round(65 + random.random() * 30, 1)
    
    return {
        "cpu": round(cpu_percent, 1),
        "memory": round(memory_gb, 1),
        "memory_total": round(memory_total_gb, 1),
        "memory_percent": mem.percent,
        "uptime": round(time.time() - start_time),
        "trust": trust,
        "events": random.randint(50, 200),
        "threats": random.randint(0, 5),
        "blocked": random.randint(10, 40),
        "response": random.randint(5, 25),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
