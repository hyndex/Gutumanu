import json
import logging
import os
from typing import Any, Dict

try:
    from kafka import KafkaProducer
except Exception:  # pragma: no cover - dependency optional
    KafkaProducer = None

logger = logging.getLogger(__name__)


class KafkaSink:
    def __init__(self) -> None:
        self.topic = os.getenv("KAFKA_TELEMETRY_TOPIC", "telemetry.raw")
        servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        if KafkaProducer:
            try:  # pragma: no cover - best effort to initialise
                self.producer = KafkaProducer(bootstrap_servers=servers)
            except Exception:  # pragma: no cover - fallback when broker absent
                logger.warning("Kafka producer init failed; running in noop mode", exc_info=True)
                self.producer = None
        else:  # pragma: no cover - used when kafka lib missing
            self.producer = None

    def publish(self, data: Dict[str, Any]) -> None:
        payload = json.dumps(data).encode("utf-8")
        if self.producer is None:
            logger.info("Kafka producer unavailable; dropping payload")
            return
        try:  # pragma: no cover - network interaction
            self.producer.send(self.topic, payload)
        except Exception as exc:
            logger.error("Kafka publish failed: %s", exc)
