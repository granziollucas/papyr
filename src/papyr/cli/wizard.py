"""Wizard flows for interactive CLI."""

from __future__ import annotations

from rich.console import Console

from papyr.cli import prompts


def run_init_wizard(console: Console) -> None:
    """Run credential setup wizard."""
    console.print(prompts.INIT_TITLE)
    console.print(prompts.NOT_IMPLEMENTED)
    for line in prompts.NEXT_COMMANDS:
        console.print(line)


def run_new_wizard(console: Console) -> None:
    """Run new search wizard."""
    console.print(prompts.NEW_TITLE)
    console.print(prompts.NOT_IMPLEMENTED)


def run_resume_wizard(console: Console, params_path: str) -> None:
    """Run resume wizard."""
    console.print(prompts.RESUME_TITLE)
    console.print(f"Params file: {params_path}")
    console.print(prompts.NOT_IMPLEMENTED)
