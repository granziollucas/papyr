"""Wizard flows for interactive CLI."""

from __future__ import annotations

import os
from pathlib import Path

from rich.console import Console
import typer

from papyr.adapters import default_providers
from papyr.adapters.crossref import CrossrefProvider
from papyr.adapters.ssrn import SsrnProvider
from papyr.cli import prompts
from papyr.core.models import PaperRecord, SearchQuery
from papyr.core.pipeline import run_metasearch
from papyr.core.state import db, repo
from papyr.core.downloader import download_pdf
from papyr.util.fs import safe_filename
from papyr.util.hashing import stable_hash
from papyr.util.config import DEFAULT_ENV_PATH, load_env_file, set_env_value


def _configure_crossref(console: Console, env_path: str = str(DEFAULT_ENV_PATH)) -> None:
    console.print("Crossref polite setup")
    email = typer.prompt("Contact email for Crossref polite requests", default="")
    if not email:
        set_env_value(Path(env_path), "CROSSREF_ENABLED", "0")
        console.print("Crossref disabled. You can configure it later.")
        return
    set_env_value(Path(env_path), "CROSSREF_EMAIL", email)
    user_agent = typer.prompt("Optional User-Agent (press enter to skip)", default="")
    if user_agent:
        set_env_value(Path(env_path), "CROSSREF_USER_AGENT", user_agent)
    set_env_value(Path(env_path), "CROSSREF_ENABLED", "1")


def _configure_ssrn(console: Console, env_path: str = str(DEFAULT_ENV_PATH)) -> None:
    console.print("SSRN setup (disabled by default)")
    enable = typer.confirm(
        "Do you have SSRN API or feed access and accept SSRN terms?",
        default=False,
    )
    if not enable:
        set_env_value(Path(env_path), "SSRN_ENABLED", "0")
        console.print("SSRN disabled.")
        return
    set_env_value(Path(env_path), "SSRN_ENABLED", "1")
    feed_url = typer.prompt("SSRN feed URL (leave blank if not applicable)", default="")
    if feed_url:
        set_env_value(Path(env_path), "SSRN_FEED_URL", feed_url)


def run_init_wizard(console: Console) -> None:
    """Run credential setup wizard."""
    console.print(prompts.INIT_TITLE)
    _configure_crossref(console)
    _configure_ssrn(console)


def _configure_missing_providers(console: Console) -> None:
    config = load_env_file(DEFAULT_ENV_PATH)
    providers = default_providers()
    for provider in providers:
        if provider.requires_credentials and not provider.is_configured(config):
            if isinstance(provider, CrossrefProvider):
                if typer.confirm("Crossref is not configured. Configure now?", default=True):
                    _configure_crossref(console)
                else:
                    set_env_value(DEFAULT_ENV_PATH, "CROSSREF_ENABLED", "0")
            config = load_env_file(DEFAULT_ENV_PATH)
        if isinstance(provider, SsrnProvider) and not provider.is_configured(config):
            if typer.confirm("SSRN is disabled (optional). Configure now?", default=False):
                _configure_ssrn(console)
                config = load_env_file(DEFAULT_ENV_PATH)


def run_bootstrap(console: Console) -> None:
    """Check credentials and optionally configure missing providers."""
    console.print(prompts.BOOTSTRAP_TITLE)
    if typer.confirm(prompts.BOOTSTRAP_SKIP_PROMPT, default=False):
        console.print("Skipped credential setup.")
        return
    _configure_missing_providers(console)
    console.print("Credential check complete.")


