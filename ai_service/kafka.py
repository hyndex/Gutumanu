import json
import logging
import os
from typing import Any, Dict

from prometheus_client import Counter, REGISTRY

try:  # pragma: no cover - optional dependency
    from kafka import KafkaProducer
except Exception:  # pragma: no cover - fallback when kafka client missing
    KafkaProducer = None

logger = logging.getLogger(__name__)


class ScoreSink:
    """Publishes inference scores to a Kafka topic."""

    def __init__(self) -> None:
        self.topic = os.getenv("KAFKA_SCORES_TOPIC", "model.scores")
        servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        if KafkaProducer:
            try:  # pragma: no cover - best effort
                self.producer = KafkaProducer(bootstrap_servers=servers)
            except Exception:  # pragma: no cover - connection failures tolerated
                logger.warning("Kafka producer init failed; running in noop mode", exc_info=True)
                self.producer = None
        else:  # pragma: no cover - kafka not installed
            self.producer = None
        if "kafka_scores_published_total" in REGISTRY._names_to_collectors:
            self._counter = REGISTRY._names_to_collectors["kafka_scores_published_total"]  # type: ignore[index]
        else:
            self._counter = Counter("kafka_scores_published_total", "Total score messages", ["topic"])

    def publish(self, data: Dict[str, Any]) -> None:
        payload = json.dumps(data).encode("utf-8")
        if not self.producer:
            logger.info("Kafka producer unavailable; dropping payload")
            return
        try:  # pragma: no cover - network interaction
            self.producer.send(self.topic, payload)
            self._counter.labels(self.topic).inc()
        except Exception as exc:  # pragma: no cover - failure tolerated
            logger.error("Kafka publish failed: %s", exc)
