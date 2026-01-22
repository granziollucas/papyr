# Quickstart

1) Initialize providers and polite settings
```bash
papyr init
```

2) Start a new search
```bash
papyr new
```

3) Resume a prior search
```bash
papyr resume <path to search_params.json>
```

4) Export RIS (optional)
```bash
papyr export ris
```

Output folder layout
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
