# Quickstart

This guide walks through a minimal run.

## 1) Initialize providers
Run the setup wizard to store provider settings.

```bash
papyr init
```

Notes:
- Crossref requires a contact email (polite requests).
- SSRN is disabled by default unless you explicitly enable it.

## 2) Start a new search
```bash
papyr new
```

You will be prompted for:
- Keywords
- Year range (optional)
- Publication types (optional)
- Search fields (optional)
- Languages (optional)
- Access filter (open/closed/both)
- Sort order
- Limit (optional)
- Download PDFs (yes/no)
- Output directory
- Dry-run (yes/no)

## 3) Resume a search
```bash
papyr resume <path to search_params.json>
```

## Optional launcher shell
If you run a launcher with no arguments, it opens a simple shell so you can run multiple commands without reopening the terminal.

Examples:
```bash
papyr.bat
papyr> init
papyr> new
papyr> exit
```

## 4) Export RIS (optional)
```bash
papyr export ris
```

## Run folder layout
```
<output_dir>/
  search_params.json
  results.csv
  results.ris
  state.sqlite
  logs/
    run_<timestamp>.log
    duplicates_<timestamp>.csv
    errors_<timestamp>.jsonl
  files/
    <sanitized_title>_<shortid>.pdf
```

## Pause/resume/stop control
Create a file named `.papyr_control` in the output directory with one of:
- `PAUSE`
- `RESUME`
- `STOP`

Papyr will poll this file during the run.
