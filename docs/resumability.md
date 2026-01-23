# Resumability

Papyr uses SQLite (`state.sqlite`) to persist everything needed for resume and incremental runs.

## Stored state
- Search parameters
- Provider pagination cursors
- Raw and normalized records
- Download status
- Failures

## Resume flow
1) Run `papyr resume <run folder>` or `papyr resume <path to search_params.json>`
2) Papyr resolves the run folder and loads the search parameters
3) You can optionally edit parameters before resuming
4) You can optionally download missing PDFs for already saved records
5) If you increase the result limit, Papyr fetches only the difference and appends new rows
6) If you type `0` for the limit during resume, Papyr removes the limit and continues unbounded
3) Provider cursors are read from SQLite and the run continues

## Incremental runs
- Re-running a search in the same output folder reuses the QueryHash
- Already seen record IDs are skipped
- `results.csv` is re-exported deterministically from all stored records

## Pause/resume/stop
- Keyboard shortcuts: p=pause, r=resume, s=save+exit, q=stop
- Control file fallback: create `.papyr_control` in the output directory
- Write one of: PAUSE, RESUME, STOP, SAVE_EXIT
- Papyr polls the file during the run
