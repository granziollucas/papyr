"""CSV export."""

from __future__ import annotations

import csv
from pathlib import Path

from papyr.core.models import PaperRecord


CSV_COLUMNS = [
    "Authors",
    "Title",
    "Abstract",
    "Origin",
    "Volume",
    "Issue",
    "Pages",
    "Publisher",
    "Month",
    "Year",
    "Type",
    "Keywords",
    "Citations",
    "OA",
    "ID",
    "URL",
    "License",
    "RetrievedAt",
    "QueryHash",
    "DuplicateOf",
]


def _csv_value(value: object) -> str:
    """Normalize values for safer CSV consumption in common tools."""
    if value is None:
        return ""
    text = str(value)
    # Normalize line breaks to avoid row-splitting in naive CSV readers.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if "\n" in text:
        text = " ".join(text.splitlines())
    return text


def export_csv(records: list[PaperRecord], path: Path) -> None:
    """Write CSV in UTF-8 with BOM for Excel friendliness."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=CSV_COLUMNS,
            quoting=csv.QUOTE_ALL,
            escapechar="\\",
            doublequote=True,
            lineterminator="\n",
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "Authors": _csv_value(record.authors),
                    "Title": _csv_value(record.title),
                    "Abstract": _csv_value(record.abstract),
                    "Origin": _csv_value(record.origin),
                    "Volume": _csv_value(record.volume),
                    "Issue": _csv_value(record.issue),
                    "Pages": _csv_value(record.pages),
                    "Publisher": _csv_value(record.publisher),
                    "Month": _csv_value(record.month),
                    "Year": _csv_value(record.year),
                    "Type": _csv_value(record.type),
                    "Keywords": _csv_value(record.keywords),
                    "Citations": _csv_value(record.citations),
                    "OA": _csv_value(record.oa),
                    "ID": _csv_value(record.id),
                    "URL": _csv_value(record.url),
                    "License": _csv_value(record.license),
                    "RetrievedAt": _csv_value(record.retrieved_at),
                    "QueryHash": _csv_value(record.query_hash),
                    "DuplicateOf": _csv_value(record.duplicate_of),
                }
            )
