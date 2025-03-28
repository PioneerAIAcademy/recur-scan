import difflib
import re
from datetime import date, datetime
from functools import lru_cache

from recur_scan.transactions import Transaction


def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring because of the vendor name - check lowercase match"""
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
    }
    return transaction.name.lower() in always_recurring_vendors


def get_is_insurance(transaction: Transaction) -> bool:
    """Check if the transaction is an insurance payment."""
    # use a regular expression with boundaries to match case-insensitive insurance
    # and insurance-related terms
    match = re.search(r"\b(insurance|insur|insuranc)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_utility(transaction: Transaction) -> bool:
    """Check if the transaction is a utility payment."""
    # use a regular expression with boundaries to match case-insensitive utility
    # and utility-related terms
    match = re.search(r"\b(utility|utilit|energy)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_phone(transaction: Transaction) -> bool:
    """Check if the transaction is a phone payment."""
    # use a regular expression with boundaries to match case-insensitive phone
    # and phone-related terms
    match = re.search(r"\b(at&t|t-mobile|verizon)\b", transaction.name, re.IGNORECASE)
    return bool(match)


@lru_cache(maxsize=1024)
def _parse_date(date_str: str) -> date:
    """Parse a date string into a datetime.date object."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    """
    Get the number of transactions in all_transactions that are on the same day of the month
    as transaction, within a tolerance of ±n_days_off.
    """
    transaction_day = _get_day(transaction.date)
    return len([
        t
        for t in all_transactions
        if t.id != transaction.id  # Exclude the transaction itself
        and abs(_get_day(t.date) - transaction_day) <= n_days_off
        and t.user_id == transaction.user_id  # Ensure the transaction belongs to the same user
        and t.name == transaction.name  # Ensure the transaction has the same name
    ])


def get_n_transactions_days_apart(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> int:
    """
    Get the number of transactions in all_transactions that are within n_days_off of
    being n_days_apart from transaction.
    """
    transaction_date = _parse_date(transaction.date)
    count = 0

    for t in all_transactions:
        days_difference = abs((_parse_date(t.date) - transaction_date).days)
        if abs(days_difference - n_days_apart) <= n_days_off:
            count += 1

    return count


def get_pct_transactions_days_apart(
    transaction: Transaction, all_transactions: list[Transaction], n_days_apart: int, n_days_off: int
) -> float:
    """
    Get the percentage of transactions in all_transactions that are within
    n_days_off of being n_days_apart from transaction
    """
    return get_n_transactions_days_apart(transaction, all_transactions, n_days_apart, n_days_off) / len(
        all_transactions
    )


def _get_day(date: str) -> int:
    """Get the day of the month from a transaction date."""
    return int(date.split("-")[2])


def get_pct_transactions_same_day(
    transaction: Transaction, all_transactions: list[Transaction], n_days_off: int
) -> float:
    """Get the percentage of transactions in all_transactions that are on the same day of the month as transaction"""
    return get_n_transactions_same_day(transaction, all_transactions, n_days_off) / len(all_transactions)


def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in 99"""
    return (transaction.amount * 100) % 100 == 99


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions)


def get_is_common_subscription_amount(transaction: Transaction) -> bool:
    """Returns True if the amount is a common subscription price."""
    common_amounts = {4.99, 5.99, 9.99, 12.99, 14.99, 19.99, 49.99, 99.99}
    return transaction.amount in common_amounts


def get_occurs_same_week(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """Checks if the transaction occurs in the same week of the month across multiple months."""
    transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    transaction_week = transaction_date.day // 7  # Determine which week in the month (0-4)

    same_week_count = sum(
        1
        for t in transactions
        if t.name == transaction.name and datetime.strptime(t.date, "%Y-%m-%d").day // 7 == transaction_week
    )

    return same_week_count >= 2  # True if found at least twice


def get_is_similar_name(
    transaction: Transaction, transactions: list[Transaction], similarity_threshold: float = 0.6
) -> bool:
    """Checks if a transaction has a similar name to other past transactions."""
    for t in transactions:
        similarity = difflib.SequenceMatcher(None, transaction.name.lower(), t.name.lower()).ratio()
        if similarity >= similarity_threshold:
            return True  # If a close match is found, return True
    return False


def get_is_fixed_interval(transaction: Transaction, transactions: list[Transaction], margin: int = 1) -> bool:
    """Returns True if a transaction recurs at fixed intervals (weekly, bi-weekly, monthly)."""
    transaction_dates = sorted([
        datetime.strptime(t.date, "%Y-%m-%d") for t in transactions if t.name == transaction.name
    ])

    if len(transaction_dates) < 2:
        return False  # Not enough transactions to determine intervals

    intervals = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    return all(abs(interval - 30) <= margin for interval in intervals)  # Allow ±1 day for monthly intervals


def get_has_irregular_spike(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """
    Check if the transaction amount is significantly higher than the average amount
    for the same transaction name in the user's transaction history.
    """
    similar_transactions = [t for t in transactions if t.name == transaction.name]
    if not similar_transactions:
        return False

    average_amount = sum(t.amount for t in similar_transactions) / len(similar_transactions)
    return transaction.amount > average_amount * 1.5  # Spike threshold: 50% higher than average


def get_is_first_of_month(transaction: Transaction) -> bool:
    """
    Checks if a transaction occurs on the first day of the month.

    Args:
        transaction (Transaction): The transaction to check.

    Returns:
        bool: True if the transaction occurs on the first day of the month, False otherwise.
    """
    return transaction.date.split("-")[2] == "01"


###
def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "ends_in_99": get_ends_in_99(transaction),
        "amount": transaction.amount,
        "same_day_exact": get_n_transactions_same_day(transaction, all_transactions, 0),
        "pct_transactions_same_day": get_pct_transactions_same_day(transaction, all_transactions, 0),
        "same_day_off_by_1": get_n_transactions_same_day(transaction, all_transactions, 1),
        "same_day_off_by_2": get_n_transactions_same_day(transaction, all_transactions, 2),
        "14_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 14, 0),
        "pct_14_days_apart_exact": get_pct_transactions_days_apart(transaction, all_transactions, 14, 0),
        "14_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 14, 1),
        "pct_14_days_apart_off_by_1": get_pct_transactions_days_apart(transaction, all_transactions, 14, 1),
        "7_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 7, 0),
        "pct_7_days_apart_exact": get_pct_transactions_days_apart(transaction, all_transactions, 7, 0),
        "7_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 7, 1),
        "pct_7_days_apart_off_by_1": get_pct_transactions_days_apart(transaction, all_transactions, 7, 1),
        "is_insurance": get_is_insurance(transaction),
        "is_utility": get_is_utility(transaction),
        "is_phone": get_is_phone(transaction),
        "is_always_recurring": get_is_always_recurring(transaction),
        # Newly Added Features
        "is_common_subscription_amount": get_is_common_subscription_amount(transaction),
        "occurs_same_week": get_occurs_same_week(transaction, all_transactions),
        "is_similar_name": get_is_similar_name(transaction, all_transactions),
        "is_fixed_interval": get_is_fixed_interval(transaction, all_transactions),
        "has_irregular_spike": get_has_irregular_spike(transaction, all_transactions),
        "is_first_of_month": get_is_first_of_month(transaction),
    }
