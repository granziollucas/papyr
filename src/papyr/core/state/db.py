"""SQLite access helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(db_path: Path) -> sqlite3.Connection:
    """Create a SQLite connection with row factory."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Initialize database schema."""
    schema_path = Path(__file__).with_name("schema.sql")
    schema_sql = schema_path.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()
