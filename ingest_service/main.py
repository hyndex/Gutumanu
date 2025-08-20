import os
import re
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from . import db
from .kafka import KafkaSink
from .rate_limit import RateLimiter
from .schemas import TelemetryV1, TripV1

app = FastAPI()

RATE_LIMIT_RATE = float(os.getenv("RATE_LIMIT_RATE", "5"))
RATE_LIMIT_CAPACITY = int(os.getenv("RATE_LIMIT_CAPACITY", "10"))
rate_limiter = RateLimiter(RATE_LIMIT_RATE, RATE_LIMIT_CAPACITY)
producer = KafkaSink()


def _parse_version(content_type: str, media: str) -> int:
    pattern = rf"application/vnd.{media}.v(\d+)\+json"
    m = re.fullmatch(pattern, content_type)
    if not m:
        raise HTTPException(status_code=415, detail="Unsupported Content-Type")
    return int(m.group(1))


@app.on_event("startup")
async def startup() -> None:
    db.init_db()


@app.post("/telemetry", status_code=202)
async def ingest_telemetry(
    request: Request,
    content_type: str = Header(..., alias="Content-Type"),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    org_id: str = Header(..., alias="Org-Id"),
):
    allowed, retry_after = rate_limiter.consume(org_id)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded", headers={"Retry-After": str(int(retry_after))})

    version = _parse_version(content_type, "telemetry")
    if version != 1:
        raise HTTPException(status_code=415, detail="Unsupported version")
    body = await request.body()
    try:
        payload = TelemetryV1.model_validate_json(body)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        dedupe_count = db.log_ingest(idempotency_key, body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if dedupe_count > 1:
        return JSONResponse(status_code=200, content={"status": "duplicate", "dedupe_count": dedupe_count})

    producer.publish(payload.model_dump(mode="json"), "telemetry")
    return {"status": "accepted"}


@app.post("/trip", status_code=202)
async def ingest_trip(
    request: Request,
    content_type: str = Header(..., alias="Content-Type"),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    org_id: str = Header(..., alias="Org-Id"),
):
    allowed, retry_after = rate_limiter.consume(org_id)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded", headers={"Retry-After": str(int(retry_after))})

    version = _parse_version(content_type, "trip")
    if version != 1:
        raise HTTPException(status_code=415, detail="Unsupported version")
    body = await request.body()
    try:
        payload = TripV1.model_validate_json(body)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        dedupe_count = db.log_ingest(idempotency_key, body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if dedupe_count > 1:
        return JSONResponse(status_code=200, content={"status": "duplicate", "dedupe_count": dedupe_count})

    producer.publish(payload.model_dump(mode="json"), "trip")
    return {"status": "accepted"}
