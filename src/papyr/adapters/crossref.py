"""Crossref adapter."""

from __future__ import annotations

import time
from typing import Iterable

import requests

from papyr.adapters.base import Provider
from papyr.core.models import PaperRecord, ProviderState, RateLimitPolicy, RawRecord, SearchQuery
from papyr.core.rate_limit import RateLimiter
from papyr.util.time import now_iso


class CrossrefProvider(Provider):
    name = "Crossref"
    requires_credentials = True
    credential_fields: list[str] = ["CROSSREF_EMAIL", "CROSSREF_USER_AGENT"]

    def is_configured(self, config: dict[str, str]) -> bool:
        if config.get("CROSSREF_ENABLED", "1") == "0":
            return False
        return bool(config.get("CROSSREF_EMAIL"))

    def setup_instructions(self) -> list[str]:
        return [
            "Crossref requires polite requests with a contact email.",
            "Provide a contact email and optional user agent string.",
        ]

    def rate_limit_policy(self) -> RateLimitPolicy:
        return RateLimitPolicy(min_delay_seconds=1.0)

    def search(self, query: SearchQuery, state: ProviderState) -> Iterable[RawRecord]:
        cursor = state.cursor or "*"
        remaining = query.limit
        limiter = RateLimiter(self.rate_limit_policy())
        while True:
            rows = 100
            if remaining is not None:
                rows = min(100, remaining)
                if rows <= 0:
                    break
            params = {
                "query": query.keywords,
                "rows": rows,
                "cursor": cursor,
            }
            filters: list[str] = []
            if query.year_start:
                filters.append(f"from-pub-date:{query.year_start}-01-01")
            if query.year_end:
                filters.append(f"until-pub-date:{query.year_end}-12-31")
            if query.types:
                filters.append(f"type:{query.types[0]}")
            if filters:
                params["filter"] = ",".join(filters)
            email = query.extra.get("crossref_email") if hasattr(query, "extra") else None
            if email:
                params["mailto"] = email
            limiter.wait()
            headers = {}
            user_agent = query.extra.get("crossref_user_agent") if hasattr(query, "extra") else None
            if user_agent:
                headers["User-Agent"] = user_agent
            resp = requests.get(
                "https://api.crossref.org/works",
                params=params,
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            payload = resp.json().get("message", {})
            items = payload.get("items", [])
            for item in items:
                doi = item.get("DOI")
                yield RawRecord(provider=self.name, data=item, record_id=doi)
                if remaining is not None:
                    remaining -= 1
                    if remaining <= 0:
                        break
            next_cursor = payload.get("next-cursor")
            if next_cursor:
                cursor = next_cursor
                state.cursor = cursor
            state.last_request_time = time.time()
            if not items or not next_cursor:
                break
            if remaining is not None and remaining <= 0:
                break

    def normalize(self, raw: RawRecord) -> PaperRecord:
        data = raw.data
        doi = raw.record_id or ""
        isbn = ""
        if not doi:
            isbns = data.get("ISBN", []) or []
            if isinstance(isbns, list) and isbns:
                isbn = str(isbns[0])
        authors = []
        for author in data.get("author", []) or []:
            given = author.get("given", "")
            family = author.get("family", "")
            if family or given:
                authors.append(f"{family}, {given[:1]}." if given else family)
        title = ""
        if data.get("title"):
            title = data.get("title")[0]
        abstract = data.get("abstract", "")
        publisher = data.get("publisher", "")
        year = ""
        if data.get("issued") and data["issued"].get("date-parts"):
            year = str(data["issued"]["date-parts"][0][0])
        record = PaperRecord(
            authors="; ".join(authors),
            title=title,
            abstract=abstract,
            origin=self.name,
            publisher=publisher,
            year=year,
            id=doi or isbn,
            url=f"https://doi.org/{doi}" if doi else data.get("URL", ""),
            retrieved_at=now_iso(),
        )
        return record

    def get_official_urls(self, record: PaperRecord) -> dict[str, str | None]:
        return {"landing_url": record.url, "pdf_url": None}
