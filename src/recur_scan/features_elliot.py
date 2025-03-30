import re
from collections import defaultdict
from datetime import datetime

from thefuzz import fuzz

from recur_scan.transactions import Transaction


def get_is_near_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if a transaction has a recurring amount within 5% of another transaction."""
    return any(t != transaction and abs(transaction.amount - t.amount) / t.amount <= 0.05 for t in all_transactions)


def is_utility_bill(transaction: Transaction) -> bool:
    """
    Check if the transaction is a utility bill (water, gas, electricity, etc.).
    """
    utility_keywords = (
        r"\b(water|gas|electricity|power|energy|utility|sewage|trash|waste|heating|cable|internet|broadband|tv)\b"
    )
    utility_providers = {
        "duke energy",
        "pg&e",
        "con edison",
        "national grid",
        "xcel energy",
        "southern california edison",
        "dominion energy",
        "centerpoint energy",
        "peoples gas",
        "nrg energy",
        "direct energy",
        "atmos energy",
        "comcast",
        "xfinity",
        "spectrum",
        "verizon fios",
        "centurylink",
        "at&t",
        "cox communications",
    }

    name_lower = transaction.name.lower()

    # Check for keywords or known US utility providers
    return bool(re.search(utility_keywords, name_lower, re.IGNORECASE)) or any(
        provider in name_lower for provider in utility_providers
    )


def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring using fuzzy matching."""
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
        "apple music",
        "apple arcade",
        "apple tv+",
        "apple fitness+",
        "apple icloud",
        "apple one",
        "amazon prime",
        "adobe creative cloud",
        "microsoft 365",
        "dropbox",
        "youtube premium",
        "discord nitro",
        "playstation plus",
        "xbox game pass",
        "comcast xfinity",
        "spectrum",
        "verizon fios",
        "centurylink",
        "cox communications",
        "at&t internet",
        "t-mobile home internet",
    }

    return any(fuzz.partial_ratio(transaction.name.lower(), vendor) > 85 for vendor in always_recurring_vendors)


def is_auto_pay(transaction: Transaction) -> bool:
    """
    Check if the transaction is an automatic recurring payment.
    """
    return bool(re.search(r"\b(auto\s?pay|autopayment|automatic payment)\b", transaction.name, re.IGNORECASE))


def is_membership(transaction: Transaction) -> bool:
    """
    Check if the transaction is a membership payment.
    """
    membership_keywords = r"\b(membership|subscription|club|gym|association|society)\b"
    return bool(re.search(membership_keywords, transaction.name, re.IGNORECASE))


def is_recurring_based_on_99(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if a transaction is recurring based on:
    - Amount ending in .99
    - At least 3 occurrences
    - Same company/vendor
    - Appears at 7, 14, 30, or 60-day intervals

    :param transaction: Transaction to check
    :param all_transactions: List of all transactions
    :return: True if it meets the recurring pattern, False otherwise
    """
    if (transaction.amount * 100) % 100 != 99:
        return False

    vendor = transaction.name.lower()
    date_occurrences = defaultdict(list)

    # Store transactions for the same vendor
    for t in all_transactions:
        if t.name.lower() == vendor and (t.amount * 100) % 100 == 99:
            days_since_epoch = (datetime.strptime(t.date, "%Y-%m-%d") - datetime(1970, 1, 1)).days
            date_occurrences[vendor].append(days_since_epoch)

    # Check for recurring pattern (7, 14, 30, or 60 days apart)
    if len(date_occurrences[vendor]) < 3:
        return False  # Must appear at least 3 times

    date_occurrences[vendor].sort()

    count = 1  # Start with the first transaction counted
    for i in range(1, len(date_occurrences[vendor])):
        day_diff = date_occurrences[vendor][i] - date_occurrences[vendor][i - 1]

        if day_diff in {7, 14, 30, 60}:
            count += 1
            if count >= 3:
                return True  # Recurring pattern found
        else:
            count = 1  # Reset count if the gap doesn't match

    return False


def get_transaction_similarity(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Computes the average similarity score of a transaction with other transactions."""
    scores: list[int] = [
        fuzz.partial_ratio(transaction.name.lower(), t.name.lower()) for t in all_transactions if t.id != transaction.id
    ]
    return float(sum(scores)) / len(scores) if scores else 0.0


def is_weekday_transaction(transaction: Transaction) -> bool:
    """Returns True if the transaction happened on a weekday (Monday-Friday)."""
    return datetime.strptime(transaction.date, "%Y-%m-%d").weekday() < 5


def is_price_trending(transaction: Transaction, all_transactions: list[Transaction], threshold: int) -> bool:
    """
    Checks if a transaction's amount gradually increases or decreases within a threshold percentage.
    """
    same_vendor_txs = [t.amount for t in all_transactions if t.name == transaction.name]
    if len(same_vendor_txs) < 3:  # Need at least 3 data points to detect trends
        return False

    price_differences = [abs(same_vendor_txs[i] - same_vendor_txs[i - 1]) for i in range(1, len(same_vendor_txs))]
    avg_change = sum(price_differences) / len(price_differences)

    return avg_change <= (transaction.amount * threshold / 100)


def is_split_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Detects if a transaction is part of a split payment series."""
    related_txs = [t for t in all_transactions if t.amount < transaction.amount and t.name == transaction.name]
    return len(related_txs) >= 2  # Consider it a split payment if there are 2+ similar smaller transactions
