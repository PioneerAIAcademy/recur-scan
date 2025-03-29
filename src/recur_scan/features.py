import re
from datetime import date, datetime
from functools import lru_cache

import numpy as np

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


# my feature start here#


def _get_days(date: str) -> int:
    """Get the number of days since the epoch of a transaction date."""
    # Assuming date is in the format YYYY-MM-DD
    # use the datetime module for an accurate determination
    # of the number of days since the epoch
    return (datetime.strptime(date, "%Y-%m-%d") - datetime(1970, 1, 1)).days


def get_transaction_time_of_month(transaction: Transaction) -> str:
    """Categorize the transaction as early, mid, or late in the month."""
    day = int(transaction.date.split("-")[2])
    if day <= 10:
        return "early"
    elif day <= 20:
        return "mid"
    else:
        return "late"


def get_transaction_amount_stability(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the standard deviation of transaction amounts for the same name.

    Note: This function uses numpy for calculating the standard deviation.
    """
    same_name_transactions = [t.amount for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0
    return float(np.std(same_name_transactions))


def get_time_between_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the average time gap (in days) between transactions with the same name."""
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0
    dates = sorted(_get_days(t.date) for t in same_name_transactions)
    intervals = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
    return sum(intervals) / len(intervals) if intervals else 0.0


def get_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the average frequency (in days) of transactions with the same name."""
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0
    dates = sorted(_get_days(t.date) for t in same_name_transactions)
    intervals = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
    return sum(intervals) / len(intervals)


def get_n_same_name_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Count transactions with the same name."""
    return len([t for t in all_transactions if t.name == transaction.name])


def get_irregular_periodicity(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate the standard deviation of time gaps (in days) between transactions with the same name.
    A higher value indicates irregular periodicity.

    Note: This function uses numpy for calculating the standard deviation.
    """
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0
    dates = sorted(_get_days(t.date) for t in same_name_transactions)
    intervals = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
    return float(np.std(intervals)) if intervals else 0.0


def get_irregular_periodicity_with_tolerance(
    transaction: Transaction, all_transactions: list[Transaction], tolerance: int = 5
) -> float:
    """
    Calculate the normalized standard deviation of time gaps (in days) between transactions with the same name,
    allowing for a tolerance in interval consistency.

    Note: This function uses numpy for calculating the standard deviation and median.
    """
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0

    dates = sorted(_get_days(t.date) for t in same_name_transactions)
    intervals = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
    if not intervals:
        return 0.0

    # Group intervals that are within the tolerance range
    interval_groups: list[list[int]] = []  # Added type annotation
    for interval in intervals:
        added = False
        for group in interval_groups:
            if abs(interval - group[0]) <= tolerance:
                group.append(interval)
                added = True
                break
        if not added:
            interval_groups.append([interval])

    # Find the largest group of intervals
    largest_group = max(interval_groups, key=len)
    largest_group_std = float(np.std(largest_group)) if len(largest_group) > 1 else 0.0  # Cast to float

    # Normalize by the median interval for scale invariance
    median_interval = float(np.median(intervals))  # Cast to float
    normalized_std = largest_group_std / median_interval if median_interval > 0 else 0.0

    return normalized_std


def get_user_transaction_frequency(user_id: str, all_transactions: list[Transaction]) -> float:
    """
    Calculate the average frequency (in days) of all transactions for a specific user.
    """
    user_transactions = [t for t in all_transactions if t.user_id == user_id]
    if len(user_transactions) < 2:
        return 0.0

    dates = sorted(_get_days(t.date) for t in user_transactions)
    intervals = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
    return sum(intervals) / len(intervals) if intervals else 0.0


def get_vendor_recurring_ratio(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate the ratio of recurring transactions to total transactions for the same vendor.
    """
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if not same_name_transactions:
        return 0.0
    recurring_count = len([t for t in same_name_transactions if t.amount == transaction.amount])
    return recurring_count / len(same_name_transactions)


def get_vendor_recurrence_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate the percentage of transactions from the same vendor that occur at regular intervals,
    allowing for a tolerance in interval consistency.
    """
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0

    # Sort dates in days
    dates = sorted(_get_days(t.date) for t in same_name_transactions)
    intervals = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
    if not intervals:
        return 0.0

    # Define a tolerance for "consistent" intervals (e.g., ±5 days)
    tolerance = 5  # Renamed to lowercase to fix N806
    # Group intervals that are within tolerance of each other
    interval_groups: dict[int, list[int]] = {}  # Added type annotation
    for interval in intervals:
        assigned = False
        for group_interval in interval_groups:
            if abs(interval - group_interval) <= tolerance:
                interval_groups[group_interval].append(interval)
                assigned = True
                break
        if not assigned:
            interval_groups[interval] = [interval]

    # Find the largest group of "consistent" intervals
    most_common_group_size = max(len(group) for group in interval_groups.values())
    return most_common_group_size / len(intervals)


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int | str]:
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
        ##
        "transaction_time_of_month": get_transaction_time_of_month(transaction),
        "transaction_amount_stability": get_transaction_amount_stability(transaction, all_transactions),
        "time_between_transactions": get_time_between_transactions(transaction, all_transactions),
        "transaction_frequency": get_transaction_frequency(transaction, all_transactions),
        "n_same_name_transactions": get_n_same_name_transactions(transaction, all_transactions),
        "irregular_periodicity": get_irregular_periodicity(transaction, all_transactions),
        "irregular_periodicity_with_tolerance": get_irregular_periodicity_with_tolerance(transaction, all_transactions),
        "user_transaction_frequency": get_user_transaction_frequency(transaction.user_id, all_transactions),
        "vendor_recurring_ratio": get_vendor_recurring_ratio(transaction, all_transactions),
        "vendor_recurrence_consistency": get_vendor_recurrence_consistency(transaction, all_transactions),
    }
