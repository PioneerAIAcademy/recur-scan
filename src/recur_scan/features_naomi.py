from datetime import datetime

import numpy as np

from recur_scan.transactions import Transaction


def _get_days(date: str) -> int:
    """Get the number of days since the epoch of a transaction date."""
    # Assuming date is in the format YYYY-MM-DD
    # use the datetime module for an accurate determination
    # of the number of days since the epoch
    return (datetime.strptime(date, "%Y-%m-%d") - datetime(1970, 1, 1)).days


def get_transaction_time_of_month(transaction: Transaction) -> int:
    """Categorize the transaction as early, mid, or late in the month."""
    day = int(transaction.date.split("-")[2])
    if day <= 10:
        return 0
    elif day <= 20:
        return 1
    else:
        return 2


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
