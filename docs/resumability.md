# Resumability

Papyr uses SQLite (`state.sqlite`) to persist everything needed for resume and incremental runs.

## Stored state
- Search parameters
- Provider pagination cursors
- Raw and normalized records
- Download status
- Failures

## Resume flow
1) Run `papyr resume <path to search_params.json>`
2) Papyr loads the run folder from that path
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
