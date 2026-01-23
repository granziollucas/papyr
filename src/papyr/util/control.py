"""Control helpers for pause/resume/stop."""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path


class KeyboardControl:
    """Background keyboard listener for pause/resume/stop."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._command: str | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._enabled = False
        self._is_windows = sys.platform.startswith("win")

    def start(self) -> bool:
        """Start keyboard listener; returns True if enabled."""
        if not sys.stdin.isatty():
            return False
        try:
            if self._is_windows:
                import msvcrt  # noqa: F401
            else:
                import termios  # noqa: F401
                import tty  # noqa: F401
        except Exception:
            return False
        self._enabled = True
        self._thread = threading.Thread(target=self._run, name="papyr-keyboard", daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        """Stop keyboard listener."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    def get_command(self) -> str | None:
        with self._lock:
            return self._command

    def clear_command(self) -> None:
        with self._lock:
            self._command = None

    def _set_command(self, command: str) -> None:
        with self._lock:
            self._command = command

    def _run(self) -> None:
        if self._is_windows:
            self._run_windows()
        else:
            self._run_posix()

    def _run_windows(self) -> None:
        import msvcrt

        while not self._stop.is_set():
            if msvcrt.kbhit():
                ch = msvcrt.getwch().lower()
                cmd = _map_key(ch)
                if cmd:
                    self._set_command(cmd)
            time.sleep(0.1)

    def _run_posix(self) -> None:
        import select
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            while not self._stop.is_set():
                readable, _, _ = select.select([sys.stdin], [], [], 0.1)
                if readable:
                    ch = sys.stdin.read(1).lower()
                    cmd = _map_key(ch)
                    if cmd:
                        self._set_command(cmd)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _map_key(ch: str) -> str | None:
    if ch == "p":
        return "PAUSE"
    if ch == "r":
        return "RESUME"
    if ch == "s":
        return "SAVE_EXIT"
    if ch == "q":
        return "STOP"
    return None


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


def wait_if_paused(control_path: Path, keyboard: KeyboardControl | None = None) -> str:
    """Pause loop; returns resume/stop/save_exit."""
    while True:
        cmd = poll_control(control_path, keyboard)
        if cmd == "STOP":
            return "stop"
        if cmd == "SAVE_EXIT":
            return "save_exit"
        if cmd == "RESUME":
            return "resume"
        time.sleep(1.0)


def poll_control(control_path: Path, keyboard: KeyboardControl | None) -> str | None:
    if keyboard:
        cmd = keyboard.get_command()
        if cmd:
            keyboard.clear_command()
            return cmd
    cmd = read_control_command(control_path)
    if cmd:
        clear_control_command(control_path)
    return cmd
