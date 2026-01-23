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
from papyr.core.models import SearchQuery
from papyr.core.pipeline import run_metasearch
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
    console.print("Search complete. Results saved to results.csv")


def run_resume_wizard(console: Console, params_path: str) -> None:
    """Run resume wizard."""
    console.print(prompts.RESUME_TITLE)
    console.print(f"Params file: {params_path}")
    console.print(prompts.NOT_IMPLEMENTED)
