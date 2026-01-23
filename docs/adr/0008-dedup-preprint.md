# ADR 0008: Drop Preprints When Published Matches by Title and Authors

## Context
- arXiv preprints often later appear as published works.
- Users want published versions to take precedence even when IDs differ.
- Current dedup logic requires title + ID match only.

## Decision
- Add a dedup rule: if normalized title and authors match, and one record is a preprint,
  mark the preprint as a duplicate of the published work.
- Keep the existing title + ID rule and Crossref canonical preference.

## Alternatives Considered
- Keep strict title + ID only (misses common preprint/published duplicates).
- Fuzzy author matching (higher false-positive risk).

## Consequences
- Some preprints will be removed when a published version exists with matching authors.
- The rule is conservative: requires exact normalized author string match.
