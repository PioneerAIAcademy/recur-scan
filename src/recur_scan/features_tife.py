from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date
from typing import cast

import numpy as np
from numpy import ndarray
from scipy.stats import mode

from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date


def get_transaction_frequency(all_transactions: list[Transaction]) -> float:
    if len(all_transactions) < 2:
        return 0.0
    dates: list[date] = sorted([parse_date(t.date) for t in all_transactions])
    intervals: list[int] = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    return float(np.mean(intervals)) if intervals else 0.0


def get_interval_consistency(all_transactions: list[Transaction]) -> float:
    if len(all_transactions) < 2:
        return 0.0
    dates: list[date] = sorted([parse_date(t.date) for t in all_transactions])
    intervals: list[int] = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    return float(np.std(intervals)) if intervals else 0.0


def get_amount_variability(all_transactions: list[Transaction]) -> float:
    if not all_transactions:
        return 0.0
    amounts: list[float] = [t.amount for t in all_transactions]
    mean_amount: float = float(np.mean(amounts))
    return float(np.std(amounts) / mean_amount) if mean_amount > 0 else 0.0


def get_amount_range(all_transactions: list[Transaction]) -> float:
    amounts = [t.amount for t in all_transactions]
    return max(amounts) - min(amounts) if amounts else 0.0


def get_transaction_count(all_transactions: list[Transaction]) -> int:
    return len(all_transactions)


def get_interval_mode(all_transactions: list[Transaction]) -> float:
    if len(all_transactions) < 2:
        return 0.0
    dates = sorted([parse_date(t.date) for t in all_transactions])
    intervals: list[int] = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    if not intervals:
        return 0.0
    mode_result = mode(intervals, keepdims=True)
    mode_array = cast(ndarray, mode_result.mode)
    if mode_array.size > 0:
        mode_value = int(mode_array.item(0))  # type: ignore[call-overload, operator]
        return float(mode_value)
    return 0.0


def get_normalized_interval_consistency(all_transactions: list[Transaction]) -> float:
    if len(all_transactions) < 2:
        return 0.0
    dates = sorted([parse_date(t.date) for t in all_transactions])
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    mean_interval = float(np.mean(intervals)) if intervals else 0.0
    # return float(np.std(intervals) / mean_interval) if mean_interval > 0 else 0.0
    std_dev = float(np.std(intervals)) if intervals else 0.0  # Ensure type is float
    return std_dev / mean_interval if mean_interval > 0 else 0.0


def get_days_since_last_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    prior_transactions = [
        t
        for t in all_transactions
        if parse_date(t.date) < parse_date(transaction.date) and t.amount == transaction.amount
    ]
    if not prior_transactions:
        return -1.0
    last_date = max([parse_date(t.date) for t in prior_transactions])
    return (parse_date(transaction.date) - last_date).days


def get_amount_relative_change(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    prior_transactions = [t for t in all_transactions if parse_date(t.date) < parse_date(transaction.date)]
    if not prior_transactions:
        return 0.0
    last_amount = prior_transactions[-1].amount
    return (transaction.amount - last_amount) / last_amount if last_amount > 0 else 0.0


def get_merchant_name_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    return sum(1 for t in all_transactions if t.name == transaction.name)


def get_interval_histogram(all_transactions: list[Transaction]) -> dict[str, float]:
    if len(all_transactions) < 2:
        return {"biweekly": 0.0, "monthly": 0.0}
    dates = sorted([parse_date(t.date) for t in all_transactions])
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    biweekly = sum(1 for i in intervals if 13 <= i <= 15) / len(intervals) if intervals else 0.0
    monthly = sum(1 for i in intervals if 28 <= i <= 31) / len(intervals) if intervals else 0.0
    return {"biweekly": biweekly, "monthly": monthly}


def get_amount_stability_score(all_transactions: list[Transaction]) -> float:
    if not all_transactions:
        return 0.0
    amounts = [t.amount for t in all_transactions]
    mean = np.mean(amounts)
    std = np.std(amounts)
    return sum(1 for a in amounts if abs(a - mean) <= std) / len(amounts) if std > 0 else 1.0


def get_dominant_interval_strength(all_transactions: list[Transaction]) -> float:
    if len(all_transactions) < 2:
        return 0.0
    dates = sorted([parse_date(t.date) for t in all_transactions])
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    if not intervals:
        return 0.0
    bins = [(6, 8), (13, 15), (28, 31)]
    counts = [sum(1 for i in intervals if lo <= i <= hi) for lo, hi in bins]
    max_count = max(counts) if counts else 0
    return max_count / len(intervals) if intervals else 0.0


def get_near_amount_consistency(
    transaction: Transaction, all_transactions: list[Transaction], threshold: float = 0.05
) -> float:
    if not all_transactions:
        return 0.0
    amounts = [t.amount for t in all_transactions]
    similar = sum(1 for a in amounts if abs(a - transaction.amount) / transaction.amount <= threshold)
    return similar / len(amounts)


def get_merchant_amount_signature(
    transaction: Transaction, all_transactions: list[Transaction], threshold: float = 0.05
) -> float:
    merchant_transactions = [t for t in all_transactions if t.name == transaction.name]
    if not merchant_transactions:
        return 0.0
    similar = sum(
        1 for t in merchant_transactions if abs(t.amount - transaction.amount) / transaction.amount <= threshold
    )
    return similar / len(merchant_transactions)


def get_amount_cluster_count(
    transaction: Transaction, all_transactions: list[Transaction], threshold: float = 0.05
) -> int:
    if len(all_transactions) < 2:
        return 0
    amounts = [t.amount for t in all_transactions]
    dates = sorted([parse_date(t.date) for t in all_transactions])
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    cluster_count = 0
    for i, a in enumerate(amounts):
        if abs(a - transaction.amount) / transaction.amount <= threshold and i > 0 and intervals[i - 1] > 5:
            cluster_count += 1
    return cluster_count


def get_transaction_density(all_transactions: list[Transaction]) -> float:
    if not all_transactions:
        return 0.0
    dates = [parse_date(t.date) for t in all_transactions]
    if len(dates) < 2:
        return 0.0
    time_span = (max(dates) - min(dates)).days
    return len(all_transactions) / time_span if time_span > 0 else 0.0
