"""Configuration helpers (env/.env)."""

from __future__ import annotations

from pathlib import Path


DEFAULT_ENV_PATH = Path(".env")


def load_env_file(path: Path) -> dict[str, str]:
    """Load a simple .env file (KEY=VALUE)."""
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def write_env_file(path: Path, data: dict[str, str]) -> None:
    """Write .env data (KEY=VALUE)."""
    lines = []
    for key in sorted(data.keys()):
        value = data[key]
        lines.append(f"{key}={value}")
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def set_env_value(path: Path, key: str, value: str) -> None:
    """Set a single key in the .env file."""
    data = load_env_file(path)
    data[key] = value
    write_env_file(path, data)
