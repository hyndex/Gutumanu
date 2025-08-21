import logging
import os
import re

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pythonjsonlogger import jsonlogger

from gutumanu.logging import OpenSearchHandler, PIIFilter
from rules import RuleEngine, parse_rules
from rules import db as rules_db

from . import db
from .kafka import KafkaSink
from .rate_limit import RateLimiter
from .schemas import TelemetryV1, TripV1

try:  # pragma: no cover - optional observability hooks
    from prometheus_fastapi_instrumentator import Instrumentator
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint:
        resource = Resource.create({"service.name": "ingest_service"})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
    else:  # pragma: no cover
        FastAPIInstrumentor = None  # type: ignore
except Exception:  # pragma: no cover
    Instrumentator = None  # type: ignore
    FastAPIInstrumentor = None  # type: ignore

app = FastAPI()

if 'Instrumentator' in globals() and Instrumentator:  # pragma: no cover - optional pkg
    Instrumentator().instrument(app).expose(app)
    try:
        FastAPIInstrumentor.instrument_app(app)
    except Exception:
        pass

formatter = jsonlogger.JsonFormatter()
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.addFilter(PIIFilter())
root_logger.addHandler(stream_handler)
os_handler = OpenSearchHandler()
os_handler.setFormatter(formatter)
os_handler.addFilter(PIIFilter())
root_logger.addHandler(os_handler)

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
    rules_db.init_db()


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

    producer.publish(payload.model_dump(mode="json"))
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

    producer.publish(payload.model_dump(mode="json"))
    return {"status": "accepted"}


@app.post("/v1/alerts/test")
async def test_alerts(request: Request):
    body = await request.json()
    rule_src = body.get("rule")
    payload = body.get("payload", {})
    if not rule_src:
        raise HTTPException(status_code=400, detail="rule is required")
    parsed = parse_rules(rule_src)
    engine = RuleEngine([parsed])
    actions = engine.run(payload)
    return {"actions": actions}
