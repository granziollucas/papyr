"""Pipeline orchestration (skeleton)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from papyr.core.dedup import find_duplicates
from papyr.core.export_csv import export_csv
from papyr.core.models import PaperRecord, ProviderState, RawRecord, SearchQuery
from papyr.core.normalize import normalize_generic
from papyr.core.state import db, repo
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


def run_metasearch(
    query: SearchQuery,
    providers: Iterable,
    config: dict[str, str],
) -> list[PaperRecord]:
    """Run sequential provider searches with persistence and CSV export."""
    output_dir = Path(query.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    params_path = output_dir / "search_params.json"
    params_path.write_text(query.model_dump_json(indent=2), encoding="utf-8")

    query_hash = stable_hash(query.model_dump())
    conn = db.connect(output_dir / "state.sqlite")
    db.init_db(conn)

    run_row = repo.get_run_by_hash(conn, query_hash)
    run_id = run_row["id"] if run_row else repo.create_run(conn, query_hash, query.model_dump())

    all_records: list[PaperRecord] = []
    record_row_ids: dict[int, int] = {}

    for provider in providers:
        if provider.requires_credentials and not provider.is_configured(config):
            continue
        state = repo.get_provider_state(conn, run_id, provider.name) or ProviderState()
        for raw in provider.search(query, state):
            record = provider.normalize(raw)
            record.query_hash = query_hash
            record.retrieved_at = now_iso()
            all_records.append(record)
            row_id = repo.insert_record(conn, run_id, provider.name, raw, record)
            record_row_ids[id(record)] = row_id
        repo.upsert_provider_state(conn, run_id, provider.name, state)

    canonical, duplicates = deduplicate(all_records)
    for duplicate, canonical_record, _reason in duplicates:
        duplicate_of = canonical_record.id or canonical_record.url
        if duplicate_of:
            duplicate.duplicate_of = duplicate_of
            row_id = record_row_ids.get(id(duplicate))
            if row_id:
                repo.mark_duplicate(conn, row_id, duplicate_of)

    export_results(canonical, output_dir)
    _export_duplicates(duplicates, output_dir)
    return canonical


def _export_duplicates(
    duplicates: list[tuple[PaperRecord, PaperRecord, str]],
    output_dir: Path,
) -> None:
    if not duplicates:
        return
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = now_iso().replace(":", "").replace("+", "")
    path = logs_dir / f"duplicates_{timestamp}.csv"
    with path.open("w", encoding="latin1", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["DuplicateTitle", "DuplicateID", "CanonicalTitle", "CanonicalID", "Reason"])
        for duplicate, canonical, reason in duplicates:
            writer.writerow([duplicate.title, duplicate.id, canonical.title, canonical.id, reason])
