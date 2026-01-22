"""Pipeline orchestration (skeleton)."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from papyr.core.dedup import find_duplicates
from papyr.core.export_csv import export_csv
from papyr.core.models import PaperRecord, ProviderState, RawRecord, SearchQuery
from papyr.core.normalize import normalize_generic
from papyr.util.hashing import stable_hash
from papyr.util.time import now_iso


def normalize_records(records: Iterable[RawRecord]) -> list[PaperRecord]:
    """Normalize raw records with a generic fallback."""
    normalized: list[PaperRecord] = []
    for raw in records:
        record = normalize_generic(raw)
        normalized.append(record)
    return normalized


def apply_metadata(records: list[PaperRecord], query: SearchQuery) -> list[PaperRecord]:
    """Attach query hash and retrieved timestamp."""
    query_hash = stable_hash(query.model_dump())
    for record in records:
        record.query_hash = query_hash
        record.retrieved_at = now_iso()
    return records


def export_results(records: list[PaperRecord], output_dir: Path) -> Path:
    """Export results.csv and return its path."""
    path = output_dir / "results.csv"
    export_csv(records, path)
    return path


def deduplicate(records: list[PaperRecord]) -> tuple[list[PaperRecord], list[tuple[PaperRecord, PaperRecord, str]]]:
    """Return canonical records and duplicate pairs."""
    duplicates = find_duplicates(records)
    duplicate_ids = {id(dup[0]) for dup in duplicates}
    canonical = [record for record in records if id(record) not in duplicate_ids]
    return canonical, duplicates


def run_search(query: SearchQuery, providers: Iterable) -> list[PaperRecord]:
    """Run a basic search across providers (sequential, no persistence yet)."""
    all_records: list[PaperRecord] = []
    for provider in providers:
        state = ProviderState()
        for raw in provider.search(query, state):
            record = provider.normalize(raw)
            all_records.append(record)
    return all_records
