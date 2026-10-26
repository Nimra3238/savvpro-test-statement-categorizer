import pytest
from app.categorizer import categorize


@pytest.mark.parametrize("desc,amount,expected", [
    ("ADOBE CREATIVE CLOUD", -54.99, "Software"),
    ("UBER *TRIP HELP.UBER.COM", -18.40, "Travel"),
    ("UBER EATS 8841", -26.15, "Meals"),
    ("AMAZON WEB SERVICES", -31.77, "Software"),
    ("TRANSFER TO SAVINGS", -500, "Non-spending"),
    ("PAYMENT THANK YOU", 800, "Non-spending"),
    ("ADOBE REFUND", 54.99, "Refund"),
    ("INVOICE 1043 CLIENT PAYMENT", 1500, "Income"),
])
def test_known_cases(desc, amount, expected):
    result = categorize(desc, amount)
    assert result.category == expected
    assert not result.needs_review


@pytest.mark.parametrize("desc,amount", [
    ("JOES CAFE 9921", -12.5),
    ("MYSTERY VENDOR LLC", -88.0),
    ("AMAZON MKTPLACE PMTS", -43.21),
    ("SQ *CORNER BAKERY", -9.5),
    ("RANDOM DEPOSIT", 50.0),
    ("", -5.0),
    ("ADOBE CREATIVE CLOUD", 0.0),
])
def test_uncertain_goes_to_review(desc, amount):
    assert categorize(desc, amount).needs_review


def test_refund_is_never_income():
    assert categorize("FIGMA REFUND", 15.0).category != "Income"