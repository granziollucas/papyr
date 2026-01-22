"""Typer CLI entrypoint."""

from __future__ import annotations

import typer
from rich.console import Console

from papyr.cli import wizard

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


@app.command("new")
def new_command() -> None:
    """Start a new search wizard."""
    wizard.run_new_wizard(console)


@app.command("resume")
def resume_command(params_path: str = typer.Argument(..., help="Path to search_params.json")) -> None:
    """Resume a prior search."""
    wizard.run_resume_wizard(console, params_path)


@config_app.command("show")
def config_show() -> None:
    """Display current config (redact secrets)."""
    console.print("Not implemented yet.")


@config_app.command("init")
def config_init() -> None:
    """Create config template file."""
    console.print("Not implemented yet.")


@app.command("doctor")
def doctor() -> None:
    """Validate environment, credentials, connectivity (best-effort)."""
    console.print("Not implemented yet.")


@app.command("reset-cache")
def reset_cache() -> None:
    """Reset local cache/state for a run (ask for confirmation)."""
    console.print("Not implemented yet.")


@export_app.command("ris")
def export_ris() -> None:
    """Generate RIS file from current run (CSV-driven)."""
    console.print("Not implemented yet.")
