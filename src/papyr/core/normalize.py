"""Normalization helpers."""

from __future__ import annotations

from typing import Any

from papyr.core.models import PaperRecord, RawRecord


def _first(value: Any) -> str:
    if isinstance(value, list):
        return str(value[0]) if value else ""
    if value is None:
        return ""
    return str(value)


def normalize_generic(raw: RawRecord) -> PaperRecord:
    """Best-effort normalization for provider records.

    Providers can override this with richer mapping.
    """
    data = raw.data
    title = _first(data.get("title"))
    abstract = _first(data.get("abstract"))
    authors = _first(data.get("authors"))
    publisher = _first(data.get("publisher"))
    year = ""
    if isinstance(data.get("year"), int):
        year = str(data.get("year"))
    return PaperRecord(
        authors=str(authors),
        title=str(title),
        abstract=str(abstract),
        origin=raw.provider,
        publisher=str(publisher),
        year=year,
        id=raw.record_id or "",
    )
