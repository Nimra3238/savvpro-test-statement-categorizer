from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
SAMPLE = Path(__file__).parent.parent / "sample_data" / "statement.csv"


def _upload(content: bytes, name="s.csv", **params):
    return client.post("/api/upload", files={"file": (name, content, "text/csv")}, params=params)


def test_sample_statement():
    res = _upload(SAMPLE.read_bytes())
    assert res.status_code == 200
    data = res.json()
    by_desc = {t["description"]: t for t in data["transactions"]}
    assert by_desc["ADOBE CREATIVE CLOUD"]["category"] == "Software"
    assert by_desc["MYSTERY VENDOR LLC"]["needs_review"] is True
    assert by_desc["ADOBE REFUND"]["category"] == "Refund"
    assert data["summary"]["skipped_rows"] == 1
    assert any("possible_duplicate" in t["flags"] for t in data["transactions"])


def test_rejects_non_csv():
    assert _upload(b"hello", name="x.txt").status_code == 400


def test_rejects_bad_columns():
    assert _upload(b"A,B\n1,2\n").status_code == 422