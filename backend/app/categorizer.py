import re
from dataclasses import dataclass

from .rules import (
    AMBIGUOUS_MERCHANTS, INCOME, INCOME_HINTS, MERCHANT_RULES, NEEDS_REVIEW,
    NON_SPENDING, REFUND, REFUND_HINTS, REVIEW_THRESHOLD, TRANSFER_HINTS,
)


@dataclass(frozen=True)
class Result:
    category: str
    confidence: float
    reason: str

    @property
    def needs_review(self) -> bool:
        return self.category == NEEDS_REVIEW or self.confidence < REVIEW_THRESHOLD


def normalize(description: str) -> str:
    """Uppercase, drop symbols and long reference numbers."""
    text = description.upper()
    text = re.sub(r"[^A-Z0-9.& ]", " ", text)
    text = re.sub(r"\b\d{3,}\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _contains(text: str, phrase: str) -> bool:
    return re.search(rf"\b{re.escape(phrase)}\b", text) is not None


def _match_merchant(text: str):
    """Longest keyword wins ('UBER EATS' beats 'UBER').
    Returns (category, keyword, status) or None."""
    hits = []
    for category, keywords in MERCHANT_RULES.items():
        hits += [(len(k), k, category) for k in keywords if _contains(text, k)]
    hits += [(len(k), k, NEEDS_REVIEW) for k in AMBIGUOUS_MERCHANTS if _contains(text, k)]
    if not hits:
        return None
    longest = max(h[0] for h in hits)
    top = [h for h in hits if h[0] == longest]
    if len({h[2] for h in top}) > 1:
        return NEEDS_REVIEW, top[0][1], "conflict"
    category, keyword = top[0][2], top[0][1]
    return category, keyword, ("ambiguous" if category == NEEDS_REVIEW else "ok")


def categorize(description: str, amount: float) -> Result:
    """amount < 0 means money spent, amount > 0 means money in."""
    text = normalize(description)
    if not text:
        return Result(NEEDS_REVIEW, 0.0, "Empty description")

    if any(_contains(text, h) for h in TRANSFER_HINTS):
        return Result(NON_SPENDING, 0.95, "Transfer or card payment, not spending")

    match = _match_merchant(text)

    if amount > 0:
        if any(_contains(text, h) for h in REFUND_HINTS):
            source = f" from {match[0]}" if match and match[2] == "ok" else ""
            return Result(REFUND, 0.85, f"Money back{source}, not income")
        if any(_contains(text, h) for h in INCOME_HINTS):
            return Result(INCOME, 0.85, "Client payment or payout")
        return Result(NEEDS_REVIEW, 0.3, "Money in with no clear refund or income signal")

    if amount == 0:
        return Result(NEEDS_REVIEW, 0.0, "Zero amount")
    if match is None:
        return Result(NEEDS_REVIEW, 0.0, "Unknown merchant")

    category, keyword, status = match
    if status == "ambiguous":
        return Result(NEEDS_REVIEW, 0.2, f"'{keyword}' sells many things, can't guess")
    if status == "conflict":
        return Result(NEEDS_REVIEW, 0.2, "Matches more than one category")
    return Result(category, 0.9, f"Matched merchant '{keyword}'")