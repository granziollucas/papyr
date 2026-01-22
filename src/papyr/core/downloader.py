"""PDF downloader with validation and retries."""

from __future__ import annotations

import time
from pathlib import Path

import requests


class DownloadResult:
    """Download result container."""

    def __init__(self, ok: bool, attempts: int, message: str = "") -> None:
        self.ok = ok
        self.attempts = attempts
        self.message = message


def download_pdf(url: str, dest_path: Path) -> DownloadResult:
    """Download a PDF if content-type and magic bytes are valid."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    attempts = 0
    delay = 1.0
    while attempts < 3:
        attempts += 1
        try:
            with requests.get(url, stream=True, timeout=30) as resp:
                resp.raise_for_status()
                content_type = resp.headers.get("Content-Type", "")
                if "pdf" not in content_type.lower():
                    return DownloadResult(False, attempts, f"Invalid content-type: {content_type}")
                iterator = resp.iter_content(chunk_size=8192)
                first_chunk = next(iterator, b"")
                if not first_chunk.startswith(b"%PDF"):
                    return DownloadResult(False, attempts, "Invalid PDF magic bytes")
                with dest_path.open("wb") as handle:
                    handle.write(first_chunk)
                    for chunk in iterator:
                        if chunk:
                            handle.write(chunk)
                return DownloadResult(True, attempts, "ok")
        except Exception as exc:  # noqa: BLE001
            if attempts >= 3:
                return DownloadResult(False, attempts, str(exc))
            time.sleep(delay)
            delay *= 2
    return DownloadResult(False, attempts, "failed")
