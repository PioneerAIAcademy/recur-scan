import re
from datetime import date, datetime
from functools import lru_cache
from statistics import median, stdev
from typing import Any

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


def get_n_transactions_days_apart(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> int:
    """
    Get the number of transactions in all_transactions that are within n_days_off of
    being n_days_apart from transaction
    """
    n_txs = 0
    transaction_date = _parse_date(transaction.date)

    # Pre-calculate bounds for faster checking
    lower_remainder = n_days_apart - n_days_off
    upper_remainder = n_days_off

    for t in all_transactions:
        t_date = _parse_date(t.date)
        days_diff = abs((t_date - transaction_date).days)

        # Skip if the difference is less than minimum required
        if days_diff < n_days_apart - n_days_off:
            continue

        # Check if the difference is close to any multiple of n_days_apart
        remainder = days_diff % n_days_apart

        if remainder <= upper_remainder or remainder >= lower_remainder:
            n_txs += 1

    return n_txs


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


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    """Get the number of transactions in all_transactions that are on the same day of the month as transaction"""
    return len([t for t in all_transactions if abs(_get_day(t.date) - _get_day(transaction.date)) <= n_days_off])


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


# added by me
def get_total_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the total amount of all transactions"""
    return sum(t.amount for t in all_transactions)


def get_average_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the average amount of all transactions"""
    if not all_transactions:
        return 0.0
    return sum(t.amount for t in all_transactions) / len(all_transactions)


def get_max_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the maximum transaction amount"""
    if not all_transactions:
        return 0.0
    return max(t.amount for t in all_transactions)


def get_min_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the minimum transaction amount"""
    if not all_transactions:
        return 0.0
    return min(t.amount for t in all_transactions)


def get_transaction_count(all_transactions: list[Transaction]) -> int:
    """Get the total number of transactions"""
    return len(all_transactions)


def get_transaction_amount_std(all_transactions: list[Transaction]) -> float:
    """Get the standard deviation of transaction amounts"""
    if len(all_transactions) < 2:  # Standard deviation requires at least two data points
        return 0.0
    return stdev(t.amount for t in all_transactions)


def get_transaction_amount_median(all_transactions: list[Transaction]) -> float:
    """Get the median transaction amount"""
    if not all_transactions:
        return 0.0
    return median(t.amount for t in all_transactions)


def get_transaction_amount_range(all_transactions: list[Transaction]) -> float:
    """Get the range of transaction amounts (max - min)"""
    if not all_transactions:
        return 0.0
    return max(t.amount for t in all_transactions) - min(t.amount for t in all_transactions)


def get_unique_transaction_amount_count(all_transactions: list[Transaction]) -> int:
    """Get the number of unique transaction amounts"""
    return len({t.amount for t in all_transactions})


def get_transaction_amount_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the frequency of the transaction amount in all transactions"""
    return sum(1 for t in all_transactions if t.amount == transaction.amount)


def get_transaction_day_of_week(transaction: Transaction) -> int:
    """Get the day of the week for the transaction (0=Monday, 6=Sunday)"""
    return datetime.strptime(transaction.date, "%Y-%m-%d").weekday()


def get_transaction_time_of_day(transaction: Transaction) -> str:
    """Get the time of day for the transaction (morning, afternoon, evening, night)"""
    try:
        hour = datetime.strptime(transaction.date, "%Y-%m-%d %H:%M:%S").hour
    except ValueError:
        return "unknown"  # Default value for missing time

    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 24:
        return "evening"
    else:
        return "night"


def get_average_transaction_interval(all_transactions: list[Transaction]) -> float:
    """Get the average time interval (in days) between transactions"""
    if len(all_transactions) < 2:
        return 0.0
    intervals = [
        (
            datetime.strptime(all_transactions[i].date, "%Y-%m-%d")
            - datetime.strptime(all_transactions[i - 1].date, "%Y-%m-%d")
        ).days
        for i in range(1, len(all_transactions))
    ]
    return sum(intervals) / len(intervals)


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, Any]:
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
        "total_transaction_amount": get_total_transaction_amount(all_transactions),
        "average_transaction_amount": get_average_transaction_amount(all_transactions),
        "max_transaction_amount": get_max_transaction_amount(all_transactions),
        "min_transaction_amount": get_min_transaction_amount(all_transactions),
        "transaction_count": get_transaction_count(all_transactions),
        "transaction_amount_std": get_transaction_amount_std(all_transactions),
        "transaction_amount_median": get_transaction_amount_median(all_transactions),
        "transaction_amount_range": get_transaction_amount_range(all_transactions),
        "unique_transaction_amount_count": get_unique_transaction_amount_count(all_transactions),
        "transaction_amount_frequency": get_transaction_amount_frequency(transaction, all_transactions),
        "transaction_day_of_week": get_transaction_day_of_week(transaction),
        "transaction_time_of_day": get_transaction_time_of_day(transaction),
        "average_transaction_interval": get_average_transaction_interval(all_transactions),
    }
