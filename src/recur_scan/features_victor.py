from datetime import datetime

import numpy as np

from recur_scan.transactions import Transaction


def get_avg_days_between(all_transactions: list[Transaction]) -> float:
    """Calculate average days between transactions."""
    if len(all_transactions) < 2:
        return 0.0
    dates = sorted([datetime.strptime(t.date, "%Y-%m-%d") for t in all_transactions])
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    return float(np.mean(intervals)) if intervals else 0.0


def interval_variability(all_transactions: list[Transaction]) -> float:
    """Calculate sample standard deviation of transaction intervals."""
    if len(all_transactions) < 2:
        return 0.0
    dates = sorted([datetime.strptime(t.date, "%Y-%m-%d") for t in all_transactions])
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    return float(np.std(intervals, ddof=1)) if intervals else 0.0


def amount_cluster_count(all_transactions: list[Transaction], tolerance: float = 0.05) -> float:
    """Count clusters of transaction amounts within tolerance."""
    if not all_transactions:
        return 0.0
    amounts = [t.amount for t in all_transactions]
    if not amounts:
        return 0.0
    clusters = []
    sorted_amounts = sorted(amounts)
    current_cluster = [sorted_amounts[0]]
    for i in range(1, len(sorted_amounts)):
        if abs(sorted_amounts[i] - current_cluster[-1]) <= current_cluster[-1] * tolerance:
            current_cluster.append(sorted_amounts[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [sorted_amounts[i]]
    clusters.append(current_cluster)
    return len(clusters)


def recurring_day_of_month(all_transactions: list[Transaction]) -> float:
    """Check if transactions occur on consistent days of the month."""
    days = [datetime.strptime(t.date, "%Y-%m-%d").day for t in all_transactions]
    if not days:
        return 0.0
    most_common_day = max(set(days), key=days.count)
    return days.count(most_common_day) / len(days)


def near_interval_ratio(all_transactions: list[Transaction], tolerance: int = 5) -> float:
    """Calculate ratio of intervals near common periods (e.g., weekly, monthly)."""
    if len(all_transactions) < 2:
        return 0.0
    dates = sorted([datetime.strptime(t.date, "%Y-%m-%d") for t in all_transactions])
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    if not intervals:
        return 0.0
    common_intervals = [7, 14, 28, 30, 90, 180, 365]
    near_count = 0
    for interval in intervals:
        for common in common_intervals:
            if abs(interval - common) <= tolerance:
                near_count += 1
                break  # Count at most one match per interval
    return near_count / len(intervals)


def amount_stability_index(all_transactions: list[Transaction], tolerance: float = 0.1) -> float:
    """Calculate fraction of amounts within tolerance of the median."""
    if not all_transactions:
        return 0.0
    amounts = [t.amount for t in all_transactions]
    if not amounts:
        return 0.0
    median_amount = np.median(amounts)
    within_tolerance = len([amount for amount in amounts if abs(amount - median_amount) <= median_amount * tolerance])
    return within_tolerance / len(amounts)


def merchant_recurrence_score(all_transactions: list[Transaction], merchant_scores: dict[str, float]) -> float:
    """Return the merchant's recurrence score."""
    if not all_transactions or not merchant_scores:
        return 0.0
    merchant = all_transactions[0].name
    return merchant_scores.get(merchant, 0.0)


def sequence_length(all_transactions: list[Transaction]) -> float:
    """Return the number of transactions in the sequence."""
    return len(all_transactions)


def get_count_same_amount_monthly(all_transactions: list[Transaction], current_transaction: Transaction) -> float:
    """Count transactions for the same user, vendor, and amount within 25-35 days."""
    user_id = current_transaction.user_id
    vendor = current_transaction.name.lower()
    amount = current_transaction.amount
    current_date = datetime.strptime(current_transaction.date, "%Y-%m-%d")

    target_vendors = ["apple", "brigit", "cleo ai", "cleo"]

    if vendor not in target_vendors:
        return 0.0

    count = 0
    for t in all_transactions:
        if (
            t.user_id == user_id
            and t.name.lower() in target_vendors
            and t.amount == amount
            and t != current_transaction
        ):
            delta = abs((datetime.strptime(t.date, "%Y-%m-%d") - current_date).days)
            if 25 <= delta <= 35:
                count += 1
    return float(count)


def is_small_fixed_amount(current_transaction: Transaction) -> float:
    """Check if the transaction amount is small (≤$10) and subscription-like."""
    vendor = current_transaction.name.lower()
    amount = current_transaction.amount

    target_vendors = ["apple", "brigit", "cleo ai", "cleo"]

    if vendor not in target_vendors:
        return 0.0

    if amount <= 10 and (f"{amount:.2f}".endswith(".99") or f"{amount:.2f}".endswith(".00")):
        return 1.0
    return 0.0


def get_days_since_last_same_amount(all_transactions: list[Transaction], current_transaction: Transaction) -> float:
    """Calculate days since the last transaction for the same user, vendor, and amount."""
    user_id = current_transaction.user_id
    vendor = current_transaction.name.lower()
    amount = current_transaction.amount
    current_date = datetime.strptime(current_transaction.date, "%Y-%m-%d")

    target_vendors = ["apple", "brigit", "cleo ai", "cleo"]

    if vendor not in target_vendors:
        return 999.0

    min_days = 999
    for t in all_transactions:
        if (
            t.user_id == user_id
            and t.name.lower() in target_vendors
            and t.amount == amount
            and t != current_transaction
            and datetime.strptime(t.date, "%Y-%m-%d") < current_date
        ):
            days = (current_date - datetime.strptime(t.date, "%Y-%m-%d")).days
            if days < min_days:
                min_days = days
    return float(min_days)


def get_new_features(
    all_transactions: list[Transaction],
    merchant_scores: dict[str, float] | None = None,
    current_transaction: Transaction | None = None,
) -> list[tuple[str, float]]:
    """Extract new features for a transaction group."""
    if not all_transactions:
        return []
    merchant_scores = merchant_scores or {}
    features = [
        ("avg_days_between", get_avg_days_between(all_transactions)),
        ("interval_variability", interval_variability(all_transactions)),
        ("amount_cluster_count", amount_cluster_count(all_transactions, tolerance=0.05)),
        ("recurring_day_of_month", recurring_day_of_month(all_transactions)),
        ("near_interval_ratio", near_interval_ratio(all_transactions, tolerance=5)),
        ("amount_stability_index", amount_stability_index(all_transactions, tolerance=0.1)),
        ("merchant_recurrence_score", merchant_recurrence_score(all_transactions, merchant_scores)),
        ("sequence_length", sequence_length(all_transactions)),
    ]
    if current_transaction:
        features.extend([
            ("count_same_amount_monthly", get_count_same_amount_monthly(all_transactions, current_transaction)),
            ("is_small_fixed_amount", is_small_fixed_amount(current_transaction)),
            ("days_since_last_same_amount", get_days_since_last_same_amount(all_transactions, current_transaction)),
        ])
    return features
