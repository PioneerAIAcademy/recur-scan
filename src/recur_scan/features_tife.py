import random
from functools import lru_cache
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from datetime import date
import numpy as np
from numpy import ndarray
from scipy.stats import mode

from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date


def _precompute_dates_and_intervals(all_transactions: list[Transaction]) -> tuple[list["date"], list[int]]:
    """Precompute sorted dates and intervals to avoid redundant calculations."""
    if len(all_transactions) < 2:
        return [], []
    dates = sorted([parse_date(t.date) for t in all_transactions])
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    return dates, intervals


@lru_cache(maxsize=1000)
def _cached_merchant_transactions(merchant_name: str, transactions_tuple: tuple) -> list[Transaction]:
    """Cache merchant transactions to avoid repeated filtering."""
    transactions = list(transactions_tuple)
    return [t for t in transactions if t.name == merchant_name]


def get_transaction_frequency(all_transactions: list[Transaction]) -> float:
    _, intervals = _precompute_dates_and_intervals(all_transactions)
    return float(np.mean(intervals)) if intervals else 0.0


def get_interval_consistency(all_transactions: list[Transaction]) -> float:
    _, intervals = _precompute_dates_and_intervals(all_transactions)
    return float(np.std(intervals)) if intervals else 0.0


def get_amount_variability(all_transactions: list[Transaction]) -> float:
    if not all_transactions:
        return 0.0
    amounts = np.fromiter((t.amount for t in all_transactions), float)
    mean_amount = float(np.mean(amounts))
    return float(np.std(amounts) / mean_amount) if mean_amount > 0 else 0.0


def get_amount_range(all_transactions: list[Transaction]) -> float:
    if not all_transactions:
        return 0.0
    amounts = np.fromiter((t.amount for t in all_transactions), float)
    return float(np.max(amounts) - np.min(amounts)) if amounts.size else 0.0


def get_transaction_count(all_transactions: list[Transaction]) -> int:
    return len(all_transactions)


def get_interval_mode(all_transactions: list[Transaction]) -> float:
    _, intervals = _precompute_dates_and_intervals(all_transactions)
    if not intervals:
        return 0.0
    mode_result = mode(intervals, keepdims=True)
    mode_array = cast(ndarray, mode_result.mode)
    return float(mode_array.item(0)) if mode_array.size > 0 else 0.0


def get_normalized_interval_consistency(all_transactions: list[Transaction]) -> float:
    _, intervals = _precompute_dates_and_intervals(all_transactions)
    mean_interval = float(np.mean(intervals)) if intervals else 0.0
    std_dev = float(np.std(intervals)) if intervals else 0.0
    return std_dev / mean_interval if mean_interval > 0 else 0.0


def get_days_since_last_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    prior_transactions = (
        t
        for t in all_transactions
        if parse_date(t.date) < parse_date(transaction.date) and t.amount == transaction.amount
    )
    prior_dates = [parse_date(t.date) for t in prior_transactions]
    return (parse_date(transaction.date) - max(prior_dates)).days if prior_dates else -1.0


