"""Typer CLI entrypoint."""

from __future__ import annotations

import typer
from rich.console import Console

from papyr.cli import prompts, wizard
from papyr.adapters import default_providers
from papyr.util.config import DEFAULT_ENV_PATH, load_env_file, write_env_file

app = typer.Typer(add_completion=False, help="Papyr CLI")
config_app = typer.Typer(help="Config commands")
export_app = typer.Typer(help="Export commands")

app.add_typer(config_app, name="config")
app.add_typer(export_app, name="export")

console = Console()


@app.command("init")
def init_command() -> None:
    """Credential setup wizard + doctor checks."""
    wizard.run_init_wizard(console)
    _print_credential_status(show_fix=False)
    _print_next_choices()


@app.command("bootstrap")
def bootstrap_command() -> None:
    """Credential check and guided next steps."""
    wizard.run_bootstrap(console)
    _print_credential_status(show_fix=True)
    _print_next_choices()


@app.command("new")
def new_command() -> None:
    """Start a new search wizard."""
    wizard.run_new_wizard(console)


@app.command("resume")
def resume_command(
    params_path: str | None = typer.Argument(
        None,
        help="Path to search_params.json",
    )
) -> None:
    """Resume a prior search."""
    if not params_path:
        params_path = typer.prompt(
            "Step 1/1: Path to search_params.json. Example: C:\\Papyr\\runs\\climate\\search_params.json"
        )
    wizard.run_resume_wizard(console, params_path)


@config_app.command("show")
def config_show() -> None:
    """Display current config (redact secrets)."""
    config = load_env_file(DEFAULT_ENV_PATH)
    if not config:
        console.print("No .env found.")
        return
    redacted = {}
    for key, value in config.items():
        if key.endswith("_KEY") or key.endswith("_TOKEN") or key.endswith("_PASSWORD"):
            redacted[key] = "****"
        else:
            redacted[key] = value
    for key in sorted(redacted.keys()):
        console.print(f"{key}={redacted[key]}")


@config_app.command("init")
def config_init() -> None:
    """Create config template file."""
    template = {
        "CROSSREF_ENABLED": "1",
        "CROSSREF_EMAIL": "",
        "CROSSREF_USER_AGENT": "",
        "SSRN_ENABLED": "0",
        "SSRN_FEED_URL": "",
    }
    write_env_file(DEFAULT_ENV_PATH, template)
    console.print("Created .env template.")


@app.command("doctor")
def doctor() -> None:
    """Validate environment, credentials, connectivity (best-effort)."""
    console.print(prompts.DOCTOR_TITLE)
    _print_credential_status(show_fix=True)
    _print_next_choices()


@app.command("reset-cache")
def reset_cache() -> None:
    """Reset local cache/state for a run (ask for confirmation)."""
    console.print("Not implemented yet.")


@export_app.command("ris")
def export_ris() -> None:
    """Generate RIS file from current run (CSV-driven)."""
    console.print("Not implemented yet.")


def _credential_report() -> tuple[bool, list[str]]:
    config = load_env_file(DEFAULT_ENV_PATH)
    providers = default_providers()
    ok = True
    lines: list[str] = []
    for provider in providers:
        if provider.requires_credentials:
            if provider.is_configured(config):
                lines.append(f"{provider.name}: ok")
            else:
                ok = False
                lines.append(f"{provider.name}: missing credentials")
        else:
            if provider.is_configured(config):
                lines.append(f"{provider.name}: enabled")
            else:
                lines.append(f"{provider.name}: disabled (optional)")
    return ok, lines


def _print_credential_status(show_fix: bool) -> bool:
    ok, lines = _credential_report()
    console.print("Credential check:")
    for line in lines:
        console.print(f"  {line}")
    if not ok and show_fix:
        console.print("Fix: run papyr init to configure missing credentials.")
    return ok


def _print_next_choices() -> None:
    for line in prompts.BOOTSTRAP_CHOICES:
        console.print(line)
