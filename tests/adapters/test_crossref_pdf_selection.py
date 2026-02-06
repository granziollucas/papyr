"""Tests for Crossref PDF selection."""

from papyr.adapters.crossref import CrossrefProvider
from papyr.core.models import RawRecord


def test_crossref_pdf_link_selected() -> None:
    provider = CrossrefProvider()
    data = {
        "DOI": "10.1234/example",
        "link": [
            {
                "URL": "https://example.org/file.pdf",
                "content-type": "application/pdf",
                "intended-application": "text-mining",
            }
        ],
        "license": [{"URL": "https://creativecommons.org/licenses/by/4.0/"}],
    }
    raw = RawRecord(provider="Crossref", data=data, record_id="10.1234/example")
    record = provider.normalize(raw)
    urls = provider.get_official_urls(record)
    assert urls["pdf_url"] == "https://example.org/file.pdf"
    assert record.oa == "true"
    assert record.license == "https://creativecommons.org/licenses/by/4.0/"


def test_crossref_pdf_link_rejected_for_non_pdf() -> None:
    provider = CrossrefProvider()
    data = {
        "DOI": "10.9999/example",
        "link": [
            {
                "URL": "https://example.org/page.html",
                "content-type": "text/html",
            }
        ],
    }
    raw = RawRecord(provider="Crossref", data=data, record_id="10.9999/example")
    record = provider.normalize(raw)
    urls = provider.get_official_urls(record)
    assert urls["pdf_url"] is None
    assert record.oa == "unknown"
