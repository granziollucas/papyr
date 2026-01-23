"""Core data models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


AccessFilter = Literal["open", "closed", "both"]


class SearchQuery(BaseModel):
    """User search parameters."""

    keywords: str
    year_start: int | None = None
    year_end: int | None = None
    types: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    fields_to_search: list[str] = Field(default_factory=list)
    access_filter: AccessFilter = "both"
    sort_order: str = "relevance"
    limit: int | None = None
    download_pdfs: bool = False
    output_dir: str
    dry_run: bool = False
    output_format: Literal["csv", "tsv"] = "csv"
    parallel_providers: bool = False
    extra: dict[str, str] = Field(default_factory=dict)


class RawRecord(BaseModel):
    """Raw provider record."""

    provider: str
    data: dict[str, Any]
    record_id: str | None = None


class PaperRecord(BaseModel):
    """Normalized record for CSV export."""

    authors: str = ""
    title: str = ""
    abstract: str = ""
    origin: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    publisher: str = ""
    month: str = ""
    year: str = ""
    type: str = ""
    keywords: str = ""
    citations: str = ""
    oa: str = "unknown"
    id: str = ""
    url: str = ""
    license: str = ""
    retrieved_at: str = ""
    query_hash: str = ""
    duplicate_of: str = ""


class ProviderState(BaseModel):
    """Provider-specific state for resuming."""

    cursor: str | None = None
    last_request_time: float | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class RateLimitPolicy(BaseModel):
    """Rate limit policy."""

    min_delay_seconds: float = 1.0
