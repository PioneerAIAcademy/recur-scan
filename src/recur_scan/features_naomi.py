from datetime import date, datetime
from statistics import mean, stdev
from typing import TypedDict

import pandas as pd

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


# New features are below
class TransactionDict(TypedDict):
    amount: float
    date: str
    name: str


class TestTransaction:
    def __init__(self, user_id: str, name: str, amount: float, date: str | date, timestamp: int | None = None) -> None:
        self.user_id = user_id
        self.name = name
        self.amount = amount
        self.date = date
        self.timestamp = timestamp


def get_date(txn: Transaction) -> date:
    if hasattr(txn, "timestamp") and txn.timestamp:
        return datetime.fromtimestamp(txn.timestamp).date()
    return datetime.strptime(txn.date, "%Y-%m-%d").date() if isinstance(txn.date, str) else txn.date


def days_since_last(transaction: Transaction, transactions: list[Transaction], grace_period: int = 0) -> int:
    """Calculate the number of days since the last transaction for a merchant."""

    tx_date = get_date(transaction)
    txns_sorted = sorted(transactions, key=lambda x: get_date(x), reverse=True)
    for txn in txns_sorted:
        txn_date = get_date(txn)
        if txn_date < tx_date:
            days = (tx_date - txn_date).days
            return max(days - grace_period, 30) if grace_period else days
    return -1


def get_amount_change_trend(transactions: list[TransactionDict]) -> float:
    """Calculate the trend (average change) in transaction amounts."""
    if len(transactions) < 2:
        return 0.0
    amounts = [txn["amount"] for txn in transactions]
    changes = [amounts[i] - amounts[i - 1] for i in range(1, len(amounts))]
    return sum(changes) / len(changes)


def get_txns_last_30_days(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in the last 30 days."""
    if isinstance(transaction.date, str):
        today = datetime.strptime(transaction.date, "%Y-%m-%d").date()
    else:
        today = transaction.date
    count = 0
    for t in all_transactions:
        if t.name != transaction.name:
            continue
        t_date = datetime.strptime(t.date, "%Y-%m-%d").date() if isinstance(t.date, str) else t.date
        days_diff = (today - t_date).days
        if 0 < days_diff <= 30:
            count += 1
    return count


def get_avg_amount_same_name(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Calculate the average amount for transactions with the same name."""
    same_name_txns = [t.amount for t in transactions if t.name == transaction.name]
    if not same_name_txns:
        return 0.0
    return sum(same_name_txns) / len(same_name_txns)


def get_empower_twice_monthly_count(transactions: list[Transaction]) -> int:
    """Count months with at least two Empower transactions."""
    df = pd.DataFrame([t.__dict__ for t in transactions])
    df_empower = df[df["name"].str.contains("Empower", case=False, na=False)].copy()
    if df_empower.empty:
        return 0
    df_empower["date"] = df_empower["date"].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%d") if isinstance(x, str) else x
    )
    df_empower["year"] = df_empower["date"].apply(lambda x: x.year)
    df_empower["month"] = df_empower["date"].apply(lambda x: x.month)
    monthly_counts = df_empower.groupby(["year", "month"]).size()
    return int((monthly_counts >= 2).sum())


def get_merchant_recurrence_score(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Calculate how consistently a merchant appears across months."""
    merchant_dates = [txn.date for txn in transactions if txn.name == transaction.name]
    if not merchant_dates:
        return 0.0
    parsed_dates = [datetime.strptime(d, "%Y-%m-%d") if isinstance(d, str) else d for d in merchant_dates]
    months = {(d.year, d.month) for d in parsed_dates}
    total_months = max((max(months)[0] - min(months)[0]) * 12 + (max(months)[1] - min(months)[1]) + 1, 1)
    return float(len(months) / total_months)


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int | bool | float]:
    """Compute all new features for a transaction."""
    return {
        "days_since_last": days_since_last(transaction, all_transactions),
        "amount_change_trend": get_amount_change_trend([
            TransactionDict(
                amount=txn.amount,
                date=(
                    datetime.strptime(txn.date, "%Y-%m-%d").strftime("%Y-%m-%d")
                    if isinstance(txn.date, str)
                    else f"{txn.date:%Y-%m-%d}"
                ),
                name=txn.name,
            )
            for txn in all_transactions
        ]),
        "txns_last_30_days": get_txns_last_30_days(transaction, all_transactions),
        "avg_amount_same_name": get_avg_amount_same_name(transaction, all_transactions),
        "empower_twice_monthly_count": get_empower_twice_monthly_count(all_transactions),
        "merchant_recurrence_score": get_merchant_recurrence_score(transaction, all_transactions),
        # "transaction_date": get_date(transaction, all_transactions),
    }
