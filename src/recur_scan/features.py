import re
from datetime import date, datetime
from functools import lru_cache

import numpy as np

from recur_scan.transactions import Transaction


def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring because of the vendor name - check lowercase match"""
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
    }
    return transaction.name.lower() in always_recurring_vendors


def get_is_insurance(transaction: Transaction) -> bool:
    """Check if the transaction is an insurance payment."""
    # use a regular expression with boundaries to match case-insensitive insurance
    # and insurance-related terms
    match = re.search(r"\b(insurance|insur|insuranc)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_utility(transaction: Transaction) -> bool:
    """Check if the transaction is a utility payment."""
    # use a regular expression with boundaries to match case-insensitive utility
    # and utility-related terms
    match = re.search(r"\b(utility|utilit|energy)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_phone(transaction: Transaction) -> bool:
    """Check if the transaction is a phone payment."""
    # use a regular expression with boundaries to match case-insensitive phone
    # and phone-related terms
    match = re.search(r"\b(at&t|t-mobile|verizon)\b", transaction.name, re.IGNORECASE)
    return bool(match)


@lru_cache(maxsize=1024)
def _parse_date(date_str: str) -> date:
    """Parse a date string into a datetime.date object."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def get_n_transactions_days_apart(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> int:
    """
    Get the number of transactions in all_transactions that are within n_days_off of
    being n_days_apart from transaction
    """
    n_txs = 0
    transaction_date = _parse_date(transaction.date)

    # Pre-calculate bounds for faster checking
    lower_remainder = n_days_apart - n_days_off
    upper_remainder = n_days_off

    for t in all_transactions:
        t_date = _parse_date(t.date)
        days_diff = abs((t_date - transaction_date).days)

        # Skip if the difference is less than minimum required
        if days_diff < n_days_apart - n_days_off:
            continue

        # Check if the difference is close to any multiple of n_days_apart
        remainder = days_diff % n_days_apart

        if remainder <= upper_remainder or remainder >= lower_remainder:
            n_txs += 1

    return n_txs


def get_pct_transactions_days_apart(
    transaction: Transaction, all_transactions: list[Transaction], n_days_apart: int, n_days_off: int
) -> float:
    """
    Get the percentage of transactions in all_transactions that are within
    n_days_off of being n_days_apart from transaction.
    """
    if not all_transactions:
        return 0.0
    n_matches = get_n_transactions_days_apart(transaction, all_transactions, n_days_apart, n_days_off)
    return n_matches / len(all_transactions)


def _get_day(date: str) -> int:
    """Get the day of the month from a transaction date."""
    return int(date.split("-")[2])


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    """Get the number of transactions in all_transactions that are on the same day of the month as transaction"""
    return len([t for t in all_transactions if abs(_get_day(t.date) - _get_day(transaction.date)) <= n_days_off])


def get_pct_transactions_same_day(
    transaction: Transaction, all_transactions: list[Transaction], n_days_off: int
) -> float:
    """Get the percentage of transactions in all_transactions that are on the same day of the month as transaction"""
    return get_n_transactions_same_day(transaction, all_transactions, n_days_off) / len(all_transactions)


def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in 99"""
    return bool((transaction.amount * 100) % 100 == 99)


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions)


# my features start from here
def get_is_weekly(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if the transaction occurs weekly."""
    transaction_dates = [_parse_date(t.date) for t in all_transactions if t.name == transaction.name]
    date_diffs = [abs((transaction_dates[i] - transaction_dates[i - 1]).days) for i in range(1, len(transaction_dates))]
    return any(diff == 7 for diff in date_diffs)


