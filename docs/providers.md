# Providers

Papyr v1 supports Crossref, arXiv, and SSRN. Providers are queried sequentially with conservative rate limits.

## Crossref
- Credentials: not required.
- Search: keyword-based, supports basic year filtering and type filtering.
- Notes: results are normalized to Papyr's CSV schema.

Official API:
```
https://api.crossref.org
```

## arXiv
- Credentials: not required.
- Search: keyword-based via the arXiv API.
- Notes: treated as preprints where possible.

Official API:
```
https://arxiv.org/help/api
```

## SSRN (disabled by default)
- Credentials: required only if you have an approved SSRN API or metadata feed.
- Status: disabled by default. Papyr will not attempt SSRN access unless you explicitly enable it.
- How to enable:
  - Set `SSRN_ENABLED=1` in your `.env` file.
  - Provide any required API credentials or feed URLs as instructed by SSRN Support.
  - Do not enable SSRN unless the access method is explicitly permitted by SSRN’s terms.

Official SSRN site:
```
https://www.ssrn.com
```

Important
- SSRN provides RSS feeds (author pages and rankings) and XML metadata feeds for institutions.
- Requests for SSRN API access or metadata feeds should be submitted to SSRN Support.
- SSRN’s Terms of Use prohibit automated queries; do not enable SSRN unless you have explicit permission.
- SSRN’s policy allows re-displaying title/author/abstract for individual documents with a link to SSRN.
- If SSRN requires scraping for access, do not enable it unless SSRN’s terms explicitly permit it.
- Papyr never bypasses paywalls or uses unauthorized sources.
