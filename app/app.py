from fastapi import FastAPI, Request
import json
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["POST"],
#     allow_headers=["*"],
# )

# Load telemetry data
with open("data.json") as f:
    telemetry = json.load(f)

@app.post("/")
async def check_latency(request: Request):
    data = await request.json()
    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 0)

    result = {}
    for region in regions:
        region_data = telemetry.get(region, [])
        if not region_data:
            result[region] = {
                "error": "Region not found"
            }
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

    return result
