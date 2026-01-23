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
- Output format is chosen per run: CSV or TSV.
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
- Duplicates require matching title and ID by default
- If title and authors match and one record is a preprint, the preprint is dropped
- Crossref is canonical when duplicates are found
