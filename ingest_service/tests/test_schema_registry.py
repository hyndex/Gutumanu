import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ingest_service.schema_registry import register_schema
from ingest_service.schemas import TelemetryV1


def test_schema_hash_stable(monkeypatch):
    monkeypatch.delenv("SCHEMA_REGISTRY_URL", raising=False)
    h1 = register_schema(TelemetryV1, "telemetry-value")
    h2 = register_schema(TelemetryV1, "telemetry-value")
    assert h1 == h2
