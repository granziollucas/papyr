"""Provider interface contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from papyr.core.models import PaperRecord, ProviderState, RawRecord, RateLimitPolicy, SearchQuery


class Provider(ABC):
    """Provider interface."""

    name: str
    requires_credentials: bool
    credential_fields: list[str]

    @abstractmethod
    def is_configured(self, config: dict[str, str]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def setup_instructions(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: SearchQuery, state: ProviderState) -> Iterable[RawRecord]:
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw: RawRecord) -> PaperRecord:
        raise NotImplementedError

    @abstractmethod
    def get_official_urls(self, record: PaperRecord) -> dict[str, str | None]:
        raise NotImplementedError

    @abstractmethod
    def rate_limit_policy(self) -> RateLimitPolicy:
        raise NotImplementedError
