from datetime import datetime
from statistics import mean, stdev

from recur_scan.transactions import Transaction

# class Transaction:
#     """A simple transaction class for type annotation."""

#     def __init__(self, id: int, user_id: str, name: str, date: str, amount: float) -> None:
#         self.id = id
#         self.user_id = user_id
#         self.name = name
#         self.date = date
#         self.amount = amount


def parse_date(date_str: str) -> datetime:
    """Parse a date string into a datetime object."""
    try:
        if "/" in date_str:
            return datetime.strptime(date_str, "%m/%d/%Y")
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return datetime(1970, 1, 1)


def get_n_transactions_same_amount(transaction: Transaction, transactions: list[Transaction]) -> int:
    """Count transactions with the same amount."""
    return sum(1 for t in transactions if t.amount == transaction.amount)


def get_percent_transactions_same_amount(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Percentage of transactions with the same amount."""
    if not transactions:
        return 0.0
    return get_n_transactions_same_amount(transaction, transactions) / len(transactions)


def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the amount ends in .99."""
    return str(transaction.amount).endswith(".99")


def get_n_transactions_same_day(transaction: Transaction, transactions: list[Transaction], tolerance: int) -> int:
    """Count transactions on the same day within tolerance."""
    ref_date = parse_date(transaction.date)
    return sum(1 for t in transactions if abs((parse_date(t.date) - ref_date).days) <= tolerance)


def get_pct_transactions_same_day(transaction: Transaction, transactions: list[Transaction], tolerance: int) -> float:
    """Percentage of transactions on the same day within tolerance."""
    if not transactions:
        return 0.0
    return get_n_transactions_same_day(transaction, transactions, tolerance) / len(transactions)


def get_n_transactions_days_apart(
    transaction: Transaction, transactions: list[Transaction], days: int, tolerance: int
) -> int:
    """Count transactions exactly 'days' apart within tolerance."""
    ref_date = parse_date(transaction.date)
    count = 0
    for t in transactions:
        delta = abs((parse_date(t.date) - ref_date).days)
        if delta != 0 and abs(delta - days) <= tolerance:
            count += 1
    return count


def get_pct_transactions_days_apart(
    transaction: Transaction, transactions: list[Transaction], days: int, tolerance: int
) -> float:
    """Percentage of transactions 'days' apart within tolerance."""
    if not transactions:
        return 0.0
    return get_n_transactions_days_apart(transaction, transactions, days, tolerance) / len(transactions)


def get_is_insurance(transaction: Transaction) -> bool:
    """Check if the transaction is insurance-related."""
    return "insurance" in transaction.name.lower()


def get_is_phone(transaction: Transaction) -> bool:
    """Check if the transaction is phone-related."""
    return any(kw in transaction.name.lower() for kw in {"at&t", "t-mobile", "verizon", "phone"})


def get_is_utility(transaction: Transaction) -> bool:
    """Check if the transaction is utility-related."""
    keywords = {"energy", "water", "electric", "gas"}
    name_lower = transaction.name.lower()
    return any(kw == name_lower or f" {kw} " in f" {name_lower} " for kw in keywords)


def get_is_always_recurring(transaction: Transaction, recurring_merchants: set[str]) -> int:
    """Check if the merchant is always recurring."""
    return 1 if transaction.name in recurring_merchants else 0


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
    return max(0.0, 1.0 - (3 * variance / avg_interval))


def get_outlier_score(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Calculate z-score to detect outliers."""
    same_name_txns = [t for t in transactions if t.name == transaction.name]
    if len(same_name_txns) < 2:
        return 0.0
    amounts = [t.amount for t in same_name_txns]
    avg = mean(amounts)
    std = stdev(amounts) if len(amounts) > 1 else 0.0  # Avoid stdev on single value
    return abs(transaction.amount - avg) / std if std > 0 else 0.0


def get_features(transaction: Transaction, transactions: list[Transaction]) -> dict[str, float]:
    """Extract all features for a transaction."""
    recurring_merchants = {"Netflix", "Spotify", "Disney+", "Hulu", "Amazon Prime"}
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, transactions),
        "pct_transactions_same_amount": get_percent_transactions_same_amount(transaction, transactions),
        "ends_in_99": float(get_ends_in_99(transaction)),
        "n_transactions_same_day": get_n_transactions_same_day(transaction, transactions, tolerance=0),
        "pct_transactions_same_day": get_pct_transactions_same_day(transaction, transactions, tolerance=0),
        "n_transactions_30_days_apart": get_n_transactions_days_apart(transaction, transactions, 30, 1),
        "pct_transactions_30_days_apart": get_pct_transactions_days_apart(transaction, transactions, 30, 1),
        "is_insurance": float(get_is_insurance(transaction)),
        "is_phone": float(get_is_phone(transaction)),
        "is_utility": float(get_is_utility(transaction)),
        "is_always_recurring": float(get_is_always_recurring(transaction, recurring_merchants)),
        "is_monthly_recurring": float(get_is_monthly_recurring(transaction, transactions)),
        "is_similar_amount": float(get_is_similar_amount(transaction, transactions)),
        "transaction_interval_consistency": get_transaction_interval_consistency(transaction, transactions),
        "cluster_label": float(get_cluster_label(transaction, transactions)),
        "subscription_keyword_score": get_subscription_keyword_score(transaction),
        "recurring_confidence_score": get_recurring_confidence_score(transaction, transactions),
        "time_regularity_score": get_time_regularity_score(transaction, transactions),
        "outlier_score": get_outlier_score(transaction, transactions),
    }
