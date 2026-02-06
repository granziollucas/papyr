# ADR 0010: SSRN Optional by Default

## Status
Accepted

## Context
- The AGENTS contract listed SSRN as mandatory, but the adapter is disabled by default.
- SSRN access often requires explicit permission or approved feeds.
- The project policy forbids scraping when ToS is unclear.

## Decision
- Treat SSRN as optional and disabled by default until explicit permission is available.
- Keep SSRN adapter gated by `SSRN_ENABLED=1` and documented in providers.

## Alternatives Considered
- Require SSRN by default (risks ToS violations and blocked access).
- Remove SSRN entirely (would conflict with the long-term goal to support it ethically).

## Consequences
- Users can still opt in when authorized.
- Default behavior stays compliant and low-risk.
