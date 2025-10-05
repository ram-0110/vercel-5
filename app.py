from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import json
import os

app = FastAPI()

# Allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load telemetry data
data_path = os.path.join(os.path.dirname(__file__), "./data.json")
with open(data_path) as f:
    telemetry = json.load(f)

@app.post("/")
async def check_latency(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON"}, status_code=400)

    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 0)

    result = {}
    for region in regions:
        region_data = telemetry.get(region, [])
        if not region_data:
            result[region] = {"error": "Region not found"}
            continue

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime"] for r in region_data]

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))

        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "under_threshold": avg_latency < threshold
        }

    return JSONResponse(content=result)
