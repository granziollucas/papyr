Title: Layered architecture (adapters + core)
Date: 2026-01-22
Status: Accepted

Context
- Papyr must support multiple providers with different APIs and be extensible.
- The CLI needs stable core logic for normalization, deduplication, and persistence.

Decision
- Use a layered architecture with provider adapters and a domain core.
- Providers implement a common interface and emit RawRecord objects.
- Core pipeline normalizes, deduplicates, persists to SQLite, and exports CSV/RIS.

Alternatives considered
- Monolithic provider-specific pipelines.
- Provider-specific output formats instead of a shared core model.

Consequences / trade-offs
- Additional abstraction requires more upfront structure.
- Easier to add providers and keep output consistent.
