# Papyr

Papyr is a Python CLI that searches academic works across multiple sources and exports a single CSV (or TSV) with official access links. It can optionally download legitimate PDFs when explicitly enabled.

## Key Features
- Searches Crossref and arXiv (SSRN optional and disabled by default).
- Exports a fixed-schema results file and supports resumable runs via SQLite.
- Runs as a wizard-driven CLI with minimal console noise and detailed logs.
- Optional PDF downloads from official, legitimate sources only.

## What Papyr Does NOT Do
- It does not bypass paywalls or use unauthorized sources.
- It does not scrape SSRN without explicit permission.
- It does not use LLM features in v1.

## Tech Stack
- Python 3.11+
- Typer (CLI)
- Rich (console UI)
- SQLite (state)

## Prerequisites
- Python 3.11+
- Optional: `pip` and a virtual environment manager of your choice

## Install
Editable install for local development:

```bash
pip install -e .
```

## Quick Start
```bash
papyr init
papyr new
```

## Launcher Scripts
Use launchers if you want a simple shell (`papyr>`) for multiple commands:

- Windows: `papyr-setup.bat` installs requirements, then run `papyr.bat`
- macOS/Linux: `papyr-setup.sh` installs requirements, then run `papyr.sh`

Example:
```bash
papyr.bat
papyr> init
papyr> new
papyr> exit
```

## Commands
- `papyr init` initialize credentials and providers
- `papyr new` start a new search wizard
- `papyr resume <run folder or search_params.json>` resume a prior search
- `papyr config show` display current config (secrets redacted)
- `papyr config init` create a `.env` template
- `papyr doctor` validate environment and show next steps
- `papyr reset-cache` reset local cache/state for a run (asks for confirmation)
- `papyr export ris` export RIS from CSV

## Providers
### Crossref
- Requires a contact email for polite requests.
- Optional User-Agent string.

### arXiv
- No credentials required.

### SSRN (Disabled by Default)
- Only enable if you have explicit permission or approved API/feed access.

See `docs/providers.md` for details.

## Output Layout
```
<output_dir>/
  search_params.json
  results.csv
  results.tsv
  results.xlsx
  results.ris
  state.sqlite
  logs/
    run_<timestamp>.log
    duplicates_<timestamp>.csv
    errors_<timestamp>.jsonl
  files/
    <sanitized_title>_<shortid>.pdf
```

Notes:
- The run creates `results.xlsx` by default, or `results.csv`/`results.tsv` if selected.
- The XLSX contains one sheet per provider (Crossref/arXiv/SSRN) with the same columns.
- Only one of `results.xlsx`, `results.csv`, or `results.tsv` is created per run.
- All results use UTF-8 with BOM (`utf-8-sig`) for Excel friendliness.

## Resumability and Incremental Runs
- State is stored in `state.sqlite`.
- You can resume by pointing at the run folder or `search_params.json`.
- If you increase the limit, Papyr fetches only the delta.
- Control file (`.papyr_control`) can pause/resume/stop reliably. Keyboard shortcuts are best-effort.

## PDF Download Policy
Downloads happen ONLY when explicitly enabled in the wizard.
- Only official, legitimate PDF URLs are used.
- No paywall bypass or scraping is supported.

## Logs and Errors
- Console output is minimal.
- Full DEBUG logs: `logs/run_<timestamp>.log`
- Structured errors: `logs/errors_<timestamp>.jsonl`
- Duplicates: `logs/duplicates_<timestamp>.csv`

## Documentation
Serve docs locally:
```bash
mkdocs serve
```

Key docs:
- `docs/quickstart.md`
- `docs/cli_reference.md`
- `docs/providers.md`
- `docs/data_schema.md`
- `docs/resumability.md`
- `docs/troubleshooting.md`

## Testing
```bash
pytest -v
```

Network tests (skipped by default) live under `tests/adapters/`.

## License
See `LICENSE`.
