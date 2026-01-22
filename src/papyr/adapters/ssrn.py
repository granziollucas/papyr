"""SSRN adapter (disabled by default)."""

from __future__ import annotations

from typing import Iterable

from papyr.adapters.base import Provider
from papyr.core.models import PaperRecord, ProviderState, RateLimitPolicy, RawRecord, SearchQuery


class SsrnProvider(Provider):
    name = "SSRN"
    requires_credentials = False
    credential_fields: list[str] = []

    def is_configured(self, config: dict[str, str]) -> bool:
        return config.get("SSRN_ENABLED", "0") == "1"

    def setup_instructions(self) -> list[str]:
        return [
            "SSRN adapter is disabled by default.",
            "Enable by setting SSRN_ENABLED=1 in your .env if you accept SSRN terms.",
        ]

    def rate_limit_policy(self) -> RateLimitPolicy:
        return RateLimitPolicy(min_delay_seconds=2.0)

    def search(self, query: SearchQuery, state: ProviderState) -> Iterable[RawRecord]:
        raise NotImplementedError(
            "SSRN adapter is disabled by default. See docs/providers.md before enabling."
        )

    def normalize(self, raw: RawRecord) -> PaperRecord:
        raise NotImplementedError("SSRN adapter not implemented yet.")

    def get_official_urls(self, record: PaperRecord) -> dict[str, str | None]:
        return {"landing_url": record.url, "pdf_url": None}
