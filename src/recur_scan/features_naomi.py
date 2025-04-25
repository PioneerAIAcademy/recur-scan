from statistics import mean, stdev

from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date


def get_is_monthly_recurring(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """Check if the transaction recurs monthly."""
    same_name_txns = [t for t in transactions if t.name == transaction.name and t.date != transaction.date]
    if len(same_name_txns) < 2:  # Require at least 2 prior transactions
        return False
    ref_date = parse_date(transaction.date)
    intervals = sorted([abs((parse_date(t.date) - ref_date).days) for t in same_name_txns])
    # Check if at least two intervals are approximately monthly (28-31 days)
    monthly_count = sum(1 for i in intervals if 28 <= i <= 31)
    return monthly_count >= 2  # Require at least 2 monthly intervals


def get_is_similar_amount(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """Check if the amount is similar to others (within 5%)."""
    same_name_txns = [t for t in transactions if t.name == transaction.name]
    if not same_name_txns:
        return False
    avg_amount = mean([t.amount for t in same_name_txns])
    return abs(transaction.amount - avg_amount) / (avg_amount or 1.0) <= 0.05  # Avoid division by zero


def get_transaction_interval_consistency(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Measure consistency of transaction intervals."""
    same_name_txns = sorted([t for t in transactions if t.name == transaction.name], key=lambda x: parse_date(x.date))
    if len(same_name_txns) < 3:  # Need at least 2 intervals (3 transactions)
        return 0.0 if len(same_name_txns) <= 1 else 0.5
    intervals = [
        (parse_date(same_name_txns[i].date) - parse_date(same_name_txns[i - 1].date)).days
        for i in range(1, len(same_name_txns))
    ]
    return 1.0 - (stdev(intervals) / mean(intervals) if intervals and mean(intervals) > 0 else 0.0)


def get_cluster_label(transaction: Transaction, transactions: list[Transaction]) -> int:
    """Simple clustering: 1 if similar to others, 0 if not."""
    same_name_txns = [t for t in transactions if t.name == transaction.name]
    return 1 if len(same_name_txns) > 1 and get_is_similar_amount(transaction, transactions) else 0


def get_subscription_keyword_score(transaction: Transaction) -> float:
    """Score based on subscription-related keywords."""
    name_lower = transaction.name.lower()
    always_recurring = {"netflix", "spotify", "disney+", "hulu", "amazon prime"}
    keywords = {"premium", "monthly", "plan", "subscription"}
    if name_lower in always_recurring:
        return 1.0
    if any(kw in name_lower for kw in keywords):
        return 0.8
    return 0.0


def get_recurring_confidence_score(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Calculate a confidence score for recurrence."""
    same_name_txns = [t for t in transactions if t.name == transaction.name]
    if not same_name_txns:
        return 0.0
    time_score = get_time_regularity_score(transaction, transactions)
    amount_score = 1.0 if get_is_similar_amount(transaction, transactions) else 0.5
    freq_score = min(1.0, len(same_name_txns) * 0.4)
    return max(0.0, min(1.0, (time_score * 0.5 + amount_score * 0.3 + freq_score * 0.2)))


def get_time_regularity_score(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Score based on regularity of transaction timing."""
    same_name_txns = sorted([t for t in transactions if t.name == transaction.name], key=lambda x: parse_date(x.date))
    if len(same_name_txns) < 2:
        return 0.0
    intervals = [
        (parse_date(same_name_txns[i].date) - parse_date(same_name_txns[i - 1].date)).days
        for i in range(1, len(same_name_txns))
    ]
    if not intervals:
        return 0.0
    avg_interval = mean(intervals)
    variance = sum(abs(x - avg_interval) for x in intervals) / len(intervals)
    return max(0.0, 1.0 - (3 * variance / max(avg_interval, 1)))


def get_outlier_score(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Calculate z-score to detect outliers."""
    same_name_txns = [t for t in transactions if t.name == transaction.name]
    if len(same_name_txns) < 2:
        return 0.0
    amounts = [t.amount for t in same_name_txns]
    avg = mean(amounts)
    std = stdev(amounts) if len(amounts) > 1 else 0.0  # Avoid stdev on single value
    return abs(transaction.amount - avg) / std if std > 0 else 0.0