def run_new_wizard(console: Console) -> None:
    """Run new search wizard."""
    console.print(prompts.NEW_TITLE)
    config = load_env_file(DEFAULT_ENV_PATH)
    providers = default_providers()
    for provider in providers:
        if isinstance(provider, CrossrefProvider) and not provider.is_configured(config):
            if typer.confirm("Crossref is not configured. Configure now?", default=True):
                _configure_crossref(console)
                config = load_env_file(DEFAULT_ENV_PATH)
            else:
                set_env_value(DEFAULT_ENV_PATH, "CROSSREF_ENABLED", "0")
        if isinstance(provider, SsrnProvider) and not provider.is_configured(config):
            if typer.confirm("SSRN is not configured. Configure now?", default=False):
                _configure_ssrn(console)
                config = load_env_file(DEFAULT_ENV_PATH)
            else:
                set_env_value(DEFAULT_ENV_PATH, "SSRN_ENABLED", "0")
    console.print(prompts.NEW_WIZARD_INTRO)
    keywords = typer.prompt(prompts.PROMPT_KEYWORDS)
    year_start = typer.prompt(prompts.PROMPT_YEAR_START, default="")
    year_end = typer.prompt(prompts.PROMPT_YEAR_END, default="")
    types_raw = typer.prompt(prompts.PROMPT_TYPES, default="")
    fields_raw = typer.prompt(prompts.PROMPT_FIELDS, default="")
    lang_raw = typer.prompt(prompts.PROMPT_LANG, default="")
    access_filter = typer.prompt(prompts.PROMPT_ACCESS, default="both")
    sort_order = typer.prompt(prompts.PROMPT_SORT, default="relevance")
    limit_raw = typer.prompt(prompts.PROMPT_LIMIT, default="")
    download_pdfs = typer.confirm(prompts.PROMPT_DOWNLOAD, default=False)
    output_dir = typer.prompt(prompts.PROMPT_OUTPUT)
    dry_run = typer.confirm(prompts.PROMPT_DRY_RUN, default=False)
    output_format = typer.prompt(prompts.PROMPT_OUTPUT_FORMAT, default="csv").strip().lower()
    if output_format not in {"csv", "tsv"}:
        output_format = "csv"

    query = SearchQuery(
        keywords=keywords,
        year_start=int(year_start) if str(year_start).strip() else None,
        year_end=int(year_end) if str(year_end).strip() else None,
        types=[t.strip() for t in types_raw.split(",") if t.strip()],
        fields_to_search=[f.strip() for f in fields_raw.split(",") if f.strip()],
        languages=[l.strip() for l in lang_raw.split(",") if l.strip()],
        access_filter=access_filter,
        sort_order=sort_order,
        limit=int(limit_raw) if str(limit_raw).strip() else None,
        download_pdfs=download_pdfs,
        output_dir=output_dir,
        dry_run=dry_run,
        output_format=output_format,
    )
    console.print("Keyboard: p=pause, r=resume, s=save+exit, q=stop.")
    console.print("Control file fallback: .papyr_control with PAUSE/RESUME/STOP/SAVE_EXIT in output folder.")
    _, exit_reason = run_metasearch(query, providers, config, console=console)
    if os.getenv("PAPYR_SHELL"):
        for line in prompts.BOOTSTRAP_CHOICES:
            console.print(line)
        console.print(prompts.SHELL_HINT)
    output_name = "results.tsv" if query.output_format == "tsv" else "results.csv"
    console.print(f"Search complete. Results saved to {output_name}")


def _resolve_params_path(input_path: str) -> Path | None:
    candidate = Path(input_path).expanduser()
    if candidate.is_dir():
        params_path = candidate / "search_params.json"
        return params_path if params_path.exists() else None
    if candidate.is_file():
        return candidate if candidate.name.lower() == "search_params.json" else None
    return None


def run_resume_wizard(console: Console, params_path: str) -> None:
    """Run resume wizard."""
    console.print(prompts.RESUME_TITLE)
    resolved = _resolve_params_path(params_path)
    if not resolved:
        console.print("Could not find search_params.json at that path.")
        return
    console.print(f"Params file: {resolved}")
    config = load_env_file(DEFAULT_ENV_PATH)
    _configure_missing_providers(console)
    config = load_env_file(DEFAULT_ENV_PATH)
    params_text = resolved.read_text(encoding="utf-8")
    query = SearchQuery.model_validate_json(params_text)
    original_hash = stable_hash(query.model_dump())
    run_id = _resolve_run_id(query, original_hash)
    existing_count = _count_existing_records(query, run_id)
    do_search, desired_limit, downloads_requested = _maybe_edit_resume_query(query, existing_count)
    resolved.write_text(query.model_dump_json(indent=2), encoding="utf-8")
    providers = default_providers()
    if downloads_requested is None:
        downloads_requested = typer.confirm(
            "Check existing records for missing PDFs and download now?", default=False
        )
    if downloads_requested:
        if not query.download_pdfs:
            if typer.confirm("Downloads are disabled in this run. Enable downloads now?", default=True):
                query.download_pdfs = True
                resolved.write_text(query.model_dump_json(indent=2), encoding="utf-8")
        if query.download_pdfs:
            _download_missing_pdfs(console, query, providers, run_id)
    console.print("Keyboard: p=pause, r=resume, s=save+exit, q=stop.")
    console.print("Control file fallback: .papyr_control with PAUSE/RESUME/STOP/SAVE_EXIT in output folder.")
    if do_search and desired_limit is not None:
        max_new = max(0, desired_limit - existing_count)
    else:
        max_new = None
        if not do_search:
            if os.getenv("PAPYR_SHELL"):
                for line in prompts.BOOTSTRAP_CHOICES:
                    console.print(line)
                console.print(prompts.SHELL_HINT)
            output_name = "results.tsv" if query.output_format == "tsv" else "results.csv"
            console.print(f"Search complete. Results saved to {output_name}")
            return
    _, _exit_reason = run_metasearch(
        query,
        providers,
        config,
        console=console,
        resume_run_id=run_id,
        max_new=max_new,
        append_new_only=True,
    )
    if os.getenv("PAPYR_SHELL"):
        for line in prompts.BOOTSTRAP_CHOICES:
            console.print(line)
        console.print(prompts.SHELL_HINT)
    output_name = "results.tsv" if query.output_format == "tsv" else "results.csv"
    console.print(f"Search complete. Results saved to {output_name}")


