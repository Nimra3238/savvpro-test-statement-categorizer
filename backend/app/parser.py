import csv
import io
import re
from datetime import datetime

DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%d-%m-%Y",
                "%b %d, %Y", "%d %b %Y", "%m/%d/%y"]

ALIASES = {
    "date": {"date", "transaction date", "trans date", "posted date", "posting date"},
    "description": {"description", "memo", "details", "merchant", "narrative", "payee", "name"},
    "amount": {"amount", "value", "transaction amount"},
    "debit": {"debit", "withdrawal", "withdrawals"},
    "credit": {"credit", "deposit", "deposits"},
}


class StatementError(Exception):
    pass


def parse_amount(raw: str) -> float:
    s = (raw or "").strip()
    if not s:
        raise ValueError("empty amount")
    negative = s.startswith("(") and s.endswith(")")
    cleaned = re.sub(r"[^\d.\-]", "", s)
    if cleaned in ("", "-", "."):
        raise ValueError(f"bad amount '{raw}'")
    value = float(cleaned)
    return -abs(value) if negative else value


def parse_date(raw: str) -> str:
    s = (raw or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"bad date '{raw}'")


def _map_headers(fieldnames):
    mapping = {}
    for name in fieldnames or []:
        key = name.strip().lower()
        for canonical, names in ALIASES.items():
            if key in names and canonical not in mapping:
                mapping[canonical] = name
    return mapping


def parse_statement(text: str, purchases_positive: bool = False):
    """Returns (rows, errors). Bad rows never crash the upload."""
    reader = csv.DictReader(io.StringIO(text))
    cols = _map_headers(reader.fieldnames)

    has_amount = "amount" in cols
    has_split = "debit" in cols or "credit" in cols
    if "date" not in cols or "description" not in cols or not (has_amount or has_split):
        raise StatementError(
            "CSV needs a date column, a description column and an amount "
            "(or debit/credit) column."
        )

    rows, errors = [], []
    for line_no, row in enumerate(reader, start=2):
        try:
            date = parse_date(row[cols["date"]])
            description = (row[cols["description"]] or "").strip()
            if not description:
                raise ValueError("empty description")
            if has_amount:
                amount = parse_amount(row[cols["amount"]])
                if purchases_positive:
                    amount = -amount
            else:
                debit = parse_amount(row[cols["debit"]]) if row.get(cols.get("debit", ""), "").strip() else 0.0
                credit = parse_amount(row[cols["credit"]]) if row.get(cols.get("credit", ""), "").strip() else 0.0
                amount = abs(credit) - abs(debit)
            rows.append({"date": date, "description": description, "amount": round(amount, 2)})
        except (ValueError, KeyError, TypeError) as exc:
            errors.append({"line": line_no, "error": str(exc)})
    return rows, errors