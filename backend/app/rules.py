NEEDS_REVIEW = "Needs Review"
NON_SPENDING = "Non-spending"
REFUND = "Refund"
INCOME = "Income"

REVIEW_THRESHOLD = 0.6

# Use case: freelance designer's business credit card
MERCHANT_RULES = {
    "Software": ["ADOBE", "FIGMA", "NOTION", "GITHUB", "DROPBOX", "ZOOM",
                 "SLACK", "AMAZON WEB SERVICES", "CANVA"],
    "Travel": ["UBER", "CAREEM", "LYFT", "AIRLINE", "AIRWAYS", "HOTEL",
               "BOOKING.COM", "AIRBNB", "PARKING"],
    "Meals": ["UBER EATS", "STARBUCKS", "RESTAURANT", "KFC",
              "PIZZA", "DOORDASH"],
    "Office Supplies": ["STAPLES", "OFFICE DEPOT", "PRINTING", "STATIONERY"],
    "Advertising": ["GOOGLE ADS", "META ADS", "FACEBK", "LINKEDIN ADS"],
    "Bank Fees": ["ANNUAL FEE", "LATE FEE", "INTEREST CHARGE", "FOREIGN TRANSACTION FEE"],
}

# Merchants that sell everything: we refuse to guess.
AMBIGUOUS_MERCHANTS = ["AMAZON", "PAYPAL", "WALMART", "TARGET", "SQ"]

TRANSFER_HINTS = ["TRANSFER", "PAYMENT THANK YOU", "AUTOPAY", "AUTOMATIC PAYMENT",
                  "TO SAVINGS", "FROM SAVINGS"]
REFUND_HINTS = ["REFUND", "REVERSAL", "RETURN", "CHARGEBACK", "CREDIT ADJUSTMENT"]
INCOME_HINTS = ["INVOICE", "CLIENT PAYMENT", "STRIPE PAYOUT", "PAYOUT"]


def all_categories() -> list[str]:
    return [*MERCHANT_RULES.keys(), NON_SPENDING, REFUND, INCOME, NEEDS_REVIEW]