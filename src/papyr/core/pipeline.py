"""Pipeline orchestration (skeleton)."""

from __future__ import annotations

import csv
import json
import traceback
from pathlib import Path
from typing import Iterable

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeRemainingColumn

from papyr.core.dedup import find_duplicates
from papyr.core.downloader import download_pdf
from papyr.core.export_csv import export_csv
from papyr.core.models import PaperRecord, ProviderState, RawRecord, SearchQuery
from papyr.core.normalize import normalize_generic
from papyr.core.state import db, repo
from papyr.util.control import read_control_command, wait_if_paused, clear_control_command
from papyr.util.fs import safe_filename
from papyr.util.hashing import stable_hash
from papyr.util.logging import setup_file_logger
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
    console: Console | None = None,
) -> list[PaperRecord]:
    """Run sequential provider searches with persistence and CSV export."""
    console = console or Console()
    output_dir = Path(query.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    params_path = output_dir / "search_params.json"
    params_path.write_text(query.model_dump_json(indent=2), encoding="utf-8")

    query_hash = stable_hash(query.model_dump())
    if not query.extra:
        query.extra = {}
    if config.get("CROSSREF_EMAIL"):
        query.extra["crossref_email"] = config.get("CROSSREF_EMAIL", "")
    if config.get("CROSSREF_USER_AGENT"):
        query.extra["crossref_user_agent"] = config.get("CROSSREF_USER_AGENT", "")
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_stamp = now_iso().replace(":", "").replace("+", "")
    log_path = logs_dir / f"run_{log_stamp}.log"
    error_path = logs_dir / f"errors_{log_stamp}.jsonl"
    logger = setup_file_logger(log_path)

    conn = db.connect(output_dir / "state.sqlite")
    db.init_db(conn)

    run_row = repo.get_run_by_hash(conn, query_hash)
    run_id = run_row["id"] if run_row else repo.create_run(conn, query_hash, query.model_dump())

    existing_ids = repo.list_record_ids(conn, run_id)
    all_records: list[PaperRecord] = []
    record_row_ids: dict[int, int] = {}
    control_path = output_dir / ".papyr_control"

    total = query.limit if query.limit is not None else None
    progress_columns = [
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TaskProgressColumn(show_speed=True),
        TimeRemainingColumn(),
    ]
    with Progress(*progress_columns, console=console) as progress:
        task_id = progress.add_task("Searching", total=total)
        for provider in providers:
            if not provider.is_configured(config):
                continue
            progress.update(task_id, description=f"Searching {provider.name}")
            cmd = read_control_command(control_path)
            if cmd == "STOP":
                clear_control_command(control_path)
                break
            if cmd == "PAUSE":
                if not wait_if_paused(control_path):
                    break
            state = repo.get_provider_state(conn, run_id, provider.name) or ProviderState()
            try:
                for raw in provider.search(query, state):
                    progress.advance(task_id, 1)
                    cmd = read_control_command(control_path)
                    if cmd == "STOP":
                        clear_control_command(control_path)
                        break
                    if cmd == "PAUSE":
                        if not wait_if_paused(control_path):
                            break
                    if raw.record_id and raw.record_id in existing_ids:
                        continue
                    record = provider.normalize(raw)
                    record.query_hash = query_hash
                    record.retrieved_at = now_iso()
                    all_records.append(record)
                    row_id = repo.insert_record(conn, run_id, provider.name, raw, record)
                    record_row_ids[id(record)] = row_id
                    if raw.record_id:
                        existing_ids.add(raw.record_id)
                    if query.download_pdfs and not query.dry_run:
                        urls = provider.get_official_urls(record)
                        pdf_url = urls.get("pdf_url") if urls else None
                        if pdf_url:
                            filename = safe_filename(record.title, record.id or record.url)
                            dest = output_dir / "files" / filename
                            result = download_pdf(pdf_url, dest)
                            status = "ok" if result.ok else "failed"
                            repo.upsert_download(
                                conn,
                                run_id,
                                record.id or None,
                                pdf_url,
                                str(dest) if result.ok else None,
                                status,
                                result.attempts,
                                None if result.ok else result.message,
                            )
            except Exception as exc:  # noqa: BLE001 - log and continue per resilience requirements
                message = str(exc) or "Provider search failed."
                stack = traceback.format_exc()
                repo.log_failure(
                    conn,
                    run_id,
                    provider.name,
                    "search",
                    message,
                    type(exc).__name__,
                    stack,
                    None,
                )
                _append_error_jsonl(
                    error_path,
                    provider.name,
                    "search",
                    message,
                    type(exc).__name__,
                    stack,
                )
                logger.exception("Provider search failed: %s", provider.name)
                print(f"An error occurred. Please check the log at: {log_path}")
            repo.upsert_provider_state(conn, run_id, provider.name, state)

    all_rows = repo.list_records(conn, run_id)
    all_records = []
    record_row_ids = {}
    for row in all_rows:
        record = PaperRecord.model_validate_json(row["normalized_json"])
        all_records.append(record)
        record_row_ids[id(record)] = int(row["id"])

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
        writer = csv.writer(handle, quoting=csv.QUOTE_ALL)
        writer.writerow(["DuplicateTitle", "DuplicateID", "CanonicalTitle", "CanonicalID", "Reason"])
        for duplicate, canonical, reason in duplicates:
            writer.writerow([duplicate.title, duplicate.id, canonical.title, canonical.id, reason])


def _append_error_jsonl(
    path: Path,
    provider: str,
    stage: str,
    message: str,
    exception_type: str,
    stacktrace: str,
) -> None:
    record = {
        "timestamp": now_iso(),
        "provider": provider,
        "stage": stage,
        "message": message,
        "exception_type": exception_type,
        "stacktrace": stacktrace,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")
