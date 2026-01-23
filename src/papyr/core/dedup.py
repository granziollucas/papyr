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


def normalize_authors(authors: str) -> str:
    """Normalize authors string for dedup comparison."""
    simplified = _PUNCT.sub("", authors or "")
    simplified = " ".join(simplified.split())
    return simplified.casefold()


def _is_preprint(record: PaperRecord) -> bool:
    return record.type.strip().lower() == "preprint" or record.origin.strip().lower() == "arxiv"


def find_duplicates(records: Iterable[PaperRecord]) -> list[tuple[PaperRecord, PaperRecord, str]]:
    """Return list of duplicates as (duplicate, canonical, reason)."""
    by_key: dict[tuple[str, str], PaperRecord] = {}
    duplicates: list[tuple[PaperRecord, PaperRecord, str]] = []
    duplicate_ids: set[int] = set()
    by_title: dict[str, list[PaperRecord]] = {}
    for record in records:
        title_key = normalize_title(record.title)
        id_key = (record.id or "").strip().casefold()
        key = (title_key, id_key)
        if title_key:
            by_title.setdefault(title_key, []).append(record)
        if not title_key or not id_key:
            continue
        if key not in by_key:
            by_key[key] = record
            continue
        canonical = by_key[key]
        if canonical.origin.lower() != "crossref" and record.origin.lower() == "crossref":
            by_key[key] = record
            duplicates.append((canonical, record, "title+id match (crossref canonical)"))
            duplicate_ids.add(id(canonical))
        else:
            duplicates.append((record, canonical, "title+id match"))
            duplicate_ids.add(id(record))
    for title_key, group in by_title.items():
        if len(group) < 2:
            continue
        published = [r for r in group if not _is_preprint(r)]
        preprints = [r for r in group if _is_preprint(r)]
        if not published or not preprints:
            continue
        preferred = None
        for candidate in published:
            if candidate.origin.strip().lower() == "crossref":
                preferred = candidate
                break
        if not preferred:
            preferred = published[0]
        canonical_authors = normalize_authors(preferred.authors)
        if not canonical_authors:
            continue
        for preprint in preprints:
            if id(preprint) in duplicate_ids:
                continue
            if normalize_authors(preprint.authors) != canonical_authors:
                continue
            duplicates.append((preprint, preferred, "title+authors match (drop preprint)"))
            duplicate_ids.add(id(preprint))
    return duplicates
