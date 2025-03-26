import re
from dataclasses import dataclass
from datetime import datetime

# Removed the conflicting import of Transaction


def get_is_always_recurring(transaction: "Transaction") -> bool:
    """Check if the transaction is always recurring because of the vendor name - check lowercase match"""
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
    }
    return transaction.name.lower() in always_recurring_vendors


def get_is_insurance(transaction: "Transaction") -> bool:
    """Check if the transaction is an insurance payment."""
    # use a regular expression with boundaries to match case-insensitive insurance
    # and insurance-related terms
    match = re.search(r"\b(insurance|insur|insuranc)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_utility(transaction: "Transaction") -> bool:
    """Check if the transaction is a utility payment."""
    # use a regular expression with boundaries to match case-insensitive utility
    # and utility-related terms
    match = re.search(r"\b(utility|utilit|energy)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_phone(transaction: "Transaction") -> bool:
    """Check if the transaction is a phone payment."""
    # use a regular expression with boundaries to match case-insensitive phone
    # and phone-related terms
    match = re.search(r"\b(at&t|t-mobile|verizon)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def _get_days(date: str) -> int:
    """Get the number of days since the epoch of a transaction date."""
    # Assuming date is in the format YYYY-MM-DD
    # use the datetime module for an accurate determination
    # of the number of days since the epoch
    return (datetime.strptime(date, "%Y-%m-%d") - datetime(1970, 1, 1)).days


def get_n_transactions_days_apart(
    transaction: "Transaction",
    all_transactions: list["Transaction"],
    n_days_apart: int,
    n_days_off: int,
) -> int:
    """
    Get the number of transactions in all_transactions that are within n_days_off of
    being n_days_apart from transaction
    """
    n_txs = 0
    transaction_days = _get_days(transaction.date)

    for t in all_transactions:
        t_days = _get_days(t.date)
        days_diff = abs(t_days - transaction_days)
        # skip if the difference is less than n_days_apart - n_days_off
        if days_diff < n_days_apart - n_days_off:
            continue

        # Check if the difference is close to any multiple of n_days_apart
        # For example, with n_days_apart=14 and n_days_off=1, we want to count
        # transactions that are 13-15, 27-29, 41-43, etc. days apart
        remainder = days_diff % n_days_apart

        if remainder <= n_days_off or (n_days_apart - remainder) <= n_days_off:
            n_txs += 1

    return n_txs


def _get_day(date: str) -> int:
    """Get the day of the month from a transaction date."""
    return int(date.split("-")[2])


def get_n_transactions_same_day(
    transaction: "Transaction", all_transactions: list["Transaction"], n_days_off: int
) -> int:
    """Get the number of transactions in all_transactions that are on the same day of the month as transaction"""
    return len([t for t in all_transactions if abs(_get_day(t.date) - _get_day(transaction.date)) <= n_days_off])


def get_ends_in_99(transaction: "Transaction") -> bool:
    """Check if the transaction amount ends in 99"""
    return (transaction.amount * 100) % 100 == 99


def get_n_transactions_same_amount(transaction: "Transaction", all_transactions: list["Transaction"]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: "Transaction", all_transactions: list["Transaction"]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions)


def get_features(transaction: "Transaction", all_transactions: list["Transaction"]) -> dict[str, float | int]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "ends_in_99": get_ends_in_99(transaction),
        "amount": transaction.amount,
        "same_day_exact": get_n_transactions_same_day(transaction, all_transactions, 0),
        "same_day_off_by_1": get_n_transactions_same_day(transaction, all_transactions, 1),
        "same_day_off_by_2": get_n_transactions_same_day(transaction, all_transactions, 2),
        "14_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 14, 0),
        "14_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 14, 1),
        "7_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 7, 0),
        "7_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 7, 1),
        "is_insurance": get_is_insurance(transaction),
        "is_utility": get_is_utility(transaction),
        "is_phone": get_is_phone(transaction),
        "is_always_recurring": get_is_always_recurring(transaction),
    }


def get_n_transactions_same_description(transaction: "Transaction", all_transactions: list["Transaction"]) -> int:
    """Get the number of transactions in all_transactions with the same description as transaction"""
    return len([t for t in all_transactions if t.description == transaction.description])  # type: ignore


def get_percent_transactions_same_description(
    transaction: "Transaction", all_transactions: list["Transaction"]
) -> float:
    """Get the percentage of transactions in all_transactions with the same description as transaction"""
    if not all_transactions:
        return 0.0
    n_same_description = len([t for t in all_transactions if t.description == transaction.description])  # type: ignore
    return n_same_description / len(all_transactions)


def get_transaction_frequency(transaction: "Transaction", all_transactions: list["Transaction"]) -> float:
    """Calculate the average number of days between occurrences of this transaction."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 2:
        return 0.0  # Not enough data to calculate frequency

    dates = sorted([_get_days(t.date) for t in same_transactions])
    intervals = [dates[i] - dates[i - 1] for i in range(1, len(dates))]
    return sum(intervals) / len(intervals)


# def get_amount_variability(transaction, transactions):
#     """
#     Calculate the population standard deviation of amounts for transactions with the same description.
#     """
#     same_description_transactions = [t.amount for t in transactions if t.name == transaction.name]
#     if len(same_description_transactions) < 2:
#         return 0.0
#     return statistics.stdev(same_description_transactions)

def get_day_of_month_consistency(transaction: "Transaction", all_transactions: list["Transaction"]) -> float:
    """Calculate the consistency of the day of the month for transactions with the same name."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 2:
        return 0.0  # Not enough data to calculate consistency

    days = [_get_day(t.date) for t in same_transactions]
    most_common_day = max(set(days), key=days.count)
    return sum(1 for day in days if day == most_common_day) / len(days)


def interval_based_on_periodic(interval_stats: dict[str, float]) -> float:
    """Calculate how closely time intervals match common periodic patterns (weekly, monthly, yearly).

    Scores range from 0 (no match) to 1 (perfect match) based on:
    - Proximity to target intervals (7, 30, or 365 days)
    - Consistency of intervals (standard deviation < 5 days)

    Args:
        interval_stats: Dictionary containing:
            - 'mean': Average interval in days
            - 'std': Standard deviation of intervals

    Returns:
        float: Match score between 0 and 1
    """
    # Handle edge cases
    if not interval_stats or interval_stats.get("mean", 0) == 0:
        return 0.0

    mean = interval_stats["mean"]
    std = interval_stats.get("std", float("inf"))  # Default to high std if missing

    # Common periodic patterns with their tolerances
    periodic_patterns = [
        (7, 2),  # Weekly: 7±2 days
        (30, 3),  # Monthly: 30±3 days
        (365, 10),  # Yearly: 365±10 days
    ]

    best_score = 0.0

    for target_days, tolerance in periodic_patterns:
        # Skip if intervals are too inconsistent
        if std >= 5:
            continue

        # Calculate how far we are from target (normalized)
        deviation = abs(mean - target_days) / target_days
        normalized_tolerance = tolerance / target_days

        # Calculate score (1 - normalized deviation)
        score = 1.0 - min(deviation / normalized_tolerance, 1.0)
        best_score = max(best_score, score)

    return best_score


@dataclass
class Transaction:
    amount: float
    name: str
    date: str  # Add the date attribute as a string in the format "YYYY-MM-DD"
    # Add other relevant fields as needed


def calculate_merchant_pattern_consistency(
    target_transaction: "Transaction", all_transactions: list["Transaction"], merchant_transactions: list["Transaction"]
) -> float:
    """Calculates how consistent a transaction amount/name pattern is for a merchant relative to all transactions.

    Measures what percentage of all transactions have the exact same amount and merchant name
    as the target transaction within the merchant's transaction history.

    Args:
        target_transaction: The transaction being evaluated
        all_transactions: Complete transaction history for context
        merchant_transactions: Filtered transactions just for this merchant

    Returns:
        Ratio between 0 (no matches) and 1 (all transactions match)
        0 if no transactions exist
    """
    if not all_transactions:
        return 0.0

    matching_count = sum(
        1 for t in merchant_transactions if t.amount == target_transaction.amount and t.name == target_transaction.name
    )

    return matching_count / len(all_transactions)
