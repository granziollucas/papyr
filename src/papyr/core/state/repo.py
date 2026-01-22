"""Repository helpers for state persistence."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from papyr.core.models import PaperRecord, ProviderState, RawRecord
from papyr.util.time import now_iso


def create_run(conn: sqlite3.Connection, query_hash: str, params: dict[str, Any]) -> int:
    """Create a run row and return run_id."""
    cur = conn.execute(
        "INSERT INTO runs (query_hash, params_json, created_at) VALUES (?, ?, ?)",
        (query_hash, json.dumps(params, ensure_ascii=True), now_iso()),
    )
    conn.commit()
    return int(cur.lastrowid)


def upsert_provider_state(
    conn: sqlite3.Connection,
    run_id: int,
    provider: str,
    state: ProviderState,
) -> None:
    """Insert or update provider state."""
    conn.execute(
        """
        INSERT INTO provider_state (run_id, provider, cursor, last_request_time, extra_json)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(run_id, provider) DO UPDATE SET
            cursor=excluded.cursor,
            last_request_time=excluded.last_request_time,
            extra_json=excluded.extra_json
        """,
        (
            run_id,
            provider,
            state.cursor,
            state.last_request_time,
            json.dumps(state.extra, ensure_ascii=True),
        ),
    )
    conn.commit()


def upsert_record(
    conn: sqlite3.Connection,
    run_id: int,
    provider: str,
    raw: RawRecord,
    normalized: PaperRecord,
    is_duplicate: bool = False,
    duplicate_of: str | None = None,
) -> None:
    """Insert a record (no merge)."""
    conn.execute(
        """
        INSERT INTO records (
            run_id, provider, record_id, normalized_json, raw_json,
            is_duplicate, duplicate_of, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            provider,
            raw.record_id,
            normalized.model_dump_json(),
            raw.model_dump_json(),
            1 if is_duplicate else 0,
            duplicate_of,
            now_iso(),
            now_iso(),
        ),
    )
    conn.commit()


def list_records(conn: sqlite3.Connection, run_id: int) -> list[sqlite3.Row]:
    """Return all records for a run."""
    cur = conn.execute(
        "SELECT * FROM records WHERE run_id=? ORDER BY id",
        (run_id,),
    )
    return list(cur.fetchall())


def log_failure(
    conn: sqlite3.Connection,
    run_id: int,
    provider: str,
    stage: str,
    message: str,
    exception_type: str | None = None,
    stacktrace: str | None = None,
    record_id: str | None = None,
) -> None:
    """Insert a failure row."""
    conn.execute(
        """
        INSERT INTO failures (
            run_id, provider, stage, message, exception_type, stacktrace, record_id, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (run_id, provider, stage, message, exception_type, stacktrace, record_id, now_iso()),
    )
    conn.commit()
