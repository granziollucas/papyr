"""Pipeline orchestration (skeleton)."""

from __future__ import annotations

import csv
import json
import threading
import time
import traceback
from pathlib import Path
from typing import Iterable

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeRemainingColumn

from papyr.core.dedup import find_duplicates
from papyr.core.downloader import download_pdf
from papyr.core.export_csv import export_csv
from papyr.core.export_tsv import export_tsv
from papyr.core.models import PaperRecord, ProviderState, RawRecord, SearchQuery
from papyr.core.normalize import normalize_generic
from papyr.core.state import db, repo
from papyr.util.control import KeyboardControl, poll_control, wait_if_paused
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


def export_results(records: list[PaperRecord], output_dir: Path, output_format: str) -> Path:
    """Export results in the requested format and return its path."""
    if output_format == "tsv":
        path = output_dir / "results.tsv"
        export_tsv(records, path)
        return path
    path = output_dir / "results.csv"
    export_csv(records, path)
    return path


def append_results(records: list[PaperRecord], output_dir: Path, output_format: str) -> Path:
    """Append results in the requested format and return its path."""
    if output_format == "tsv":
        path = output_dir / "results.tsv"
        export_tsv(records, path, append=True)
        return path
    path = output_dir / "results.csv"
    export_csv(records, path, append=True)
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
    resume_run_id: int | None = None,
    max_new: int | None = None,
    append_new_only: bool = False,
) -> tuple[list[PaperRecord], str]:
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

    if resume_run_id is not None:
        run_id = resume_run_id
    else:
        run_row = repo.get_run_by_hash(conn, query_hash)
        run_id = run_row["id"] if run_row else repo.create_run(conn, query_hash, query.model_dump())

    existing_ids = repo.list_record_ids(conn, run_id)
    downloaded_ids = repo.list_downloaded_ids(conn, run_id)
    all_records: list[PaperRecord] = []
    record_row_ids: dict[int, int] = {}
    new_row_ids: set[int] = set()
    control_path = output_dir / ".papyr_control"
    keyboard = KeyboardControl()
    keyboard.start()
    stop_requested = False
    exit_reason = "completed"
    new_count = 0

    total = max_new if max_new is not None else query.limit
    progress_columns = [
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TaskProgressColumn(show_speed=True),
        TimeRemainingColumn(),
    ]
    try:
        with Progress(*progress_columns, console=console) as progress:
            task_id = progress.add_task("Searching", total=total)
            if query.parallel_providers:
                (
                    stop_requested,
                    exit_reason,
                    new_row_ids,
                    existing_ids,
                    downloaded_ids,
                ) = _run_parallel_providers(
                    progress,
                    task_id,
                    providers,
                    query,
                    query_hash,
                    config,
                    output_dir,
                    control_path,
                    keyboard,
                    run_id,
                    max_new,
                    existing_ids,
                    downloaded_ids,
                    error_path,
                    log_path,
                )
            else:
                stop_requested, exit_reason, new_row_ids = _run_sequential_providers(
                    progress,
                    task_id,
                    providers,
                    query,
                    query_hash,
                    config,
                    output_dir,
                    control_path,
                    keyboard,
                    run_id,
                    max_new,
                    existing_ids,
                    downloaded_ids,
                    error_path,
                    log_path,
                )
    finally:
        keyboard.stop()

    all_rows = repo.list_records(conn, run_id)
    all_records = []
    record_row_ids = {}
    row_id_to_record: dict[int, PaperRecord] = {}
    for row in all_rows:
        record = PaperRecord.model_validate_json(row["normalized_json"])
        all_records.append(record)
        record_row_ids[id(record)] = int(row["id"])
        row_id_to_record[int(row["id"])] = record

    canonical, duplicates = deduplicate(all_records)
    for duplicate, canonical_record, _reason in duplicates:
        duplicate_of = canonical_record.id or canonical_record.url
        if duplicate_of:
            duplicate.duplicate_of = duplicate_of
            row_id = record_row_ids.get(id(duplicate))
            if row_id:
                repo.mark_duplicate(conn, row_id, duplicate_of)

    if append_new_only:
        new_canonical = [
            record
            for record in canonical
            if record_row_ids.get(id(record)) in new_row_ids
        ]
        if new_canonical:
            append_results(new_canonical, output_dir, query.output_format)
    else:
        export_results(canonical, output_dir, query.output_format)
    _export_duplicates(duplicates, output_dir)
    return canonical, exit_reason


