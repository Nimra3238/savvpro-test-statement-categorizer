from .categorizer import categorize
from .parser import parse_statement
from .rules import all_categories


def process_statement(text: str, purchases_positive: bool = False) -> dict:
    parsed, errors = parse_statement(text, purchases_positive)
    seen, transactions = set(), []

    for idx, row in enumerate(parsed, start=1):
        result = categorize(row["description"], row["amount"])
        needs_review, reason, flags = result.needs_review, result.reason, []

        key = (row["date"], row["description"].lower(), row["amount"])
        if key in seen:
            flags.append("possible_duplicate")
            needs_review = True
            reason += " | Possible duplicate charge."
        seen.add(key)

        transactions.append({
            "id": idx, **row,
            "category": result.category,
            "confidence": result.confidence,
            "reason": reason,
            "needs_review": needs_review,
            "flags": flags,
            "reviewed": False,
        })

    return {
        "transactions": transactions,
        "errors": errors,
        "categories": all_categories(),
        "summary": {
            "total_rows": len(transactions),
            "needs_review": sum(t["needs_review"] for t in transactions),
            "skipped_rows": len(errors),
        },
    }