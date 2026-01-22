import sqlite3

import pytest

from papyr.core.state import db, repo
from papyr.core.models import PaperRecord, RawRecord


def test_state_resume(tmp_path):
    db_path = tmp_path / "state.sqlite"
    conn = db.connect(db_path)
    db.init_db(conn)

    run_id = repo.create_run(conn, "hash1", {"keywords": "test"})
    raw = RawRecord(provider="Crossref", data={"title": ["A"], "author": []}, record_id="10.1/abc")
    record = PaperRecord(title="A", origin="Crossref", id="10.1/abc")
    repo.insert_record(conn, run_id, "Crossref", raw, record)

    existing = repo.list_record_ids(conn, run_id)
    assert "10.1/abc" in existing
