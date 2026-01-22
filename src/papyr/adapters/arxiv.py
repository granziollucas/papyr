"""arXiv adapter."""

from __future__ import annotations

from typing import Iterable
from xml.etree import ElementTree as ET

import requests

from papyr.adapters.base import Provider
from papyr.core.models import PaperRecord, ProviderState, RateLimitPolicy, RawRecord, SearchQuery
from papyr.util.time import now_iso


class ArxivProvider(Provider):
    name = "arXiv"
    requires_credentials = False
    credential_fields: list[str] = []

    def is_configured(self, config: dict[str, str]) -> bool:
        return True

    def setup_instructions(self) -> list[str]:
        return ["No credentials required for arXiv API."]

    def rate_limit_policy(self) -> RateLimitPolicy:
        return RateLimitPolicy(min_delay_seconds=3.0)

    def search(self, query: SearchQuery, state: ProviderState) -> Iterable[RawRecord]:
        start = int(state.cursor or "0")
        max_results = min(query.limit or 20, 100)
        search_query = f"all:{query.keywords}"
        params = {
            "search_query": search_query,
            "start": start,
            "max_results": max_results,
        }
        resp = requests.get("http://export.arxiv.org/api/query", params=params, timeout=30)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            arxiv_id = entry.findtext("atom:id", default="", namespaces=ns)
            title = entry.findtext("atom:title", default="", namespaces=ns)
            summary = entry.findtext("atom:summary", default="", namespaces=ns)
            authors = [a.findtext("atom:name", default="", namespaces=ns) for a in entry.findall("atom:author", ns)]
            published = entry.findtext("atom:published", default="", namespaces=ns)
            data = {
                "title": title.strip(),
                "summary": summary.strip(),
                "authors": authors,
                "published": published,
            }
            yield RawRecord(provider=self.name, data=data, record_id=arxiv_id)

    def normalize(self, raw: RawRecord) -> PaperRecord:
        data = raw.data
        authors = []
        for author in data.get("authors", []) or []:
            parts = author.split()
            if not parts:
                continue
            family = parts[-1]
            given = " ".join(parts[:-1])
            authors.append(f"{family}, {given[:1]}." if given else family)
        year = ""
        published = data.get("published", "")
        if published:
            year = published.split("-")[0]
        record = PaperRecord(
            authors="; ".join(authors),
            title=data.get("title", ""),
            abstract=data.get("summary", ""),
            origin=self.name,
            year=year,
            id=raw.record_id or "",
            url=raw.record_id or "",
            retrieved_at=now_iso(),
            type="preprint",
        )
        return record

    def get_official_urls(self, record: PaperRecord) -> dict[str, str | None]:
        pdf_url = None
        if record.url and "arxiv.org" in record.url:
            pdf_url = record.url.replace("/abs/", "/pdf/")
        return {"landing_url": record.url, "pdf_url": pdf_url}
