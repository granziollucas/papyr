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


def get_run_by_hash(conn: sqlite3.Connection, query_hash: str) -> sqlite3.Row | None:
    """Fetch a run row by query hash."""
    cur = conn.execute(
        "SELECT * FROM runs WHERE query_hash=? ORDER BY id DESC LIMIT 1",
        (query_hash,),
    )
    return cur.fetchone()


def get_provider_state(
    conn: sqlite3.Connection, run_id: int, provider: str
) -> ProviderState | None:
    """Fetch provider state if available."""
    cur = conn.execute(
        "SELECT * FROM provider_state WHERE run_id=? AND provider=?",
        (run_id, provider),
    )
    row = cur.fetchone()
    if not row:
        return None
    extra = json.loads(row["extra_json"]) if row["extra_json"] else {}
    return ProviderState(
        cursor=row["cursor"],
        last_request_time=row["last_request_time"],
        extra=extra,
    )


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


def insert_record(
    conn: sqlite3.Connection,
    run_id: int,
    provider: str,
    raw: RawRecord,
    normalized: PaperRecord,
    is_duplicate: bool = False,
    duplicate_of: str | None = None,
) -> int:
    """Insert a record (no merge)."""
    cur = conn.execute(
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
    return int(cur.lastrowid)


def list_records(conn: sqlite3.Connection, run_id: int) -> list[sqlite3.Row]:
    """Return all records for a run."""
    cur = conn.execute(
        "SELECT * FROM records WHERE run_id=? ORDER BY id",
        (run_id,),
    )
    return list(cur.fetchall())


def list_record_ids(conn: sqlite3.Connection, run_id: int) -> set[str]:
    """Return record IDs already stored for a run."""
    cur = conn.execute(
        "SELECT record_id FROM records WHERE run_id=? AND record_id IS NOT NULL",
        (run_id,),
    )
    return {row["record_id"] for row in cur.fetchall() if row["record_id"]}


def mark_duplicate(
    conn: sqlite3.Connection,
    record_row_id: int,
    duplicate_of: str,
) -> None:
    """Mark a record as duplicate."""
    conn.execute(
        "UPDATE records SET is_duplicate=1, duplicate_of=?, updated_at=? WHERE id=?",
        (duplicate_of, now_iso(), record_row_id),
    )
    conn.commit()


def upsert_download(
    conn: sqlite3.Connection,
    run_id: int,
    record_id: str | None,
    pdf_url: str,
    file_path: str | None,
    status: str,
    attempts: int,
    last_error: str | None = None,
) -> None:
    """Insert a download row."""
    conn.execute(
        """
        INSERT INTO downloads (run_id, record_id, pdf_url, file_path, status, attempts, last_error, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (run_id, record_id, pdf_url, file_path, status, attempts, last_error, now_iso()),
    )
    conn.commit()


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
