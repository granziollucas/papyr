import pytest

openpyxl = pytest.importorskip("openpyxl")

from papyr.core.export_csv import CSV_COLUMNS
from papyr.core.export_xlsx import export_xlsx
from papyr.core.models import PaperRecord


def test_export_xlsx_creates_provider_sheets(local_tmp_dir):
    path = local_tmp_dir / "results.xlsx"
    records = [
        PaperRecord(title="One", origin="Crossref"),
        PaperRecord(title="Two", origin="arXiv"),
    ]
    export_xlsx(records, path)

    workbook = openpyxl.load_workbook(path)
    assert set(workbook.sheetnames) == {"Crossref", "arXiv"}
    sheet = workbook["Crossref"]
    header = [cell.value for cell in sheet[1]]
    assert header == CSV_COLUMNS
    assert sheet.max_row == 2


def test_export_xlsx_appends_on_resume(local_tmp_dir):
    path = local_tmp_dir / "results.xlsx"
    export_xlsx([PaperRecord(title="One", origin="Crossref")], path)
    export_xlsx([PaperRecord(title="Two", origin="Crossref")], path, append=True)

    workbook = openpyxl.load_workbook(path)
    sheet = workbook["Crossref"]
    assert sheet.max_row == 3
