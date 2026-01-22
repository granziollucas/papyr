# Resumability

Papyr uses SQLite (`state.sqlite`) in the run folder to store:
- Search parameters
- Provider pagination cursors
- Raw and normalized records
- Download status
- Failures

Resume flow
- `papyr resume` accepts a path to `search_params.json`
- The run folder is determined from that file path
- State is loaded from SQLite and search continues from the last cursor

Incremental runs
- Re-running a search in the same folder reuses the same QueryHash
- Records already seen are skipped by ID
- Results are re-exported deterministically
