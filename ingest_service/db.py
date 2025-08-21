import os
import sqlite3
import threading
from contextlib import nullcontext
from hashlib import sha256
from typing import Optional

from prometheus_client import Counter, REGISTRY

try:  # pragma: no cover - opentelemetry optional
    from opentelemetry import trace
except Exception:  # pragma: no cover
    trace = None  # type: ignore

DB_PATH = os.getenv("INGEST_LOG_DB", "/tmp/ingest_log.db")
_lock = threading.Lock()
if "ingest_db_writes_total" in REGISTRY._names_to_collectors:  # pragma: no cover - registry reuse
    _write_counter = REGISTRY._names_to_collectors["ingest_db_writes_total"]  # type: ignore[index]
else:
    _write_counter = Counter("ingest_db_writes_total", "Total ingest log writes")


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ingest_log (
                idempotency_key TEXT PRIMARY KEY,
                checksum TEXT NOT NULL,
                dedupe_count INTEGER NOT NULL
            )
            """
        )
        conn.commit()


def log_ingest(idempotency_key: str, body: bytes) -> int:
    checksum = sha256(body).hexdigest()
    tracer = trace.get_tracer(__name__) if trace else None
    with _lock, sqlite3.connect(DB_PATH) as conn:
        span_ctx = tracer.start_as_current_span("log_ingest") if tracer else nullcontext()
        with span_ctx:  # type: ignore[arg-type]
            try:
                conn.execute(
                    "INSERT INTO ingest_log (idempotency_key, checksum, dedupe_count) VALUES (?, ?, 1)",
                    (idempotency_key, checksum),
                )
                conn.commit()
                _write_counter.inc()
                return 1
            except sqlite3.IntegrityError:
                cur = conn.execute(
                    "SELECT checksum, dedupe_count FROM ingest_log WHERE idempotency_key=?",
                    (idempotency_key,),
                )
                row = cur.fetchone()
                if row is None:
                    # unexpected, treat as new
                    conn.execute(
                        "INSERT OR REPLACE INTO ingest_log (idempotency_key, checksum, dedupe_count) VALUES (?, ?, 1)",
                        (idempotency_key, checksum),
                    )
                    conn.commit()
                    _write_counter.inc()
                    return 1
                existing_checksum, dedupe_count = row
                if existing_checksum != checksum:
                    raise ValueError("Checksum mismatch for Idempotency-Key")
                dedupe_count += 1
                conn.execute(
                    "UPDATE ingest_log SET dedupe_count=? WHERE idempotency_key=?",
                    (dedupe_count, idempotency_key),
                )
                conn.commit()
                _write_counter.inc()
                return dedupe_count
