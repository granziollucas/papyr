from papyr.core.dedup import find_duplicates
from papyr.core.models import PaperRecord


def test_dedup_title_and_id():
    a = PaperRecord(title="Hello World", id="10.1/abc", origin="Crossref")
    b = PaperRecord(title="Hello, World!", id="10.1/abc", origin="arXiv")
    duplicates = find_duplicates([a, b])
    assert len(duplicates) == 1
    assert duplicates[0][0] is b


def test_dedup_prefers_crossref_as_canonical():
    first = PaperRecord(title="Sample", id="10.1/xyz", origin="arXiv")
    crossref = PaperRecord(title="Sample", id="10.1/xyz", origin="Crossref")
    duplicates = find_duplicates([first, crossref])
    assert len(duplicates) == 1
    duplicate, canonical, reason = duplicates[0]
    assert duplicate is first
    assert canonical is crossref
    assert "crossref" in reason.lower()


def test_dedup_requires_title_and_id_match():
    published = PaperRecord(
        title="Deep Learning for Trading",
        authors="Smith, J.; Doe, A.",
        origin="Crossref",
        type="paper",
        id="10.1/xyz",
    )
    preprint = PaperRecord(
        title="Deep Learning for Trading",
        authors="Smith, J.; Doe, A.",
        origin="arXiv",
        type="preprint",
        id="2201.12345",
    )
    duplicates = find_duplicates([published, preprint])
    assert duplicates == []


def test_dedup_ignores_missing_ids():
    a = PaperRecord(title="Same Title", id="", origin="Crossref")
    b = PaperRecord(title="Same Title", id="", origin="arXiv")
    duplicates = find_duplicates([a, b])
    assert duplicates == []
