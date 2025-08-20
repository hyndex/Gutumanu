import importlib
import os
import tempfile

from fastapi.testclient import TestClient


def create_app(rate="5", capacity="10"):
    tmpdir = tempfile.mkdtemp()
    os.environ["INGEST_LOG_DB"] = os.path.join(tmpdir, "ingest.db")
    os.environ["RATE_LIMIT_RATE"] = str(rate)
    os.environ["RATE_LIMIT_CAPACITY"] = str(capacity)
    db_module = importlib.import_module("ingest_service.db")
    importlib.reload(db_module)
    module = importlib.import_module("ingest_service.main")
    importlib.reload(module)
    return module.app, module


def _headers():
    return {
        "Content-Type": "application/vnd.telemetry.v1+json",
        "Idempotency-Key": "abc123",
        "Org-Id": "org1",
    }


def test_deduplication():
    app, _ = create_app()
    payload = {"device_id": "d1", "timestamp": "2024-01-01T00:00:00Z", "lat": 0.0, "lon": 0.0}
    with TestClient(app) as client:
        r1 = client.post("/telemetry", json=payload, headers=_headers())
        assert r1.status_code == 202
        r2 = client.post("/telemetry", json=payload, headers=_headers())
        assert r2.status_code == 200
        assert r2.json()["dedupe_count"] == 2


def test_rate_limit():
    app, module = create_app(rate=0, capacity=1)
    payload = {"device_id": "d1", "timestamp": "2024-01-01T00:00:00Z", "lat": 0.0, "lon": 0.0}
    with TestClient(app) as client:
        r1 = client.post("/telemetry", json=payload, headers=_headers())
        assert r1.status_code == 202
        r2 = client.post("/telemetry", json=payload, headers=_headers())
        assert r2.status_code == 429
        assert "Retry-After" in r2.headers
