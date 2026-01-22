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


def export_csv(records: list[PaperRecord], path: Path) -> None:
    """Write CSV in latin1 encoding for Excel friendliness."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="latin1", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "Authors": record.authors,
                    "Title": record.title,
                    "Abstract": record.abstract,
                    "Origin": record.origin,
                    "Volume": record.volume,
                    "Issue": record.issue,
                    "Pages": record.pages,
                    "Publisher": record.publisher,
                    "Month": record.month,
                    "Year": record.year,
                    "Type": record.type,
                    "Keywords": record.keywords,
                    "Citations": record.citations,
                    "OA": record.oa,
                    "ID": record.id,
                    "URL": record.url,
                    "License": record.license,
                    "RetrievedAt": record.retrieved_at,
                    "QueryHash": record.query_hash,
                    "DuplicateOf": record.duplicate_of,
                }
            )
