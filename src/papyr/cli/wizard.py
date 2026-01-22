"""Wizard flows for interactive CLI."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
import typer

from papyr.adapters import default_providers
from papyr.adapters.crossref import CrossrefProvider
from papyr.adapters.ssrn import SsrnProvider
from papyr.cli import prompts
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
    for line in prompts.NEXT_COMMANDS:
        console.print(line)


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
    console.print(prompts.NOT_IMPLEMENTED)


def run_resume_wizard(console: Console, params_path: str) -> None:
    """Run resume wizard."""
    console.print(prompts.RESUME_TITLE)
    console.print(f"Params file: {params_path}")
    console.print(prompts.NOT_IMPLEMENTED)
