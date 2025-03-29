import re
from datetime import date, datetime, timedelta
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
    }


# def get_days_since_last_transaction(
#     transaction: Transaction, all_transactions: list[Transaction], lookback_days: int = 90
# ) -> float:
#     """Get days since last similar transaction (same amount ±1%) within lookback window"""
#     similar_trans = [
#         t
#         for t in all_transactions
#         if t != transaction
#         and abs(t.amount - transaction.amount) / transaction.amount < 0.01
#         and (_parse_date(transaction.date) - _parse_date(t.date)).days <= lookback_days
#     ]
#     if not similar_trans:
#         return float("inf")
#     last_date = max(t.date for t in similar_trans)
#     return (_parse_date(transaction.date) - _parse_date(last_date)).days


# def get_days_since_last_transaction(transaction, transactions):
#     # Find all transactions for the same user after the current transaction
#     later_transactions = [t for t in transactions if t.user_id == transaction.user_id and t.date > transaction.date]

#     if not later_transactions:
#         return None

#     # Find the earliest subsequent transaction
#     next_transaction = min(later_transactions, key=lambda t: t.date)

#     # Calculate days difference
#     current_date = datetime.strptime(transaction.date, "%Y-%m-%d").date()
#     next_date = datetime.strptime(next_transaction.date, "%Y-%m-%d").date()
#     return (next_date - current_date).days


def get_day_of_week(transaction: Transaction) -> int:
    """Get day of week (0=Monday, 6=Sunday)"""
    return _parse_date(transaction.date).weekday()


def get_days_until_next_transaction(
    transaction: Transaction, all_transactions: list[Transaction], lookahead_days: int = 90
) -> float:
    """Get days until next similar transaction (same amount ±1%) within lookahead window"""
    similar_trans = [
        t
        for t in all_transactions
        if t != transaction
        and abs(t.amount - transaction.amount) / transaction.amount < 0.01
        and (_parse_date(t.date) - _parse_date(transaction.date)).days <= lookahead_days
    ]
    if not similar_trans:
        return float("inf")
    next_date = min(t.date for t in similar_trans)
    return (_parse_date(next_date) - _parse_date(transaction.date)).days


def get_periodicity_confidence(
    transaction: Transaction, all_transactions: list[Transaction], expected_period: int = 30
) -> float:
    """Calculate confidence score for periodicity (0-1)"""
    similar_trans = sorted([t for t in all_transactions if t != transaction], key=lambda x: x.date)

    if len(similar_trans) < 2:
        return 0.0

    deltas = []
    for i in range(1, len(similar_trans)):
        delta = (_parse_date(similar_trans[i].date) - _parse_date(similar_trans[i - 1].date)).days
        deltas.append(delta)

    if not deltas:
        return 0.0

    avg_delta = np.mean(deltas)
    std_delta = np.std(deltas)

    # Score based on how close average is to expected period and how consistent
    period_score = 1 - min(float(abs(avg_delta - expected_period) / expected_period), 1)
    consistency_score = 1 - min(float(std_delta) / expected_period, 1)

    return (period_score + consistency_score) / 2


def get_recurrence_streak(
    transaction: Transaction, all_transactions: list[Transaction], tolerance_days: int = 3
) -> int:
    """Count consecutive periods with similar transactions"""
    similar_trans = sorted([t for t in all_transactions if t != transaction], key=lambda x: x.date)

    if not similar_trans:
        return 0

    streak = 0
    expected_date = _parse_date(transaction.date) - timedelta(days=30)

    for t in reversed(similar_trans):
        if abs((expected_date - _parse_date(t.date)).days) <= tolerance_days:
            streak += 1
            expected_date = _parse_date(t.date) - timedelta(days=30)
        else:
            break

    return streak
