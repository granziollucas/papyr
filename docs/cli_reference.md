# CLI Reference

## papyr init
Runs the credential setup wizard and environment checks.

## papyr new
Starts a new search wizard.

Prompts:
- Keywords
- Year range
- Publication types
- Search fields
- Languages
- Access filter
- Sort order
- Limit
- Download PDFs
- Output directory
- Dry-run

## papyr resume
Resumes a prior search from `search_params.json`.

## papyr config show
Shows current config (secrets redacted).

## papyr config init
Creates a `.env` template file.

## papyr doctor
Validates environment, credentials, and connectivity (best-effort).

## papyr reset-cache
Resets local cache/state for a run.

## papyr export ris
Generates a RIS file from the current CSV.
