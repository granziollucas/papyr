"""Test configuration to allow imports from src/ without installation."""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4
import shutil

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


@pytest.fixture
def local_tmp_dir() -> Path:
    base_dir = PROJECT_ROOT / "test-tmp"
    base_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = base_dir / f"papyr-test-{uuid4().hex}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
