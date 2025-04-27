import statistics
from typing import Any

import numpy as np

from recur_scan.transactions import Transaction
from recur_scan.utils import get_day, parse_date


def get_is_weekly(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if the transaction occurs approximately weekly (allowing some variance)."""
    transaction_dates = sorted([parse_date(t.date) for t in all_transactions if t.name == transaction.name])
    if len(transaction_dates) < 2:
        return False
    date_diffs = [abs((transaction_dates[i] - transaction_dates[i - 1]).days) for i in range(1, len(transaction_dates))]
    return any(6 <= diff <= 8 for diff in date_diffs)


def get_is_monthly(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if the transaction occurs approximately monthly (allowing some variance)."""
    transaction_dates = sorted([parse_date(t.date) for t in all_transactions if t.name == transaction.name])
    if len(transaction_dates) < 2:
        return False
    date_diffs = [abs((transaction_dates[i] - transaction_dates[i - 1]).days) for i in range(1, len(transaction_dates))]
    return any(28 <= diff <= 32 for diff in date_diffs)


def get_is_biweekly(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if the transaction occurs biweekly."""
    transaction_dates = [parse_date(t.date) for t in all_transactions if t.name == transaction.name]
    date_diffs = [abs((transaction_dates[i] - transaction_dates[i - 1]).days) for i in range(1, len(transaction_dates))]
    return any(diff == 14 for diff in date_diffs)


def get_vendor_transaction_count(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the total number of transactions for the vendor."""
    return len([t for t in all_transactions if t.name == transaction.name])


def get_vendor_amount_variance(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the variance of transaction amounts for the vendor."""
    amounts = [t.amount for t in all_transactions if t.name == transaction.name]
    return float(np.var(amounts)) if amounts else 0.0


def get_is_round_amount(transaction: Transaction) -> bool:
    """Check if the transaction amount is a round number."""
    return transaction.amount % 1 == 0


def get_is_small_amount(transaction: Transaction) -> bool:
    """Check if the transaction amount is small (e.g., less than $10)."""
    return transaction.amount < 10


def get_transaction_gap_stats(transaction: Transaction, all_transactions: list[Transaction]) -> tuple[float, float]:
    """
    Calculate the mean and variance of gaps (in days) between consecutive transactions for the same vendor.
    Returns (mean_gap, variance_gap).
    """
    transaction_dates = sorted([parse_date(t.date) for t in all_transactions if t.name == transaction.name])
    if len(transaction_dates) < 2:
        return 0.0, 0.0
    gaps = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    return float(np.mean(gaps)), float(np.var(gaps))


def get_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate the average frequency (in days) of transactions for the same vendor.
    Returns the average number of days between consecutive transactions.
    """
    transaction_dates = sorted([parse_date(t.date) for t in all_transactions if t.name == transaction.name])
    if len(transaction_dates) < 2:
        return 0.0  # Not enough transactions to calculate frequency
    gaps = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    return float(np.mean(gaps))


def get_is_quarterly(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the transaction occurs quarterly.
    A transaction is considered quarterly if the difference between consecutive transactions is approximately 90 days.
    """
    transaction_dates = [parse_date(t.date) for t in all_transactions if t.name == transaction.name]
    date_diffs = [abs((transaction_dates[i] - transaction_dates[i - 1]).days) for i in range(1, len(transaction_dates))]
    return any(85 <= diff <= 95 for diff in date_diffs)


def get_average_transaction_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate the average transaction amount for the vendor.
    """
    amounts = [t.amount for t in all_transactions if t.name == transaction.name]
    return float(np.mean(amounts)) if amounts else 0.0


def get_is_subscription_based(transaction: Transaction) -> bool:
    """
    Check if the transaction is related to subscription services.
    This is determined by matching the transaction name against a predefined list of subscription-related keywords.
    """
    subscription_keywords = {"subscription", "membership", "monthly", "annual", "recurring"}
    return any(keyword in transaction.name.lower() for keyword in subscription_keywords)


def get_is_recurring_vendor(transaction: Transaction) -> bool:
    """
    Check if the vendor is in a predefined list of vendors known for recurring transactions.
    """
    recurring_vendors = {"netflix", "spotify", "hulu", "amazon prime", "google storage"}
    return bool(transaction.name.lower() in recurring_vendors)


def get_is_fixed_amount(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the transaction amount is consistent across all transactions for the vendor.
    """
    amounts = [t.amount for t in all_transactions if t.name == transaction.name]
    return len(set(amounts)) == 1 if amounts else False


def get_recurring_interval_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate the variance of intervals (in days) between transactions for the vendor.
    A lower variance indicates a more consistent recurring pattern.
    """
    transaction_dates = sorted([parse_date(t.date) for t in all_transactions if t.name == transaction.name])
    if len(transaction_dates) < 2:
        return 0.0  # Return 0.0 instead of infinity when there are insufficient data points
    intervals = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    return float(np.var(intervals))


def get_is_weekend_transaction(transaction: Transaction) -> bool:
    """
    Check if the transaction occurs on a weekend (Saturday or Sunday).
    """
    day_of_week = parse_date(transaction.date).weekday()
    return day_of_week in {5, 6}  # 5 = Saturday, 6 = Sunday


def get_is_high_frequency_vendor(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the vendor has a high transaction frequency (e.g., daily or weekly).
    """
    transaction_dates = sorted([parse_date(t.date) for t in all_transactions if t.name == transaction.name])
    if len(transaction_dates) < 2:
        return False
    intervals = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    average_interval = np.mean(intervals)
    return bool(average_interval <= 7)  # Explicitly cast to bool


def get_is_same_day_of_month(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the transaction consistently occurs on the same day of the month.
    """
    days = [get_day(t.date) for t in all_transactions if t.name == transaction.name]
    return len(set(days)) == 1 if days else False


# New Features
# def get_avg_interval_for_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """Calculate the average number of days between similar transactions for the same user and name."""
#     from statistics import mean
#     transaction_dates = sorted(
#     [parse_date(t.date) for t in all_transactions if t.name == transaction.name and t.user_id == transaction.user_id]
#     )
#     if len(transaction_dates) < 2:
#         return 0.0
#     date_diffs = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
#     return mean(date_diffs)

# def get_amount_frequency_score(transaction: Transaction, all_transactions: list[Transaction],
#     window: int = 90) -> int:
#     """Count how often a similar amount occurs within the past 'window' days for this user."""
#     target_date = parse_date(transaction.date)
#     similar_amounts = [
#         t for t in all_transactions
#         if t.user_id == transaction.user_id
#         and abs(parse_date(t.date) - target_date).days <= window
#         and abs(t.amount - transaction.amount) <= (0.05 * transaction.amount)
#     ]
#     return len(similar_amounts)

# def get_name_repeat_count(transaction: Transaction, all_transactions: list[Transaction]) -> int:
#     """Count how many times the same name has been used by the same user."""
#     return sum(1 for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name)


# def get_is_regular_merchant_pattern(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
#     """Check if a merchant has a consistent interval of recurrence for a user."""
#     transaction_dates = sorted(
#     [parse_date(t.date) for t in all_transactions if t.name == transaction.name and t.user_id == transaction.user_id]
#     )
#     if len(transaction_dates) < 3:
#         return False
#     date_diffs = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
#     std_dev = statistics.stdev(date_diffs)
#     return std_dev < 5  # You can tune this threshold


# def get_amount_frequency_score(transaction: Transaction, all_transactions: list[Transaction], window: int = 30)
#     -> int:
#     """Count how many similar transactions occur within a time window."""
#     transaction_date = parse_date(transaction.date)
#     return sum(
#         1
#         for t in all_transactions
#         if t.name == transaction.name and abs((parse_date(t.date) - transaction_date).days) <= window
#     )


def get_amount_consistency_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Return consistency score of transaction amounts (lower is better)."""
    amounts = [t.amount for t in all_transactions if t.name == transaction.name]
    if not amounts:
        return 0.0
    mean_amount = sum(amounts) / len(amounts)
    variance = sum((a - mean_amount) ** 2 for a in amounts) / len(amounts)
    return variance


def get_median_days_between(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get median number of days between transactions of the same name."""
    transaction_dates = sorted([parse_date(t.date) for t in all_transactions if t.name == transaction.name])
    if len(transaction_dates) < 2:
        return 0.0
    date_diffs = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    return statistics.median(date_diffs)


# def get_std_dev_days_between(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """Get standard deviation of days between transactions of the same name."""
#     transaction_dates = sorted([parse_date(t.date) for t in all_transactions if t.name == transaction.name])
#     if len(transaction_dates) < 2:
#         return 0.0
#     date_diffs = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
#     if len(date_diffs) < 2:
#         return 0.0
#     return statistics.stdev(date_diffs)
# def get_days_since_last_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> int:
#     """Return days since the last transaction with the same name."""
#     transaction_date = parse_date(transaction.date)
#     previous_dates = [parse_date(t.date) for t in all_transactions if t.name == transaction.name
#     and parse_date(t.date),
#     < transaction_date]
#     if not previous_dates:
#         return -1
#     last_date = max(previous_dates)
#     return (transaction_date - last_date).days

# def get_regular_interval_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """Return regular interval score (lower is better)."""
#     transaction_dates = sorted(parse_date(t.date) for t in all_transactions if t.name == transaction.name)
#     if len(transaction_dates) < 2:
#         return 0.0
#     intervals = [(transaction_dates[i] - transaction_dates[i-1]).days for i in range(1, len(transaction_dates))]
#     mean_interval = sum(intervals) / len(intervals)
#     variance = sum((i - mean_interval) ** 2 for i in intervals) / len(intervals)
#     return variance

# def get_recent_transaction_count(transaction: Transaction, all_transactions: list[Transaction],
#     days: int = 90) -> int:
#     """Count how many similar transactions occurred in the past 'days' days."""
#     transaction_date = parse_date(transaction.date)
#     recent_transactions = [
#         t for t in all_transactions
#         if t.name == transaction.name and 0 <= (transaction_date - parse_date(t.date)).days <= days
#     ]
#     return len(recent_transactions)

# def get_similarity_to_previous_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """Return similarity of this amount to median previous amounts."""
#     transaction_date = parse_date(transaction.date)
#     previous_amounts = [t.amount for t in all_transactions if t.name == transaction.name and parse_date(t.date)
#     < transaction_date]
#     if not previous_amounts:
#         return 0.0
#     median_amount = sorted(previous_amounts)[len(previous_amounts) // 2]
#     similarity = 1 - abs(transaction.amount - median_amount) / (median_amount + 1e-5)
#     return max(0.0, similarity)
KNOWN_RECURRING_MERCHANTS = [
    "apple",
    "amazon",
    "amazon prime",
    "amazon prime video",
    "cleo",
    "albert",
    "disney+",
    "afterpay",
    "brght lending",
    "credit ninja",
    "cashnetusa",
    "lendswift",
    "tn farm mutual",
    "root insurance",
    "petsbestinsuranc",
    "hulu",
    "spotify",
    "netflix",
    "google",
    "microsoft",
    "venmo",
    "paypal",
    "cash app",
    "att",
    "verizon",
    "shell",
    "zoom",
    "adobe",
    "dropbox",
    "scrimba",
    "coursera",
    "udemy",
    "skillshare",
    "linkedin",
    "you tube premium",
    "starlink",
]


def get_is_known_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is from a known recurring vendor (case-insensitive)."""
    transaction_name = transaction.name.lower().strip()
    return any(merchant in transaction_name for merchant in KNOWN_RECURRING_MERCHANTS)


# def get_amount_stability_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """Calculate the standard deviation of amounts for same user and merchant."""
#     amounts = [
#         t.amount for t in all_transactions
#         if t.user_id == transaction.user_id and t.name == transaction.name
#     ]
#     if len(amounts) < 2:
#         return 1000.0  # Large std deviation if insufficient data
#     return statistics.stdev(amounts)


# def get_is_common_subscription_amount(transaction: Transaction, margin: float = 0.5) -> bool:
#     """
#     Check if the transaction amount is close to common subscription price points.

#     Args:
#         transaction: The transaction to check.
#         margin: Acceptable margin of error around common amounts (default 0.5).

#     Returns:
#         bool: True if amount is close to a common subscription amount.
#     """
#     common_amounts = {
#         4.99,
#         5.99,
#         6.99,
#         7.99,
#         8.99,
#         9.99,
#         10.99,
#         11.99,
#         12.99,
#         13.99,
#         14.99,
#         15.99,
#         17.99,
#         18.99,
#         19.99,
#         24.99,
#         29.99,
#         39.99,
#         49.99,
#         59.99,
#         79.99,
#         99.99,
#     }
#     rounded_amount = round(transaction.amount, 2)
#     return any(abs(rounded_amount - common) <= margin for common in common_amounts)


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, Any]:
    """Compute additional smarter features for a transaction."""
    features = {
        # "amount_frequency_score": get_amount_frequency_score(transaction, all_transactions, window=30),
        # "avg_interval": get_avg_interval_for_transaction(transaction, all_transactions),
        # "name_repeat_count": get_name_repeat_count(transaction, all_transactions),
        # "is_regular_merchant_pattern": get_is_regular_merchant_pattern(transaction, all_transactions),
        "amount_consistency_score": get_amount_consistency_score(transaction, all_transactions),
        "median_days_between": get_median_days_between(transaction, all_transactions),
        # "std_dev_days_between": get_std_dev_days_between(transaction, all_transactions),
        # "days_since_last_transaction": get_days_since_last_transaction(transaction, all_transactions),
        # "regular_interval_score": get_regular_interval_score(transaction, all_transactions),
        # "recent_transaction_count": get_recent_transaction_count(transaction, all_transactions),
        # "similarity_to_previous_amount": get_similarity_to_previous_amount(transaction, all_transactions),
        "is_known_recurring": get_is_known_recurring(transaction),
        # "amount_stability_score": get_amount_stability_score(transaction, all_transactions),
        # "is_common_subscription_amount": get_is_common_subscription_amount(transaction),
    }

    return features
