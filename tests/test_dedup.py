from papyr.core.dedup import find_duplicates
from papyr.core.models import PaperRecord


def test_dedup_title_and_id():
    a = PaperRecord(title="Hello World", id="10.1/abc", origin="Crossref")
    b = PaperRecord(title="Hello, World!", id="10.1/abc", origin="arXiv")
    duplicates = find_duplicates([a, b])
    assert len(duplicates) == 1
    assert duplicates[0][0] is b
