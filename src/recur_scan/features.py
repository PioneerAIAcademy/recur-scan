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
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
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


# Osaseres features


def has_min_recurrence_period(
    transaction: Transaction,
    all_transactions: list[Transaction],
    min_days: int = 60,
) -> bool:
    """Check if transactions from the same vendor span at least `min_days`."""
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(vendor_txs) < 2:
        return False
    dates = sorted([_parse_date(t.date) for t in vendor_txs])
    return (dates[-1] - dates[0]).days >= min_days


def get_day_of_month_consistency(
    transaction: Transaction,
    all_transactions: list[Transaction],
    tolerance_days: int = 7,
) -> float:
    """Calculate the fraction of transactions within `tolerance_days` of the target day."""
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(vendor_txs) < 2:
        return 0.0
    target_day = _get_day(transaction.date)
    matches = 0
    for t in vendor_txs:
        day_diff = abs(_get_day(t.date) - target_day)
        if day_diff <= tolerance_days or day_diff >= 28 - tolerance_days:  # Handle month-end
            matches += 1
    return matches / len(vendor_txs)


def get_day_of_month_variability(
    transaction: Transaction,
    all_transactions: list[Transaction],
) -> float:
    """Measure consistency of day-of-month (lower = more consistent)."""
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(vendor_txs) < 2:
        return 31.0  # Max possible variability

    days = [_get_day(t.date) for t in vendor_txs]
    # Handle month-end transitions (e.g., 28th vs 1st)
    adjusted_days = []
    for day in days:
        if day > 28 and day < 31:  # Treat 28+, 1, 2, 3 as close
            adjusted_days.extend([day, day - 31])
        else:
            adjusted_days.append(day)
    return np.std(adjusted_days)  # type: ignore


def get_recurrence_confidence(
    transaction: Transaction,
    all_transactions: list[Transaction],
    decay_rate: float = 2,  # Higher = recent transactions matter more
) -> float:
    """Calculate a confidence score (0-1) based on weighted historical recurrences."""
    vendor_txs = sorted(
        [t for t in all_transactions if t.name.lower() == transaction.name.lower()],
        key=lambda x: x.date,
    )
    if len(vendor_txs) < 2:
        return 0.0

    confidence = 0.0
    for i in range(1, len(vendor_txs)):
        days_diff = (_parse_date(vendor_txs[i].date) - _parse_date(vendor_txs[i - 1].date)).days
        # Weight by decay_rate^(time ago) and normalize
        confidence += (decay_rate**i) * (1.0 if days_diff <= 35 else 0.0)

    return confidence / sum(decay_rate**i for i in range(1, len(vendor_txs)))


def is_weekday_consistent(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    weekdays = [_parse_date(t.date).weekday() for t in vendor_txs]  # Monday=0, Sunday=6
    return len(set(weekdays)) <= 2  # Allow minor drift (e.g., weekend vs. Monday)


def get_median_period(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    dates = sorted([_parse_date(t.date) for t in vendor_txs])
    if len(dates) < 2:
        return 0.0
    day_diffs = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    return float(np.median(day_diffs))  # Median is robust to outliers


# def is_recurring_transaction(
#     transaction: Transaction,
#     all_transactions: list[Transaction],
#     amount_tolerance: float = 0.5,
#     date_tolerance_days: int = 2,
#     min_recurrences: int = 2,
# ) -> bool:
#     """
#     Check if a transaction is recurring based on:
#     - Same vendor name.
#     - Similar amount (within tolerance).
#     - Evenly spaced dates (with tolerance).
#     - At least `min_recurrences` occurrences.
#     """
#     # Filter transactions for the same vendor
#     vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]

#     if len(vendor_txs) < min_recurrences:
#         return False  # Not enough occurrences to be recurring

#     # Check amount consistency (allow slight variations like taxes/fees)
#     amounts = [t.amount for t in vendor_txs]
#     amount_avg = mean(amounts)
#     if abs(transaction.amount - amount_avg) > amount_tolerance:
#         return False

#     # Parse dates and sort chronologically
#     dates = sorted([_parse_date(t.date) for t in vendor_txs])

#     # Calculate days between consecutive transactions
#     date_diffs = []
#     for i in range(1, len(dates)):
#         delta = (dates[i] - dates[i - 1]).days
#         date_diffs.append(delta)

#     if not date_diffs:
#         return False  # Only 1 transaction

#     # Check if spacings are roughly even (e.g., ~30 days for monthly)
#     avg_spacing = mean(date_diffs)
#     spacing_std = stdev(date_diffs) if len(date_diffs) > 1 else 0

#     # Allow small deviations (e.g., weekends/holidays)
#     if spacing_std > date_tolerance_days:
#         return False

#     return True


# def is_pareto_recurring(
#     transaction: Transaction,
#     all_transactions: list[Transaction],
#     threshold: float = 0.8,
# ) -> bool:
#     """Check if most of the vendor's transactions are recurring."""
#     vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
#     if len(vendor_txs) < 3:
#         return False

#     n_recurring = sum(
#         1
#         for t in vendor_txs
#         if is_recurring_transaction(t, all_transactions)
#     )
#     return n_recurring / len(vendor_txs) >= threshold


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
        # Osaseres features
        "has_min_recurrence_period": has_min_recurrence_period(transaction, all_transactions),
        "day_of_month_consistency": get_day_of_month_consistency(transaction, all_transactions),
        "day_of_month_variability": get_day_of_month_variability(transaction, all_transactions),
        "recurrence_confidence": get_recurrence_confidence(transaction, all_transactions),
        "median_period_days": get_median_period(transaction, all_transactions),
        # "is_pareto_recurring": is_pareto_recurring(transaction, all_transactions),
        # "is_recurring_transaction": is_recurring_transaction(transaction, all_transactions),
    }
