"""Filesystem helpers."""

from __future__ import annotations

import hashlib
import re

_INVALID = re.compile(r'[<>:"/\\\\|?*]')


def safe_filename(title: str, suffix_source: str) -> str:
    """Create a safe PDF filename with a short suffix."""
    base = (title or "document").strip().replace(" ", "_")
    base = _INVALID.sub("", base)
    base = re.sub(r"_+", "_", base)
    base = base.strip("._")
    suffix = _short_id(suffix_source or base)
    if not base:
        base = "document"
    filename = f"{base}_{suffix}.pdf"
    return filename[:200]


def _short_id(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return digest[:8]
