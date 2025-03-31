import numpy as np

from recur_scan.transactions import Transaction
from recur_scan.utils import get_day, parse_date


def get_is_weekly(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if the transaction occurs weekly."""
    transaction_dates = [parse_date(t.date) for t in all_transactions if t.name == transaction.name]
    date_diffs = [abs((transaction_dates[i] - transaction_dates[i - 1]).days) for i in range(1, len(transaction_dates))]
    return any(diff == 7 for diff in date_diffs)


def get_is_monthly(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if the transaction occurs monthly."""
    transaction_dates = [parse_date(t.date) for t in all_transactions if t.name == transaction.name]
    date_diffs = [abs((transaction_dates[i] - transaction_dates[i - 1]).days) for i in range(1, len(transaction_dates))]
    return any(28 <= diff <= 31 for diff in date_diffs)


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
