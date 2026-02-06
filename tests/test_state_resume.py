import sqlite3
from pathlib import Path
from uuid import uuid4
import shutil

from papyr.core.state import db, repo
from papyr.core.models import PaperRecord, RawRecord


def test_state_resume():
    base_dir = Path(__file__).resolve().parents[1] / "test-tmp"
    base_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = base_dir / f"papyr-test-{uuid4().hex}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    try:
        db_path = temp_dir / "state.sqlite"
        conn = db.connect(db_path)
        db.init_db(conn)

        run_id = repo.create_run(conn, "hash1", {"keywords": "test"})
        raw = RawRecord(provider="Crossref", data={"title": ["A"], "author": []}, record_id="10.1/abc")
        record = PaperRecord(title="A", origin="Crossref", id="10.1/abc")
        repo.insert_record(conn, run_id, "Crossref", raw, record)

        existing = repo.list_record_ids(conn, run_id)
        assert "10.1/abc" in existing
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
