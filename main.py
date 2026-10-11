
import os
import time
import logging
import pandas as pd

from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

from mapreduce import analyze_traffic
from database import (
    initialize_database,
    get_connection,
    save_traffic_records,
    load_traffic_records,
    save_analysis_results,
    record_analysis_run
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("traffic-analyzer")

API_KEY = os.getenv("API_KEY", "local-demo-key")

app = FastAPI(
    title="MapReduce Traffic Analyzer",
    description="Traffic congestion analysis API",
    version="1.0.0"
)


@app.on_event("startup")
def startup():
    initialize_database()
    logger.info("Traffic Analyzer API started")


def verify_api_key(x_api_key):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )


class TrafficRecord(BaseModel):
    record_id: int
    location: str = Field(min_length=1)
    timestamp: datetime
    vehicle_count: int = Field(ge=0)
    avg_speed: float = Field(gt=0)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "Traffic Analyzer"}


@app.post("/traffic/upload")
def upload_traffic(
    records: list[TrafficRecord],
    x_api_key: str = Header(default="")
):
    verify_api_key(x_api_key)

    if not records:
        raise HTTPException(400, "No records provided")

    try:
        normalized = [
            {
                "record_id": r.record_id,
                "location": r.location,
                "timestamp": r.timestamp.isoformat(),
                "vehicle_count": r.vehicle_count,
                "avg_speed": r.avg_speed
            }
            for r in records
        ]

        save_traffic_records(normalized)

        logger.info("Accepted %d traffic records", len(normalized))

        return {
            "status": "success",
            "records_received": len(normalized)
        }

    except Exception:
        logger.exception("Traffic upload failed")
        raise HTTPException(500, "Could not store traffic records")


@app.post("/analysis/run")
def run_analysis(x_api_key: str = Header(default="")):
    verify_api_key(x_api_key)
    start = time.perf_counter()
    df = load_traffic_records()

    if df.empty:
        raise HTTPException(400, "No traffic data available")

    try:
        results = analyze_traffic(df)
        elapsed = time.perf_counter() - start

        save_analysis_results(results)
        record_analysis_run(len(df), elapsed, "SUCCESS")

        logger.info(
            "Processed %d records in %.4f seconds",
            len(df), elapsed
        )

        return {
            "status": "success",
            "records_processed": len(df),
            "groups_created": len(results),
            "processing_time_seconds": round(elapsed, 4)
        }

    except Exception:
        elapsed = time.perf_counter() - start
        record_analysis_run(len(df), elapsed, "FAILED")
        logger.exception("Analysis failed")
        raise HTTPException(500, "Analysis failed; check application logs")


@app.get("/analysis/results")
def get_results(
    limit: int = Query(default=20, ge=1, le=1000),
    x_api_key: str = Header(default="")
):
    verify_api_key(x_api_key)

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT location, hour, total_vehicles,
                   average_speed, congestion_score, record_count
            FROM analysis_results
            ORDER BY congestion_score DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return {"results": [dict(r) for r in rows]}


@app.get("/analysis/locations")
def get_locations(x_api_key: str = Header(default="")):
    verify_api_key(x_api_key)

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT location,
                   ROUND(AVG(congestion_score), 2)
                       AS average_congestion,
                   SUM(total_vehicles) AS total_vehicles
            FROM analysis_results
            GROUP BY location
            ORDER BY average_congestion DESC
        """).fetchall()

    return {"locations": [dict(r) for r in rows]}


@app.get("/metrics")
def get_metrics(x_api_key: str = Header(default="")):
    verify_api_key(x_api_key)

    with get_connection() as conn:
        row = conn.execute("""
            SELECT dataset_size, processing_time, status, created_at
            FROM analysis_runs
            ORDER BY id DESC LIMIT 1
        """).fetchone()

    if row is None:
        return {"message": "No analysis runs recorded"}

    result = dict(row)
    elapsed = result["processing_time"] or 0

    result["records_per_second"] = (
        round(result["dataset_size"] / elapsed, 2)
        if elapsed > 0 else None
    )

    return result
