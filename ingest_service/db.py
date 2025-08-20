import os
import sqlite3
import threading
from hashlib import sha256
from typing import Optional

DB_PATH = os.getenv("INGEST_LOG_DB", "/tmp/ingest_log.db")
_lock = threading.Lock()


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
    with _lock, sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute(
                "INSERT INTO ingest_log (idempotency_key, checksum, dedupe_count) VALUES (?, ?, 1)",
                (idempotency_key, checksum),
            )
            conn.commit()
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
            return dedupe_count
