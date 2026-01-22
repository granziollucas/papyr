"""Control file helpers for pause/resume/stop."""

from __future__ import annotations

import time
from pathlib import Path


def read_control_command(control_path: Path) -> str | None:
    """Read control command from file."""
    if not control_path.exists():
        return None
    content = control_path.read_text(encoding="utf-8").strip().upper()
    return content or None


def clear_control_command(control_path: Path) -> None:
    """Clear control file contents."""
    if control_path.exists():
        control_path.write_text("", encoding="utf-8")


def wait_if_paused(control_path: Path) -> bool:
    """Pause loop; return False if stop requested."""
    while True:
        cmd = read_control_command(control_path)
        if cmd == "STOP":
            clear_control_command(control_path)
            return False
        if cmd == "RESUME" or cmd is None:
            clear_control_command(control_path)
            return True
        time.sleep(1.0)
