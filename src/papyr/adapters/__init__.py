"""Provider registry."""

from __future__ import annotations

from papyr.adapters.arxiv import ArxivProvider
from papyr.adapters.crossref import CrossrefProvider
from papyr.adapters.ssrn import SsrnProvider


def default_providers() -> list:
    """Return default provider instances."""
    return [CrossrefProvider(), ArxivProvider(), SsrnProvider()]
