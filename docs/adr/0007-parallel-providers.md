# ADR 0007: Optional Parallel Provider Execution

## Context
- Sequential provider searches can be slow for large queries.
- Users requested optional parallel execution across providers.
- SQLite state needs safe concurrent access.

## Decision
- Add an optional `parallel_providers` flag to run providers concurrently.
- Keep default as sequential to remain conservative with rate limits.
- Use separate SQLite connections per provider and a shared lock for writes.
- Enable WAL mode for improved concurrency in SQLite.

## Alternatives Considered
- Fully sequential only (simpler but slower).
- Shared connection across threads (blocked by sqlite thread-safety).
- Full async rewrite (larger refactor).

## Consequences
- Parallel mode improves throughput but still respects per-provider rate limits.
- Some operations are serialized via a write lock to avoid database lock errors.
- Control (pause/stop) remains global across providers.
