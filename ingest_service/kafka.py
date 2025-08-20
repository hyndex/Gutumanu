import hashlib
import json
import logging
import os
import urllib.request
from typing import Any, Dict

try:
    from kafka import KafkaProducer
except Exception:  # pragma: no cover - dependency optional
    KafkaProducer = None

from .schemas import TelemetryV1

logger = logging.getLogger(__name__)


class KafkaSink:
    def __init__(self) -> None:
        self.topic = os.getenv("KAFKA_TELEMETRY_TOPIC", "telemetry.raw")
        servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.schema_hash = self._register_schema()
        if KafkaProducer:
            try:  # pragma: no cover - best effort to initialise
                self.producer = KafkaProducer(bootstrap_servers=servers)
            except Exception:  # pragma: no cover - fallback when broker absent
                logger.warning("Kafka producer init failed; running in noop mode", exc_info=True)
                self.producer = None
        else:  # pragma: no cover - used when kafka lib missing
            self.producer = None

    def _register_schema(self) -> str:
        schema_dict = TelemetryV1.model_json_schema()
        schema_str = json.dumps(schema_dict, sort_keys=True)
        schema_hash = hashlib.sha256(schema_str.encode("utf-8")).hexdigest()
        registry = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
        subject = f"{self.topic}-value"
        payload = json.dumps({"schema": schema_str}).encode("utf-8")
        req = urllib.request.Request(
            f"{registry}/subjects/{subject}/versions",
            data=payload,
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
        )
        try:  # pragma: no cover - network interaction
            urllib.request.urlopen(req)
        except Exception:  # pragma: no cover - failure tolerated
            logger.warning("Schema registration failed", exc_info=True)
        return schema_hash

    def publish(self, data: Dict[str, Any]) -> None:
        payload = json.dumps(data).encode("utf-8")
        if self.producer is None:
            logger.info("Kafka producer unavailable; dropping payload")
            return
        try:  # pragma: no cover - network interaction
            headers = [("schema-hash", self.schema_hash.encode("utf-8"))]
            self.producer.send(self.topic, payload, headers=headers)
        except Exception as exc:
            logger.error("Kafka publish failed: %s", exc)
