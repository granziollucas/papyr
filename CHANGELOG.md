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
- Update dedup logic to only mark duplicates on title+ID match (Crossref canonical preference).
- Expand README and docs to reflect current CLI options, controls, and output formats.
- Add export format tests and shared local temp fixture for pytest stability.
- Align AGENTS contract with UTF-8 BOM exports and optional SSRN adapter.
- Write duplicates CSV with UTF-8 BOM for consistent encoding.
- Treat keyboard controls as best-effort only when a TTY is available.
- Add launcher shell mode when running `papyr.bat`, `papyr.sh`, or `papyr.command` with no arguments.
- Add credential check guidance in `papyr doctor` with step-by-step command help.
- Run credential check and optional setup before the launcher shell prompt.
- Allow skipping credential setup during bootstrap.
- Print command usage and step-by-step guidance during bootstrap.
- Switch bootstrap to a short `new`/`resume` hint and rely on step-by-step prompts.
- Log provider failures to JSONL and keep runs alive after HTTP errors.
- Quote all CSV fields to avoid comma/newline breakage in Excel and other parsers.
- Fix `SyntaxError` in wizard resume limit prompt string.
- Update Crossref adapter to use versioned endpoint, polite User-Agent defaults, 429 backoff, and cursor stop rule.
- Enable OA PDF downloads from Crossref only when official PDF links are present.

## 1.0.0 - 2026-01-22
- Initial CLI with wizard-driven setup and search.
- Providers: Crossref and arXiv enabled by default; SSRN disabled by default.
- Resumability and incremental runs via SQLite.
- Control-file pause/resume/stop support.
- CSV export with fixed schema and optional RIS export.
- Optional PDF downloading with validation and retries.
- Documentation set with MkDocs site and GitHub Pages workflow.
- Launcher scripts and requirements.txt.
