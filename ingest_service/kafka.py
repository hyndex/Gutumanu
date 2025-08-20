import json
import logging
import os
from typing import Any, Dict, Type

try:
    from kafka import KafkaProducer
except Exception:  # pragma: no cover - dependency optional
    KafkaProducer = None

from pydantic import BaseModel

from .schema_registry import register_schema
from .schemas import TelemetryV1, TripV1

logger = logging.getLogger(__name__)


class KafkaSink:
    """Kafka producer that registers schemas and embeds their hash."""

    def __init__(self) -> None:
        self.topic = os.getenv("KAFKA_TELEMETRY_TOPIC", "telemetry.raw")
        servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.schema_hashes: Dict[str, str] = {}

        if KafkaProducer:
            try:  # pragma: no cover - best effort to initialise
                self.producer = KafkaProducer(bootstrap_servers=servers)
            except Exception:  # pragma: no cover - fallback when broker absent
                logger.warning("Kafka producer init failed; running in noop mode", exc_info=True)
                self.producer = None
        else:  # pragma: no cover - used when kafka lib missing
            self.producer = None

        # pre-register known schemas
        self.register(TelemetryV1, "telemetry")
        self.register(TripV1, "trip")

    def register(self, model: Type[BaseModel], name: str) -> None:
        subject = f"{name}-value"
        self.schema_hashes[name] = register_schema(model, subject)

    def publish(self, data: Dict[str, Any], schema: str) -> None:
        payload = json.dumps(data).encode("utf-8")
        headers = []
        sha = self.schema_hashes.get(schema)
        if sha:
            headers.append(("schema_hash", sha.encode("utf-8")))
        if self.producer is None:
            logger.info("Kafka producer unavailable; dropping payload")
            return
        try:  # pragma: no cover - network interaction
            self.producer.send(self.topic, payload, headers=headers)
        except Exception as exc:
            logger.error("Kafka publish failed: %s", exc)
