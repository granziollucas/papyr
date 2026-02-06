# Data Schema

Papyr exports a CSV with fixed columns. Columns are always present even if blank.

## CSV Columns

- Authors: "Surname, N.; Surname, N.; ..."
- Title
- Abstract
- Origin: provider name
- Volume
- Issue
- Pages
- Publisher
- Month
- Year
- Type: paper/preprint/book_chapter/etc.
- Keywords
- Citations
- OA: true/false/unknown
- ID: DOI/arXiv/SSRN id (or ISBN for books)
- URL: official landing page
- License
- RetrievedAt: ISO timestamp
- QueryHash: stable hash of search parameters
- DuplicateOf: if deduped

## Encoding and delimiter
- Output format is chosen per run: XLSX, CSV, or TSV.
- XLSX: one sheet per provider (Crossref/arXiv/SSRN) with the same columns.
- CSV: comma-separated, UTF-8 with BOM (utf-8-sig), quoted fields.
- TSV: tab-separated, UTF-8 with BOM (utf-8-sig), quoted fields.

## RIS Mapping (best-effort)
- TY: derived from Type
- AU: Authors
- TI: Title
- PY: Year
- PB: Publisher
- UR: URL
- AB: Abstract
- DO: ID

## Deduplication
- Titles are normalized (casefold, strip punctuation, collapse whitespace)
- Duplicates are marked only when normalized title and ID both match
- Crossref is canonical when duplicates are found (title+ID match)

## OA Notes
- Crossref records are marked OA when a license or official PDF link is present.
- PDF downloads for Crossref only use links supplied by Crossref.