def get_is_monthly(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if the transaction occurs monthly."""
    transaction_dates = [_parse_date(t.date) for t in all_transactions if t.name == transaction.name]
    date_diffs = [abs((transaction_dates[i] - transaction_dates[i - 1]).days) for i in range(1, len(transaction_dates))]
    return any(28 <= diff <= 31 for diff in date_diffs)


def get_is_biweekly(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if the transaction occurs biweekly."""
    transaction_dates = [_parse_date(t.date) for t in all_transactions if t.name == transaction.name]
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


# def get_is_large_amount(transaction: Transaction) -> bool:
#     """Check if the transaction amount is large (e.g., greater than $100)."""
#     return transaction.amount > 100


# def get_vendor_name_similarity(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """Calculate the similarity of vendor names using Jaccard similarity."""
#     vendor_names = [t.name.lower() for t in all_transactions if t.name]
#     transaction_name_set = set(transaction.name.lower().split()) if transaction.name else set()
#     similarities = []

#     for name in vendor_names:
#         name_set = set(name.split())
#         union_size = len(transaction_name_set | name_set)
#         if union_size > 0:  # Avoid division by zero
#             similarity = len(transaction_name_set & name_set) / union_size
#             similarities.append(similarity)

#     return max(similarities) if similarities else 0.0


# def get_is_recurring_based_on_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
#     """Check if the transaction is recurring based on frequency analysis."""
#     vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
#     if len(vendor_transactions) < 3:
#         return False
#     transaction_dates = sorted([_parse_date(t.date) for t in vendor_transactions])
#     intervals = [
#         abs((transaction_dates[i] - transaction_dates[i - 1]).days)
#         for i in range(1, len(transaction_dates))
#     ]
#     most_common_interval = Counter(intervals).most_common(1)
#     return most_common_interval[0][1] >= 3 if most_common_interval else False


# def get_day_of_week(transaction: Transaction) -> int:
#     """Get the day of the week for the transaction (0=Monday, 6=Sunday)."""
#     return _parse_date(transaction.date).weekday()


# def get_time_of_month(transaction: Transaction) -> str:
#     """Categorize the transaction into early, mid, or late month."""
#     day = _get_day(transaction.date)
#     if day <= 10:
#         return "early"
#     elif day <= 20:
#         return "mid"
#     else:
#         return "late"


# def get_quarter_of_year(transaction: Transaction) -> int:
#     """Get the quarter of the year for the transaction (1=Q1, 4=Q4)."""
#     month = _parse_date(transaction.date).month
#     return (month - 1) // 3 + 1


def get_transaction_gap_stats(transaction: Transaction, all_transactions: list[Transaction]) -> tuple[float, float]:
    """
    Calculate the mean and variance of gaps (in days) between consecutive transactions for the same vendor.
    Returns (mean_gap, variance_gap).
    """
    transaction_dates = sorted([_parse_date(t.date) for t in all_transactions if t.name == transaction.name])
    if len(transaction_dates) < 2:
        return 0.0, 0.0
    gaps = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    return float(np.mean(gaps)), float(np.var(gaps))


# def get_vendor_popularity(transaction: Transaction, all_transactions: list[Transaction]) -> int:
#     """Count how many unique users have transactions with the same vendor."""
#     return len({t.user_id for t in all_transactions if t.name == transaction.name})


def get_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate the average frequency (in days) of transactions for the same vendor.
    Returns the average number of days between consecutive transactions.
    """
    transaction_dates = sorted([_parse_date(t.date) for t in all_transactions if t.name == transaction.name])
    if len(transaction_dates) < 2:
        return 0.0  # Not enough transactions to calculate frequency
    gaps = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    return float(np.mean(gaps))


def get_is_quarterly(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the transaction occurs quarterly.
    A transaction is considered quarterly if the difference between consecutive transactions is approximately 90 days.
    """
    transaction_dates = [_parse_date(t.date) for t in all_transactions if t.name == transaction.name]
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
    transaction_dates = sorted([_parse_date(t.date) for t in all_transactions if t.name == transaction.name])
    if len(transaction_dates) < 2:
        return 0.0  # Return 0.0 instead of infinity when there are insufficient data points
    intervals = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    return float(np.var(intervals))


def get_is_weekend_transaction(transaction: Transaction) -> bool:
    """
    Check if the transaction occurs on a weekend (Saturday or Sunday).
    """
    day_of_week = _parse_date(transaction.date).weekday()
    return day_of_week in {5, 6}  # 5 = Saturday, 6 = Sunday


def get_is_high_frequency_vendor(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the vendor has a high transaction frequency (e.g., daily or weekly).
    """
    transaction_dates = sorted([_parse_date(t.date) for t in all_transactions if t.name == transaction.name])
    if len(transaction_dates) < 2:
        return False
    intervals = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    average_interval = np.mean(intervals)
    return bool(average_interval <= 7)  # Explicitly cast to bool


def get_is_same_day_of_month(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the transaction consistently occurs on the same day of the month.
    """
    days = [_get_day(t.date) for t in all_transactions if t.name == transaction.name]
    return len(set(days)) == 1 if days else False


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    features = {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "ends_in_99": float(get_ends_in_99(transaction)),
        "amount": transaction.amount,
        "same_day_exact": get_n_transactions_same_day(transaction, all_transactions, 0),
        "pct_transactions_same_day": get_pct_transactions_same_day(transaction, all_transactions, 0),
        "same_day_off_by_1": get_n_transactions_same_day(transaction, all_transactions, 1),
        "same_day_off_by_2": get_n_transactions_same_day(transaction, all_transactions, 2),
        "14_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 14, 0),
        "pct_14_days_apart_exact": get_pct_transactions_days_apart(transaction, all_transactions, 14, 0),
        "14_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 14, 1),
        "pct_14_days_apart_off_by_1": get_pct_transactions_days_apart(transaction, all_transactions, 14, 1),
        "7_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 7, 0),
        "pct_7_days_apart_exact": get_pct_transactions_days_apart(transaction, all_transactions, 7, 0),
        "7_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 7, 1),
        "pct_7_days_apart_off_by_1": get_pct_transactions_days_apart(transaction, all_transactions, 7, 1),
        "is_insurance": float(get_is_insurance(transaction)),
        "is_utility": float(get_is_utility(transaction)),
        "is_phone": float(get_is_phone(transaction)),
        "is_always_recurring": float(get_is_always_recurring(transaction)),
        "is_weekly": float(get_is_weekly(transaction, all_transactions)),
        "is_monthly": float(get_is_monthly(transaction, all_transactions)),
        "is_biweekly": float(get_is_biweekly(transaction, all_transactions)),
        "vendor_transaction_count": get_vendor_transaction_count(transaction, all_transactions),
        "vendor_amount_variance": get_vendor_amount_variance(transaction, all_transactions),
        "is_round_amount": float(get_is_round_amount(transaction)),
        "is_small_amount": float(get_is_small_amount(transaction)),
        # "is_large_amount": float(get_is_large_amount(transaction)),
        # "vendor_name_similarity": get_vendor_name_similarity(transaction, all_transactions),
        # "is_recurring_based_on_frequency": float(get_is_recurring_based_on_frequency(transaction, all_transactions)),
        # "day_of_week": get_day_of_week(transaction),
        # "time_of_month": float(["early", "mid", "late"].index(get_time_of_month(transaction))),
        # "quarter_of_year": get_quarter_of_year(transaction),
        "transaction_gap_mean": get_transaction_gap_stats(transaction, all_transactions)[0],
        "transaction_gap_variance": get_transaction_gap_stats(transaction, all_transactions)[1],
        # "vendor_popularity": get_vendor_popularity(transaction, all_transactions),
        "transaction_frequency": get_transaction_frequency(transaction, all_transactions),
        "is_recurring_vendor": float(get_is_recurring_vendor(transaction)),
        "is_fixed_amount": float(get_is_fixed_amount(transaction, all_transactions)),
        "recurring_interval_score": get_recurring_interval_score(transaction, all_transactions),
        "is_weekend_transaction": float(get_is_weekend_transaction(transaction)),
        "is_high_frequency_vendor": float(get_is_high_frequency_vendor(transaction, all_transactions)),
        "is_same_day_of_month": float(get_is_same_day_of_month(transaction, all_transactions)),
    }
    return features
