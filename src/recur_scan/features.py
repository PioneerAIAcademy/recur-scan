# src/recur_scan/features.py
from datetime import datetime
from statistics import mean, stdev

from recur_scan.transactions import Transaction


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
    """
    Extract features for a transaction to help identify if it's recurring.

    Args:
        transaction: A Transaction object with attributes like amount, date, name.
        all_transactions: A list of Transaction objects for the same (user_id, name) pair.

    Returns:
        dict: A dictionary of features for the transaction.
    """
    features = {}

    # Existing Features
    features["n_transactions_same_amount"] = get_n_transactions_same_amount(transaction, all_transactions)
    features["percent_transactions_same_amount"] = get_percent_transactions_same_amount(transaction, all_transactions)

    # New Feature 1: Average Time Interval Between Transactions (in days)
    # Parse date strings to datetime objects
    sorted_transactions = sorted(all_transactions, key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))
    intervals = []
    for i in range(1, len(sorted_transactions)):
        delta = (
            datetime.strptime(sorted_transactions[i].date, "%Y-%m-%d")
            - datetime.strptime(sorted_transactions[i - 1].date, "%Y-%m-%d")
        ).days
        intervals.append(delta)
    features["avg_time_interval"] = mean(intervals) if intervals else 0.0

    # New Feature 2: Coefficient of Variation of Time Intervals
    if len(intervals) >= 2 and mean(intervals) != 0:
        features["time_interval_cv"] = stdev(intervals) / mean(intervals)
    else:
        features["time_interval_cv"] = 0.0

    # New Feature 3: Merchant Name Subscription Score
    subscription_scores = {
        "netflix": 1.0,
        "spotify": 1.0,
        "subscription": 1.0,
        "monthly": 1.0,
        "amazon prime": 0.9,
        "hulu": 0.9,
        "adobe": 0.9,
        "apple": 0.8,
        "store": 0.1,
        "shop": 0.1,  # Lower scores for less indicative terms
    }
    name_lower = transaction.name.lower()
    features["merchant_subscription_score"] = max(
        [score for keyword, score in subscription_scores.items() if keyword in name_lower] or [0.0]
    )

    # New Feature 4: Amount Range Consistency
    amounts = [t.amount for t in all_transactions]
    if amounts:
        mean_amount = mean(amounts)
        range_consistency = sum(1 for amt in amounts if abs(amt - mean_amount) <= 0.05 * mean_amount) / len(amounts)
        features["amount_range_consistency"] = range_consistency
    else:
        features["amount_range_consistency"] = 0.0

    return features
