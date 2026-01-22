from papyr.core.normalize import normalize_generic
from papyr.core.models import RawRecord


def test_normalize_generic():
    raw = RawRecord(provider="Crossref", data={"title": ["Test"], "author": []}, record_id="10.1/abc")
    record = normalize_generic(raw)
    assert record.title == "Test"
    assert record.origin == "Crossref"
    assert record.id == "10.1/abc"
