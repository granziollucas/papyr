"""Crossref adapter."""

from __future__ import annotations

from typing import Iterable

import requests

from papyr.adapters.base import Provider
from papyr.core.models import PaperRecord, ProviderState, RateLimitPolicy, RawRecord, SearchQuery
from papyr.util.time import now_iso


class CrossrefProvider(Provider):
    name = "Crossref"
    requires_credentials = False
    credential_fields: list[str] = []

    def is_configured(self, config: dict[str, str]) -> bool:
        return True

    def setup_instructions(self) -> list[str]:
        return ["No credentials required for Crossref API."]

    def rate_limit_policy(self) -> RateLimitPolicy:
        return RateLimitPolicy(min_delay_seconds=1.0)

    def search(self, query: SearchQuery, state: ProviderState) -> Iterable[RawRecord]:
        cursor = state.cursor or "*"
        rows = min(query.limit or 20, 100)
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
        resp = requests.get("https://api.crossref.org/works", params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json().get("message", {})
        items = payload.get("items", [])
        for item in items:
            doi = item.get("DOI")
            yield RawRecord(provider=self.name, data=item, record_id=doi)

    def normalize(self, raw: RawRecord) -> PaperRecord:
        data = raw.data
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
            id=raw.record_id or "",
            url=f"https://doi.org/{raw.record_id}" if raw.record_id else "",
            retrieved_at=now_iso(),
        )
        return record

    def get_official_urls(self, record: PaperRecord) -> dict[str, str | None]:
        return {"landing_url": record.url, "pdf_url": None}
