# Dev Notes

## Architecture summary
- Provider adapters fetch raw records from external sources.
- Core pipeline normalizes, deduplicates, persists to SQLite, and exports CSV/RIS.
- State lives in `state.sqlite` inside the run folder.

## Key modules
- `src/papyr/cli`: CLI entrypoints and wizard prompts
- `src/papyr/core`: models, pipeline, normalization, dedup, export, downloader
- `src/papyr/adapters`: provider integrations
- `src/papyr/util`: filesystem, hashing, logging, time, config

## How to add a new provider
1) Implement a Provider adapter in `src/papyr/adapters/`.
2) Add it to `default_providers()`.
3) Update `docs/providers.md` with setup and limitations.
4) Add tests for normalization and basic search behavior.

## Assumptions
- SSRN access requires explicit permission and is disabled by default.
- Requests are sequential and rate-limited; no parallelism.
- Errors should not crash a run except for invalid output directory or SQLite failures.

## Known limitations
- SSRN adapter is not implemented unless authorized access is provided.
- Pause/resume uses a control file instead of keyboard hooks.
- Provider-specific filters are best-effort and may be ignored by some APIs.
