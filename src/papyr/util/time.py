"""Time helpers."""

from __future__ import annotations

from datetime import datetime, timezone


def now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