def get_amount_relative_change(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    prior_transactions = [t for t in all_transactions if parse_date(t.date) < parse_date(transaction.date)]
    if not prior_transactions:
        return 0.0
    last_amount = prior_transactions[-1].amount
    return (transaction.amount - last_amount) / last_amount if last_amount > 0 else 0.0


def get_merchant_name_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    return sum(1 for t in all_transactions if t.name == transaction.name)


def get_interval_histogram(all_transactions: list[Transaction]) -> dict[str, float]:
    _, intervals = _precompute_dates_and_intervals(all_transactions)
    if not intervals:
        return {"biweekly": 0.0, "monthly": 0.0}
    biweekly = sum(1 for i in intervals if 13 <= i <= 15) / len(intervals)
    monthly = sum(1 for i in intervals if 28 <= i <= 31) / len(intervals)
    return {"biweekly": biweekly, "monthly": monthly}


def get_amount_stability_score(all_transactions: list[Transaction]) -> float:
    if not all_transactions:
        return 0.0
    amounts = np.fromiter((t.amount for t in all_transactions), float)
    mean = np.mean(amounts)
    std = np.std(amounts)
    return sum(1 for a in amounts if abs(a - mean) <= std) / len(amounts) if std > 0 else 1.0


def get_dominant_interval_strength(all_transactions: list[Transaction]) -> float:
    _, intervals = _precompute_dates_and_intervals(all_transactions)
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
    amounts = np.fromiter((t.amount for t in all_transactions), float)
    similar = sum(1 for a in amounts if abs(a - transaction.amount) / max(transaction.amount, 0.01) <= threshold)
    return similar / len(amounts) if amounts.size else 0.0


def get_merchant_amount_signature(
    transaction: Transaction, all_transactions: list[Transaction], threshold: float = 0.05
) -> float:
    merchant_transactions = _cached_merchant_transactions(transaction.name, tuple(all_transactions))
    if len(merchant_transactions) > 50:
        merchant_transactions = random.sample(merchant_transactions, 50)
    similar = sum(
        1
        for t in merchant_transactions
        if abs(t.amount - transaction.amount) / max(transaction.amount, 0.01) <= threshold
    )
    return similar / len(merchant_transactions) if merchant_transactions else 0.0


def get_amount_cluster_count(
    transaction: Transaction, all_transactions: list[Transaction], threshold: float = 0.05
) -> int:
    dates, intervals = _precompute_dates_and_intervals(all_transactions)
    if not intervals:
        return 0
    amounts = np.fromiter((t.amount for t in all_transactions), float)
    cluster_count = 0
    for i, a in enumerate(amounts):
        if abs(a - transaction.amount) / max(transaction.amount, 0.01) <= threshold and i > 0 and intervals[i - 1] > 5:
            cluster_count += 1
    return cluster_count


def get_transaction_density(all_transactions: list[Transaction]) -> float:
    dates = [parse_date(t.date) for t in all_transactions]
    if len(dates) < 2:
        return 0.0
    time_span = (max(dates) - min(dates)).days
    return len(all_transactions) / time_span if time_span > 0 else 0.0


def get_amount_similarity_ratio(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    merchant_transactions = _cached_merchant_transactions(transaction.name, tuple(all_transactions))
    if len(merchant_transactions) > 50:
        merchant_transactions = random.sample(merchant_transactions, 50)
    amounts = np.fromiter((t.amount for t in merchant_transactions), float)
    if not amounts.size:
        return 0.0
    median_amount = float(np.median(amounts))
    threshold = max(0.1 * median_amount, 0.01)
    similar = sum(1 for a in amounts if abs(a - transaction.amount) <= threshold)
    return similar / len(amounts) if amounts.size else 0.0


def get_interval_cluster_strength(all_transactions: list[Transaction]) -> float:
    _, intervals = _precompute_dates_and_intervals(all_transactions)
    if not intervals:
        return 0.0
    bins = [(6, 8), (13, 15), (20, 24), (28, 31)]
    counts = [sum(1 for i in intervals if lo <= i <= hi) for lo, hi in bins]
    max_count = max(counts) if counts else 0
    return max_count / len(intervals) if intervals else 0.0


def get_merchant_recurrence_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    merchant_transactions = _cached_merchant_transactions(transaction.name, tuple(all_transactions))
    if len(merchant_transactions) < 2:
        return 0.0
    dates, intervals = _precompute_dates_and_intervals(merchant_transactions)
    if not intervals:
        return 0.0
    # If all intervals are zero (same-day transactions), return 0.0
    if all(interval == 0 for interval in intervals):
        return 0.0
    mean_interval = float(np.mean(intervals))
    std_interval = float(np.std(intervals, ddof=0))  # Explicitly use population standard deviation
    consistency = 1.0 - (std_interval / mean_interval if mean_interval > 0 else 0.0)
    frequency = len(merchant_transactions) / len(all_transactions)
    score = consistency * frequency
    return score


def get_day_of_month_consistency(all_transactions: list[Transaction]) -> float:
    if len(all_transactions) < 2:
        return 0.0
    days = np.fromiter((parse_date(t.date).day for t in all_transactions), int)
    mode_result = mode(days, keepdims=True)
    mode_array = cast(ndarray, mode_result.mode)
    if mode_array.size == 0:
        return 0.0
    mode_day = int(mode_array.item(0))
    count = sum(1 for d in days if abs(d - mode_day) <= 2)
    return count / len(days)


def get_long_term_recurrence(all_transactions: list[Transaction]) -> float:
    dates = [parse_date(t.date) for t in all_transactions]
    if len(dates) < 2:
        return 0.0
    time_span = (max(dates) - min(dates)).days
    return time_span / 365.0 if time_span > 0 else 0.0


def get_transaction_interval(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Compute the interval (days) to the previous transaction for the same merchant, if recurring pattern detected."""
    merchant_transactions = _cached_merchant_transactions(transaction.name, tuple(all_transactions))
    if len(merchant_transactions) < 3:
        return 0.0
    dates, intervals = _precompute_dates_and_intervals(merchant_transactions)
    if not intervals:
        return 0.0
    mean_interval = float(np.mean(intervals))
    std_interval = float(np.std(intervals))
    if mean_interval == 0 or std_interval == 0:
        return 0.0
    if std_interval / mean_interval > 0.5:
        return 0.0
    current_date = parse_date(transaction.date)
    prior_dates = [d for d in dates if d < current_date]
    if not prior_dates:
        return 0.0
    return float((current_date - max(prior_dates)).days)


def get_amount_deviation(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Compute the z-score of the transaction amount relative to the merchant's mean amount."""
    merchant_transactions = _cached_merchant_transactions(transaction.name, tuple(all_transactions))
    if not merchant_transactions:
        return 0.0
    amounts = np.fromiter((t.amount for t in merchant_transactions), float)
    mean_amount = float(np.mean(amounts))
    std_amount = float(np.std(amounts, ddof=0))  # Use population standard deviation
    if std_amount == 0 or np.isnan(std_amount):
        return 0.0
    return float((transaction.amount - mean_amount) / std_amount)


def get_vendor_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Compute the normalized transaction frequency for the merchant in a 6-month window."""
    merchant_transactions = _cached_merchant_transactions(transaction.name, tuple(all_transactions))
    if not merchant_transactions:
        return 0.0
    dates = [parse_date(t.date) for t in merchant_transactions]
    if not dates:
        return 0.0
    max_date = max(dates)
    min_date = max_date - np.timedelta64(180, "D")
    recent_transactions = [t for t in merchant_transactions if parse_date(t.date) >= min_date]
    total_transactions = len(all_transactions)
    return float(len(recent_transactions) / total_transactions) if total_transactions > 0 else 0.0


def get_user_spending_profile(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Compute the z-score of the transaction amount relative to the user's spending mean."""
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    if not user_transactions:
        return 0.0
    amounts = np.fromiter((t.amount for t in user_transactions), float)
    mean_amount = float(np.mean(amounts))
    std_amount = float(np.std(amounts, ddof=0))  # Use population standard deviation
    if std_amount == 0 or np.isnan(std_amount):
        return 0.0
    return float((transaction.amount - mean_amount) / std_amount)


def get_duplicate_transaction_indicator(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Check for potential duplicate transactions within 7 days with similar amount."""
    merchant_transactions = _cached_merchant_transactions(transaction.name, tuple(all_transactions))
    current_date = parse_date(transaction.date)
    for t in merchant_transactions:
        if t.id == transaction.id:
            continue
        date_diff = abs((parse_date(t.date) - current_date).days)
        amount_diff = abs(t.amount - transaction.amount) / max(transaction.amount, 0.01)
        if date_diff <= 7 and amount_diff <= 0.01:
            return 1.0
    return 0.0


def get_merchant_recurrence_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Check if the transaction's interval is consistent with the merchant's typical interval."""
    merchant_transactions = _cached_merchant_transactions(transaction.name, tuple(all_transactions))
    if len(merchant_transactions) < 3:
        return 0.0
    dates, intervals = _precompute_dates_and_intervals(merchant_transactions)
    if not intervals:
        return 0.0
    mean_interval = float(np.mean(intervals))
    std_interval = float(np.std(intervals))
    current_date = parse_date(transaction.date)
    prior_dates = [d for d in dates if d < current_date]
    if not prior_dates:
        return 0.0
    current_interval = float((current_date - max(prior_dates)).days)
    if std_interval == 0 or mean_interval == 0:
        return 0.0
    return 1.0 if abs(current_interval - mean_interval) > std_interval else 0.0


def get_vendor_category(transaction: Transaction) -> float:
    """Assign a numeric score based on the vendor category."""
    category_map = {
        "Apple": "Subscription",
        "Amazon": "Subscription",
        "Disney+": "Subscription",
        "Lendswift": "Loan",
        "Afterpay": "Loan",
        "CashNetUSA": "Loan",
        "GEICO": "Insurance",
        "Progressive Insurance": "Insurance",
        "Planet Fitness": "Membership",
        "Sam's Club": "Membership",
        "AT&T": "Utilities",
        "Verizon": "Utilities",
    }
    category_scores = {
        "Subscription": 1.0,
        "Loan": 2.0,
        "Insurance": 3.0,
        "Membership": 4.0,
        "Utilities": 5.0,
        "Other": 0.0,
    }
    category = category_map.get(transaction.name, "Other")
    return category_scores[category]


def get_transaction_amount_bin(transaction: Transaction) -> float:
    """Assign a numeric score based on the amount bin."""
    amount = transaction.amount
    if amount < 10:
        return 1.0  # Low
    elif amount <= 100:
        return 2.0  # Medium
    elif amount <= 500:
        return 3.0  # High
    else:
        return 4.0  # Very High


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    """Return a dictionary of features for the transaction, including new features."""
    return {
        "amount_similarity_ratio": get_amount_similarity_ratio(transaction, all_transactions),
        "interval_cluster_strength": get_interval_cluster_strength(all_transactions),
        "merchant_recurrence_score": get_merchant_recurrence_score(transaction, all_transactions),
        "day_of_month_consistency": get_day_of_month_consistency(all_transactions),
        "long_term_recurrence": get_long_term_recurrence(all_transactions),
        "transaction_interval": get_transaction_interval(transaction, all_transactions),
        "amount_deviation": get_amount_deviation(transaction, all_transactions),
        "vendor_transaction_frequency": get_vendor_transaction_frequency(transaction, all_transactions),
        "user_spending_profile": get_user_spending_profile(transaction, all_transactions),
        "duplicate_transaction_indicator": get_duplicate_transaction_indicator(transaction, all_transactions),
        "merchant_recurrence_consistency": get_merchant_recurrence_consistency(transaction, all_transactions),
        "vendor_category": get_vendor_category(transaction),
        "transaction_amount_bin": get_transaction_amount_bin(transaction),
    }