def _resolve_run_id(query: SearchQuery, original_hash: str) -> int:
    output_dir = Path(query.output_dir)
    conn = db.connect(output_dir / "state.sqlite")
    db.init_db(conn)
    run_row = repo.get_run_by_hash(conn, original_hash)
    if run_row:
        return int(run_row["id"])
    return repo.create_run(conn, stable_hash(query.model_dump()), query.model_dump())


def _maybe_edit_resume_query(
    query: SearchQuery, existing_count: int
) -> tuple[bool, int | None, bool | None]:
    if not typer.confirm("Edit search parameters before resuming?", default=False):
        return True, query.limit, None
    keywords = typer.prompt("Keywords", default=query.keywords)
    year_start = typer.prompt("Start year (optional)", default=str(query.year_start or ""))
    year_end = typer.prompt("End year (optional)", default=str(query.year_end or ""))
    types_raw = typer.prompt("Publication types (comma-separated)", default=",".join(query.types))
    fields_raw = typer.prompt("Search fields (comma-separated)", default=",".join(query.fields_to_search))
    lang_raw = typer.prompt("Language codes or names (comma-separated)", default=",".join(query.languages))
    access_filter = typer.prompt("Access filter: open/closed/both", default=query.access_filter)
    sort_order = typer.prompt("Sort order", default=query.sort_order)
    limit_prompt = (
        f"Result limit (optional). Leave blank to skip new search; current: {query.limit or ''}"
    )
    limit_raw = typer.prompt(limit_prompt, default="")
    download_pdfs = typer.confirm("Download PDFs?", default=query.download_pdfs)
    output_format = typer.prompt("Output format: csv or tsv", default=query.output_format).strip().lower()
    if output_format not in {"csv", "tsv"}:
        output_format = query.output_format

    query.keywords = keywords
    query.year_start = int(year_start) if str(year_start).strip() else None
    query.year_end = int(year_end) if str(year_end).strip() else None
    query.types = [t.strip() for t in types_raw.split(",") if t.strip()]
    query.fields_to_search = [f.strip() for f in fields_raw.split(",") if f.strip()]
    query.languages = [l.strip() for l in lang_raw.split(",") if l.strip()]
    query.access_filter = access_filter
    query.sort_order = sort_order
    query.download_pdfs = download_pdfs
    query.output_format = output_format

    if not str(limit_raw).strip():
        return False, None, None
    limit_value = int(limit_raw)
    query.limit = limit_value
    if limit_value <= existing_count:
        return False, limit_value, None
    return True, limit_value, None


def _count_existing_records(query: SearchQuery, run_id: int) -> int:
    output_dir = Path(query.output_dir)
    conn = db.connect(output_dir / "state.sqlite")
    db.init_db(conn)
    return repo.count_records(conn, run_id)


def _download_missing_pdfs(
    console: Console,
    query: SearchQuery,
    providers: list,
    run_id: int,
) -> None:
    output_dir = Path(query.output_dir)
    conn = db.connect(output_dir / "state.sqlite")
    db.init_db(conn)
    rows = repo.list_records(conn, run_id)
    downloaded_ids = repo.list_downloaded_ids(conn, run_id)
    providers_by_name = {provider.name: provider for provider in providers}
    files_dir = output_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    for row in rows:
        record = PaperRecord.model_validate_json(row["normalized_json"])
        if record.id and record.id in downloaded_ids:
            continue
        provider = providers_by_name.get(record.origin)
        if not provider:
            continue
        urls = provider.get_official_urls(record)
        pdf_url = urls.get("pdf_url") if urls else None
        if not pdf_url:
            continue
        filename = safe_filename(record.title, record.id or record.url)
        dest = files_dir / filename
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
