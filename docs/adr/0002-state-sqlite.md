Title: SQLite for resumable state
Date: 2026-01-22
Status: Accepted

Context
- Papyr requires resumable, incremental searches with reliable local state.
- State must be cross-platform and easy to inspect or back up.

Decision
- Use SQLite (state.sqlite) in the run folder as the single state store.
- Store runs, provider state cursors, raw + normalized records, downloads, and failures.

Alternatives considered
- JSON files per provider with incremental checkpoints.
- Embedded key-value stores (e.g., sqlite alternatives).

Consequences / trade-offs
- Requires schema management and migration strategy in future versions.
- Provides robustness, queryability, and atomic writes for resumability.
