import hashlib
import importlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest_service.schemas import TelemetryV1


class DummyProducer:
    def __init__(self, *args, **kwargs):
        pass

    def send(self, topic, payload, headers=None):  # pragma: no cover - simple stub
        DummyProducer.captured = headers


def test_schema_hash_header(monkeypatch):
    kafka_module = importlib.import_module("ingest_service.kafka")
    monkeypatch.setattr(kafka_module, "KafkaProducer", DummyProducer)
    monkeypatch.setattr(kafka_module.urllib.request, "urlopen", lambda req: None)
    sink = kafka_module.KafkaSink()
    sink.publish({})

    expected = hashlib.sha256(
        json.dumps(TelemetryV1.model_json_schema(), sort_keys=True).encode("utf-8")
    ).hexdigest().encode("utf-8")
    assert ("schema-hash", expected) in DummyProducer.captured
