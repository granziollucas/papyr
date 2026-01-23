"""TSV export."""

from __future__ import annotations

import csv
from pathlib import Path

from papyr.core.export_csv import CSV_COLUMNS, _csv_value
from papyr.core.models import PaperRecord


def export_tsv(records: list[PaperRecord], path: Path, append: bool = False) -> None:
    """Write TSV in UTF-8 with BOM for Excel friendliness."""
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append and path.exists() else "w"
    write_header = mode == "w"
    with path.open(mode, encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=CSV_COLUMNS,
            delimiter="\t",
            quoting=csv.QUOTE_ALL,
            doublequote=True,
            lineterminator="\n",
        )
        if write_header:
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