def _run_sequential_providers(
    progress: Progress,
    task_id: int,
    providers: Iterable,
    query: SearchQuery,
    query_hash: str,
    config: dict[str, str],
    output_dir: Path,
    control_path: Path,
    keyboard: KeyboardControl,
    run_id: int,
    max_new: int | None,
    existing_ids: set[str],
    downloaded_ids: set[str],
    error_path: Path,
    log_path: Path,
) -> tuple[bool, str, set[int]]:
    stop_requested = False
    exit_reason = "completed"
    new_count = 0
    new_row_ids: set[int] = set()
    conn = db.connect(output_dir / "state.sqlite")
    db.init_db(conn)
    logger = setup_file_logger(log_path)
    for provider in providers:
        if not provider.is_configured(config):
            continue
        status = "Running"
        progress.update(task_id, description=f"Searching {provider.name} [{status}]")
        cmd = poll_control(control_path, keyboard)
        if cmd == "STOP":
            stop_requested = True
            exit_reason = "stopped"
            break
        if cmd == "SAVE_EXIT":
            stop_requested = True
            exit_reason = "save_exit"
            break
        if cmd == "PAUSE":
            status = "Paused"
            progress.update(task_id, description=f"Searching {provider.name} [{status}]")
            pause_result = wait_if_paused(control_path, keyboard)
            if pause_result != "resume":
                stop_requested = True
                exit_reason = "save_exit" if pause_result == "save_exit" else "stopped"
                break
            status = "Running"
            progress.update(task_id, description=f"Searching {provider.name} [{status}]")
        state = repo.get_provider_state(conn, run_id, provider.name) or ProviderState()
        try:
            for raw in provider.search(query, state):
                progress.advance(task_id, 1)
                cmd = poll_control(control_path, keyboard)
                if cmd == "STOP":
                    stop_requested = True
                    exit_reason = "stopped"
                    break
                if cmd == "SAVE_EXIT":
                    stop_requested = True
                    exit_reason = "save_exit"
                    break
                if cmd == "PAUSE":
                    status = "Paused"
                    progress.update(task_id, description=f"Searching {provider.name} [{status}]")
                    pause_result = wait_if_paused(control_path, keyboard)
                    if pause_result != "resume":
                        stop_requested = True
                        exit_reason = "save_exit" if pause_result == "save_exit" else "stopped"
                        break
                    status = "Running"
                    progress.update(task_id, description=f"Searching {provider.name} [{status}]")
                if raw.record_id and raw.record_id in existing_ids:
                    continue
                record = provider.normalize(raw)
                record.query_hash = query_hash
                record.retrieved_at = now_iso()
                row_id = repo.insert_record(conn, run_id, provider.name, raw, record)
                new_row_ids.add(row_id)
                if raw.record_id:
                    existing_ids.add(raw.record_id)
                new_count += 1
                if query.download_pdfs and not query.dry_run:
                    urls = provider.get_official_urls(record)
                    pdf_url = urls.get("pdf_url") if urls else None
                    if pdf_url:
                        filename = safe_filename(record.title, record.id or record.url)
                        dest = output_dir / "files" / filename
                        if record.id and record.id in downloaded_ids:
                            continue
                        if dest.exists():
                            repo.upsert_download(
                                conn,
                                run_id,
                                record.id or None,
                                pdf_url,
                                str(dest),
                                "ok",
                                0,
                                None,
                            )
                            if record.id:
                                downloaded_ids.add(record.id)
                            continue
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
                        if result.ok and record.id:
                            downloaded_ids.add(record.id)
                if max_new is not None and new_count >= max_new:
                    stop_requested = True
                    exit_reason = "completed"
                    break
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
        if stop_requested:
            break
    return stop_requested, exit_reason, new_row_ids


