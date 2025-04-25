import numpy as np

from recur_scan.transactions import Transaction
from recur_scan.utils import get_day, parse_date


def has_min_recurrence_period(
    transaction: Transaction,
    all_transactions: list[Transaction],
    min_days: int = 60,
) -> bool:
    """Check if transactions from the same vendor span at least `min_days`."""
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(vendor_txs) < 2:
        return False
    dates = sorted([parse_date(t.date) for t in vendor_txs])
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
    target_day = get_day(transaction.date)
    matches = 0
    for t in vendor_txs:
        day_diff = abs(get_day(t.date) - target_day)
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

    days = [get_day(t.date) for t in vendor_txs]
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
        days_diff = (parse_date(vendor_txs[i].date) - parse_date(vendor_txs[i - 1].date)).days
        # Weight by decay_rate^(time ago) and normalize
        confidence += (decay_rate**i) * (1.0 if days_diff <= 35 else 0.0)

    return confidence / sum(decay_rate**i for i in range(1, len(vendor_txs)))


def is_weekday_consistent(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    weekdays = [parse_date(t.date).weekday() for t in vendor_txs]  # Monday=0, Sunday=6
    return len(set(weekdays)) <= 2  # Allow minor drift (e.g., weekend vs. Monday)


def get_median_period(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    dates = sorted([parse_date(t.date) for t in vendor_txs])
    if len(dates) < 2:
        return 0.0
    day_diffs = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    return float(np.median(day_diffs))  # Median is robust to outliers
