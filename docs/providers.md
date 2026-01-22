# Providers

Papyr v1 supports Crossref, arXiv, and SSRN. Providers are queried sequentially with conservative rate limits.

## Crossref

### Setup
- Required: contact email for polite requests.
- Optional: user agent string.

Environment keys:
- `CROSSREF_ENABLED` (1 or 0)
- `CROSSREF_EMAIL`
- `CROSSREF_USER_AGENT`

### Capabilities
- Keyword search
- Year filter (from/until)
- Type filter (best-effort)

### Notes
- Uses Crossref API `mailto` parameter.
- If skipped, Crossref is disabled but will be prompted on each new search.

## arXiv

### Setup
- No credentials required.

### Capabilities
- Keyword search via arXiv API.

### Notes
- Results are treated as preprints.

## SSRN (disabled by default)

### Setup
- SSRN access is disabled unless you explicitly opt in.
- You must have explicit permission or approved API/feed access from SSRN.

Environment keys:
- `SSRN_ENABLED` (1 or 0)
- `SSRN_FEED_URL`

### Notes
- Do not enable SSRN unless SSRN terms explicitly allow your access method.
- Papyr will not bypass paywalls or scrape SSRN without permission.
