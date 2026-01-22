"""Hashing helpers."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_hash(payload: dict[str, Any]) -> str:
    """Create a stable SHA-256 hash from a JSON-serializable payload."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
