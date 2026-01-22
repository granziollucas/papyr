# Dev Notes

## Architecture summary
- Providers emit RawRecord objects via adapters.
- Core pipeline normalizes, deduplicates, persists to SQLite, and exports CSV/RIS.
- State is managed in `state.sqlite` in the run folder.

## Key modules
- `src/papyr/cli`: CLI entrypoints and wizards
- `src/papyr/core`: models, pipeline, normalization, dedup, export, downloader
- `src/papyr/adapters`: provider integrations
- `src/papyr/util`: filesystem, hashing, logging, time, config

## Adding a new provider
1) Implement a Provider adapter in `src/papyr/adapters/`.
2) Add it to `default_providers()`.
3) Update docs/providers.md with setup and limitations.
4) Add tests for normalization and basic search behavior.

## Assumptions and limitations
- SSRN access requires explicit permission; disabled by default.
- No parallelism; sequential requests only.
- Minimal UI; logs contain full details.
