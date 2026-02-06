from papyr.core.export_csv import export_csv, CSV_COLUMNS
from papyr.core.export_tsv import export_tsv
from papyr.core.models import PaperRecord


def _assert_bom(path):
    data = path.read_bytes()
    assert data.startswith(b"\xef\xbb\xbf")


def test_export_csv_writes_bom_and_header(local_tmp_dir):
    path = local_tmp_dir / "results.csv"
    export_csv([PaperRecord(title="Test")], path)
    _assert_bom(path)
    text = path.read_text(encoding="utf-8-sig")
    header = text.splitlines()[0]
    expected = ",".join([f"\"{col}\"" for col in CSV_COLUMNS])
    assert header == expected


def test_export_tsv_writes_bom_and_header(local_tmp_dir):
    path = local_tmp_dir / "results.tsv"
    export_tsv([PaperRecord(title="Test")], path)
    _assert_bom(path)
    text = path.read_text(encoding="utf-8-sig")
    header = text.splitlines()[0]
    expected = "\t".join([f"\"{col}\"" for col in CSV_COLUMNS])
    assert header == expected
