import re
from collections import defaultdict
from datetime import datetime

from thefuzz import fuzz

from recur_scan.transactions import Transaction

# ELDER DYLAN CODE STARTS HERE

# def get_is_always_recurring(transaction: Transaction) -> bool:
#   """Check if the transaction is always recurring because of the vendor name - check lowercase match"""
#   always_recurring_vendors = {
#       "google storage",
#       "netflix",
#       "hulu",
#       "spotify",
#   }
#   return transaction.name.lower() in always_recurring_vendors


def get_is_insurance(transaction: Transaction) -> bool:
    """Check if the transaction is an insurance payment."""
    # use a regular expression with boundaries to match case-insensitive insurance
    # and insurance-related terms
    match = re.search(r"\b(insurance|insur|insuranc)\b", transaction.name, re.IGNORECASE)
    return bool(match)


#   def get_is_utility(transaction: Transaction) -> bool:
#       """Check if the transaction is a utility payment."""
#       # use a regular expression with boundaries to match case-insensitive utility
#       # and utility-related terms
#       match = re.search(r"\b(utility|utilit|energy)\b", transaction.name, re.IGNORECASE)
#       return bool(match)


def get_is_phone(transaction: Transaction) -> bool:
    """Check if the transaction is a phone payment."""
    # use a regular expression with boundaries to match case-insensitive phone
    # and phone-related terms
    match = re.search(r"\b(at&t|t-mobile|verizon)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def _get_days(date: str) -> int:
    """Get the number of days since the epoch of a transaction date."""
    return (datetime.strptime(date, "%Y-%m-%d") - datetime(1970, 1, 1)).days


def get_n_transactions_days_apart_v1(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> int:
    n_txs = 0
    transaction_days = _get_days(transaction.date)

    for t in all_transactions:
        t_days = _get_days(t.date)
        days_diff = abs(t_days - transaction_days)

        # Skip if the difference is less than n_days_apart - n_days_off
        if days_diff < n_days_apart - n_days_off:
            continue

        remainder = days_diff % n_days_apart
        if remainder <= n_days_off or (remainder > 0 and (n_days_apart - remainder) <= n_days_off):
            n_txs += 1

        print(f"Transaction: {t.date}, Days Apart: {days_diff}, Remainder: {remainder}, Counted: {n_txs}")

    return n_txs


def _get_day(date: str) -> int:
    """Get the day of the month from a transaction date."""
    return int(date.split("-")[2])


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    """Get the number of transactions in all_transactions that are on the same day of the month as transaction"""
    return len([t for t in all_transactions if abs(_get_day(t.date) - _get_day(transaction.date)) <= n_days_off])


def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in 99"""
    return (transaction.amount * 100) % 100 == 99


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction."""
    if not all_transactions:
        return 0.0
    n_same_amount: int = len([t for t in all_transactions if t.amount == transaction.amount])
    return float(n_same_amount) / float(len(all_transactions))  # Explicit conversion


# def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
#     return {
#         "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
#         "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
#         "ends_in_99": get_ends_in_99(transaction),
#         "amount": transaction.amount,
#         "same_day_exact": get_n_transactions_same_day(transaction, all_transactions, 0),
#         "same_day_off_by_1": get_n_transactions_same_day(transaction, all_transactions, 1),
#         "same_day_off_by_2": get_n_transactions_same_day(transaction, all_transactions, 2),
#         "14_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 14, 0),
#         "14_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 14, 1),
#         "7_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 7, 0),
#         "7_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 7, 1),
#         "is_insurance": get_is_insurance(transaction),
#         "is_utility": get_is_utility(transaction),
#         "is_phone": get_is_phone(transaction),
#         "is_always_recurring": get_is_always_recurring(transaction),
#     }

# ELDER DYLAN CODE ENDS HERE


# MY CODE ADDITIONS START HERE


def get_n_transactions_days_apart(
    transaction: Transaction, all_transactions: list[Transaction], n_days_apart: int, n_days_off: int
) -> int:
    """
    Get the number of transactions in all_transactions that are within n_days_off of being
    n_days_apart from transaction.
    """
    transaction_days = _get_days(transaction.date)
    seen_transactions = set()  # Track unique transactions

    for t in all_transactions:
        t_days = _get_days(t.date)
        days_diff = abs(t_days - transaction_days)

        # Ensure transaction is within the valid range and not already counted
        if n_days_apart - n_days_off <= days_diff <= n_days_apart + n_days_off:
            seen_transactions.add(t.id)  # Add unique transaction ID

    return len(seen_transactions)  # Return the count of unique transactions


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


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int | bool]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "ends_in_99": get_ends_in_99(transaction),
        "amount": transaction.amount,
        "same_day_exact": get_n_transactions_same_day(transaction, all_transactions, 0),
        "same_day_off_by_1": get_n_transactions_same_day(transaction, all_transactions, 1),
        "same_day_off_by_2": get_n_transactions_same_day(transaction, all_transactions, 2),
        "7_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 7, 0),
        "7_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 7, 1),
        "14_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 14, 0),
        "14_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 14, 1),
        "30_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 30, 0),
        "30_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 30, 1),
        "60_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 60, 0),
        "90_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 90, 0),
        "is_insurance": get_is_insurance(transaction),
        "is_utility": is_utility_bill(transaction),
        "is_phone": get_is_phone(transaction),
        "is_always_recurring": get_is_always_recurring(transaction),
        "is_auto_pay": is_auto_pay(transaction),
        "is_membership": is_membership(transaction),
    }


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