def _run_parallel_providers(
    progress: Progress,
    task_id: int,
    providers: Iterable,
    query: SearchQuery,
    query_hash: str,
    config: dict[str, str],
    output_dir: Path,
    control_path: Path,
    keyboard: KeyboardControl,
    run_id: int,
    max_new: int | None,
    existing_ids: set[str],
    downloaded_ids: set[str],
    error_path: Path,
    log_path: Path,
) -> tuple[bool, str, set[int], set[str], set[str]]:
    status = "Running"
    progress.update(task_id, description=f"Searching providers [{status}]")
    ids_lock = threading.Lock()
    db_lock = threading.Lock()
    progress_lock = threading.Lock()
    new_row_ids: set[int] = set()
    stop_event = threading.Event()
    pause_event = threading.Event()
    pause_event.set()
    exit_reason = {"value": "completed"}
    new_count = {"value": 0}
    logger = setup_file_logger(log_path)
    providers_list = [p for p in providers if p.is_configured(config)]

    def control_loop() -> None:
        last_status = "Running"
        while not stop_event.is_set():
            cmd = poll_control(control_path, keyboard)
            if cmd == "PAUSE":
                pause_event.clear()
                if last_status != "Paused":
                    with progress_lock:
                        progress.update(task_id, description="Searching providers [Paused]")
                    last_status = "Paused"
            elif cmd == "RESUME":
                pause_event.set()
                if last_status != "Running":
                    with progress_lock:
                        progress.update(task_id, description="Searching providers [Running]")
                    last_status = "Running"
            elif cmd == "STOP":
                exit_reason["value"] = "stopped"
                stop_event.set()
                pause_event.set()
                break
            elif cmd == "SAVE_EXIT":
                exit_reason["value"] = "save_exit"
                stop_event.set()
                pause_event.set()
                break
            time.sleep(0.2)

    def provider_worker(provider) -> None:
        conn = db.connect(output_dir / "state.sqlite")
        db.init_db(conn)
        state = repo.get_provider_state(conn, run_id, provider.name) or ProviderState()
        try:
            for raw in provider.search(query, state):
                if stop_event.is_set():
                    break
                pause_event.wait()
                with progress_lock:
                    progress.advance(task_id, 1)
                with ids_lock:
                    if raw.record_id and raw.record_id in existing_ids:
                        continue
                record = provider.normalize(raw)
                record.query_hash = query_hash
                record.retrieved_at = now_iso()
                with db_lock:
                    row_id = repo.insert_record(conn, run_id, provider.name, raw, record)
                    new_row_ids.add(row_id)
                with ids_lock:
                    if raw.record_id:
                        existing_ids.add(raw.record_id)
                with ids_lock:
                    new_count["value"] += 1
                    reached_limit = max_new is not None and new_count["value"] >= max_new
                if query.download_pdfs and not query.dry_run:
                    urls = provider.get_official_urls(record)
                    pdf_url = urls.get("pdf_url") if urls else None
                    if pdf_url:
                        filename = safe_filename(record.title, record.id or record.url)
                        dest = output_dir / "files" / filename
                        with ids_lock:
                            already_downloaded = bool(record.id and record.id in downloaded_ids)
                        if already_downloaded:
                            pass
                        elif dest.exists():
                            with db_lock:
                                repo.upsert_download(
                                    conn,
                                    run_id,
                                    record.id or None,
                                    pdf_url,
                                    str(dest),
                                    "ok",
                                    0,
                                    None,
                                )
                            if record.id:
                                with ids_lock:
                                    downloaded_ids.add(record.id)
                        else:
                            result = download_pdf(pdf_url, dest)
                            status = "ok" if result.ok else "failed"
                            with db_lock:
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
                            if result.ok and record.id:
                                with ids_lock:
                                    downloaded_ids.add(record.id)
                if reached_limit:
                    stop_event.set()
                    break
        except Exception as exc:  # noqa: BLE001 - log and continue per resilience requirements
            message = str(exc) or "Provider search failed."
            stack = traceback.format_exc()
            with db_lock:
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
        with db_lock:
            repo.upsert_provider_state(conn, run_id, provider.name, state)

    control_thread = threading.Thread(target=control_loop, name="papyr-control", daemon=True)
    control_thread.start()
    threads = [
        threading.Thread(target=provider_worker, args=(provider,), daemon=True)
        for provider in providers_list
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    stop_event.set()
    return stop_event.is_set(), exit_reason["value"], new_row_ids, existing_ids, downloaded_ids


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
