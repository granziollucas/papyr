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
- ID: DOI/arXiv/SSRN id
- URL: official landing page
- License
- RetrievedAt: ISO timestamp
- QueryHash: stable hash of search parameters
- DuplicateOf: if deduped

## Encoding and delimiter
- Comma-separated
- UTF-8 with BOM (utf-8-sig) for Excel compatibility
- Proper quoting and escaping for commas/newlines

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
- Duplicates require matching title and ID
- Crossref is canonical when duplicates are found
