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

# Load telemetry data safely
data_path = os.path.join(os.path.dirname(__file__), "data.json")
try:
    with open(data_path, "r") as f:
        telemetry = json.load(f)
except FileNotFoundError:
    telemetry = {}
    print(f"Warning: telemetry file not found at {data_path}")
except json.JSONDecodeError:
    telemetry = {}
    print(f"Warning: telemetry file {data_path} contains invalid JSON")

@app.post("/")
async def check_latency(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON in request body"}, status_code=400)

    regions = data.get("regions")
    threshold = data.get("threshold_ms")

    if regions is None or not isinstance(regions, list):
        return JSONResponse(content={"error": "Missing or invalid 'regions' field"}, status_code=400)
    if threshold is None or not isinstance(threshold, (int, float)):
        return JSONResponse(content={"error": "Missing or invalid 'threshold_ms' field"}, status_code=400)

    result = {}
    for region in regions:
        region_data = telemetry.get(region)
        if not region_data:
            result[region] = {"error": "Region not found or no telemetry data"}
            continue

        latencies = [r.get("latency_ms", 0) for r in region_data if isinstance(r.get("latency_ms"), (int, float))]
        uptimes = [r.get("uptime", 0) for r in region_data if isinstance(r.get("uptime"), (int, float))]

        if not latencies or not uptimes:
            result[region] = {"error": "Telemetry data is invalid or incomplete"}
            continue

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
