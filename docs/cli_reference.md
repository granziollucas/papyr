# CLI Reference

## papyr init
Runs the credential setup wizard and provider checks.

Steps:
- Crossref polite email
- SSRN opt-in (disabled by default)

## papyr new
Starts the interactive search wizard.

Prompts:
- Keywords (required)
- Year range (optional)
- Publication types (optional)
- Search fields (optional)
- Language codes or names (optional)
- Access filter: open / closed / both
- Sort order (best-effort)
- Result limit (optional)
- Download PDFs (yes/no)
- Output directory
- Dry-run (yes/no)

During runs:
- A `.papyr_control` file in the output folder can pause/resume/stop.

## papyr resume
Resumes a prior search. You must pass the path to `search_params.json`.

## papyr config show
Shows current config with secrets redacted.

## papyr config init
Creates a `.env` template.

## papyr doctor
Validates environment, credentials, and connectivity (best-effort).

## papyr reset-cache
Resets local cache/state for a run (asks for confirmation).

## papyr export ris
Generates `results.ris` from the current CSV.
