"""RIS export."""

from __future__ import annotations

from pathlib import Path

from papyr.core.models import PaperRecord


def _ris_type(record_type: str) -> str:
    value = (record_type or "").lower()
    if "chapter" in value:
        return "CHAP"
    if "book" in value:
        return "BOOK"
    if "preprint" in value:
        return "PREP"
    return "JOUR"


def export_ris(records: list[PaperRecord], path: Path) -> None:
    """Write a basic RIS file from records."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for record in records:
        lines.append(f"TY  - {_ris_type(record.type)}")
        if record.authors:
            for author in record.authors.split(";"):
                lines.append(f"AU  - {author.strip()}")
        if record.title:
            lines.append(f"TI  - {record.title}")
        if record.year:
            lines.append(f"PY  - {record.year}")
        if record.publisher:
            lines.append(f"PB  - {record.publisher}")
        if record.url:
            lines.append(f"UR  - {record.url}")
        if record.abstract:
            lines.append(f"AB  - {record.abstract}")
        if record.id:
            lines.append(f"DO  - {record.id}")
        lines.append("ER  -")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
