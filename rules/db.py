"""Light-weight SQLite helpers for persisting rules and action outcomes."""
from __future__ import annotations

import os
import sqlite3
import threading
import time
from typing import Iterable, List, Optional, Sequence

DB_PATH = os.getenv("RULES_DB", "/tmp/rules.db")
_lock = threading.Lock()


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                definition TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS action_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id INTEGER NOT NULL,
                dedupe_key TEXT NOT NULL,
                dedupe_count INTEGER NOT NULL,
                next_run_at REAL NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        conn.commit()


def save_rule(name: str, definition: str) -> int:
    """Persist a rule definition and return its ID.

    If a rule with the same name already exists its identifier is returned and
    the definition is left untouched.  This allows callers to repeatedly store
    rules without creating duplicates, which is useful for idempotent rule
    evaluation during testing.
    """
    with _lock, sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT id FROM rule WHERE name=?", (name,))
        row = cur.fetchone()
        if row is not None:
            return int(row[0])
        cur = conn.execute(
            "INSERT INTO rule (name, definition) VALUES (?, ?)",
            (name, definition),
        )
        conn.commit()
        return int(cur.lastrowid)


def log_action(rule_id: int, dedupe_key: str, escalation: Sequence[int]) -> bool:
    """Record an action attempt respecting deduplication and escalation timers.

    Returns ``True`` if the action should be executed, ``False`` if it should be
    suppressed because the deduplication window has not yet expired.
    """
    now = time.time()
    with _lock, sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT id, dedupe_count, next_run_at FROM action_log WHERE rule_id=? AND dedupe_key=?",
            (rule_id, dedupe_key),
        )
        row = cur.fetchone()
        if row is None:
            delay = escalation[0] if escalation else 0
            next_run = now + delay
            conn.execute(
                "INSERT INTO action_log (rule_id, dedupe_key, dedupe_count, next_run_at, created_at) VALUES (?, ?, 1, ?, ?)",
                (rule_id, dedupe_key, next_run, now),
            )
            conn.commit()
            return True
        log_id, count, next_run_at = row
        if now < next_run_at:
            return False
        count += 1
        delay = escalation[min(count - 1, len(escalation) - 1)] if escalation else 0
        next_run_at = now + delay
        conn.execute(
            "UPDATE action_log SET dedupe_count=?, next_run_at=?, created_at=? WHERE id=?",
            (count, next_run_at, now, log_id),
        )
        conn.commit()
        return True
