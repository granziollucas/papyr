# Papyr

Papyr is a Python CLI that searches academic works across multiple sources and exports a single CSV with official access links. It can optionally download legitimate PDFs when explicitly enabled.

What it does
- Searches Crossref, arXiv, and SSRN (SSRN disabled by default).
- Exports a CSV with a fixed schema and official URLs.
- Supports resumable and incremental runs via SQLite state.

What it does NOT do
- It does not bypass paywalls or use unauthorized sources.
- It does not scrape SSRN without explicit permission.
- It does not use LLM features in v1.

Install
```bash
pip install -e .
```

Quick start
```bash
papyr init
papyr new
```

Launcher scripts
- Windows: `papyr-setup.bat` installs requirements, then run `papyr.bat`
- macOS/Linux: `papyr-setup.sh` installs requirements, then run `papyr.sh`

Docs site (MkDocs)
```bash
mkdocs serve
```

Key commands
- `papyr init` initialize credentials and providers
- `papyr new` start a new search
- `papyr resume` resume a prior search
- `papyr doctor` check environment
- `papyr export ris` export RIS from CSV

License
See `LICENSE`.
