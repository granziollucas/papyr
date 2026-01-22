"""Deduplication helpers."""

from __future__ import annotations

import re
from typing import Iterable

from papyr.core.models import PaperRecord

_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)


def normalize_title(title: str) -> str:
    """Normalize titles for dedup comparison."""
    simplified = _PUNCT.sub("", title or "")
    simplified = " ".join(simplified.split())
    return simplified.casefold()


def find_duplicates(records: Iterable[PaperRecord]) -> list[tuple[PaperRecord, PaperRecord, str]]:
    """Return list of duplicates as (duplicate, canonical, reason)."""
    by_key: dict[tuple[str, str], PaperRecord] = {}
    duplicates: list[tuple[PaperRecord, PaperRecord, str]] = []
    for record in records:
        title_key = normalize_title(record.title)
        id_key = (record.id or "").strip().casefold()
        key = (title_key, id_key)
        if not title_key or not id_key:
            continue
        if key not in by_key:
            by_key[key] = record
            continue
        canonical = by_key[key]
        if canonical.origin.lower() != "crossref" and record.origin.lower() == "crossref":
            by_key[key] = record
            duplicates.append((canonical, record, "title+id match (crossref canonical)"))
        else:
            duplicates.append((record, canonical, "title+id match"))
    return duplicates
