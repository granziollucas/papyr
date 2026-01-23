from papyr.core.dedup import find_duplicates
from papyr.core.models import PaperRecord


def test_dedup_title_and_id():
    a = PaperRecord(title="Hello World", id="10.1/abc", origin="Crossref")
    b = PaperRecord(title="Hello, World!", id="10.1/abc", origin="arXiv")
    duplicates = find_duplicates([a, b])
    assert len(duplicates) == 1
    assert duplicates[0][0] is b


def test_dedup_preprint_by_title_and_authors():
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
    assert len(duplicates) == 1
    assert duplicates[0][0] is preprint
