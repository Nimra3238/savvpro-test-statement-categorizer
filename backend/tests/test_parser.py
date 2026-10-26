import pytest
from app.parser import StatementError, parse_amount, parse_date, parse_statement


def test_amount_formats():
    assert parse_amount("-$1,234.50") == -1234.5
    assert parse_amount("($9.99)") == -9.99
    assert parse_amount("12") == 12.0
    with pytest.raises(ValueError):
        parse_amount("abc")


def test_date_formats():
    assert parse_date("2026-09-01") == "2026-09-01"
    assert parse_date("09/01/2026") == "2026-09-01"
    with pytest.raises(ValueError):
        parse_date("nope")


def test_bad_rows_are_skipped_not_fatal():
    rows, errors = parse_statement("Date,Description,Amount\n2026-09-01,X,-5\nbad,Y,abc\n")
    assert len(rows) == 1 and len(errors) == 1


def test_missing_columns_raises():
    with pytest.raises(StatementError):
        parse_statement("Foo,Bar\n1,2\n")


def test_purchases_positive_flips_sign():
    rows, _ = parse_statement("Date,Description,Amount\n2026-09-01,X,5\n", purchases_positive=True)
    assert rows[0]["amount"] == -5.0


def test_debit_credit_columns():
    rows, _ = parse_statement("Date,Description,Debit,Credit\n2026-09-01,X,5.00,\n2026-09-02,Y,,9.00\n")
    assert [r["amount"] for r in rows] == [-5.0, 9.0]