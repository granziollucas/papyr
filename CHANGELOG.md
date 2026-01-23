# CHANGELOG

## 1.1 - 2026-01-23
- Select output format (CSV or TSV) during the search wizard; persisted per run.
- Add TSV export with UTF-8 BOM for improved Excel/pandas compatibility.
- Switch CSV export to UTF-8 BOM to prevent Unicode encoding errors.
- Normalize IDs to codes only (DOI/arXiv/ISBN), not URLs.
- Show shell guidance lines after runs complete, stop, or save+exit.
- Add keyboard controls for pause/resume/save+exit/stop with control-file fallback.
- Show running/paused status in the progress line.

## Unreleased
- Add launcher shell mode when running `papyr.bat`, `papyr.sh`, or `papyr.command` with no arguments.
- Add credential check guidance in `papyr doctor` with step-by-step command help.
- Run credential check and optional setup before the launcher shell prompt.
- Allow skipping credential setup during bootstrap.
- Print command usage and step-by-step guidance during bootstrap.
- Switch bootstrap to a short `new`/`resume` hint and rely on step-by-step prompts.
- Log provider failures to JSONL and keep runs alive after HTTP errors.
- Quote all CSV fields to avoid comma/newline breakage in Excel and other parsers.

## 1.0.0 - 2026-01-22
- Initial CLI with wizard-driven setup and search.
- Providers: Crossref and arXiv enabled by default; SSRN disabled by default.
- Resumability and incremental runs via SQLite.
- Control-file pause/resume/stop support.
- CSV export with fixed schema and optional RIS export.
- Optional PDF downloading with validation and retries.
- Documentation set with MkDocs site and GitHub Pages workflow.
- Launcher scripts and requirements.txt.
