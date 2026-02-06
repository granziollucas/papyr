# ADR 0009: UTF-8 BOM for CSV Outputs

## Status
Accepted

## Context
- The AGENTS contract required `latin1` encoding for CSV outputs, but the implementation already uses UTF-8 BOM for better Unicode support.
- `latin1` truncates or corrupts non-ASCII author names and titles.
- Excel reliably opens UTF-8 BOM CSVs across platforms.

## Decision
- Standardize CSV outputs (including duplicates logs) on UTF-8 BOM (`utf-8-sig`).
- Update the AGENTS contract to reflect UTF-8 BOM as the expected export encoding.

## Alternatives Considered
- Keep `latin1` for Excel compatibility (rejects Unicode correctness).
- Switch to UTF-8 without BOM (can display incorrectly in Excel on Windows).

## Consequences
- Unicode data is preserved in exports.
- Excel compatibility remains strong via BOM.
- Any tooling expecting `latin1` must be updated.
