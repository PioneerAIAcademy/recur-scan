import math
import re
import statistics
from datetime import datetime
from statistics import mean, stdev

import numpy as np

from recur_scan.transactions import Transaction

# Helper function to get the number of days since the epoch


def _get_days(date: str) -> int:
    """Get the number of days since the epoch of the transaction date."""
    # Assuming date is in the format YYYY-MM-DD
    # use the datetime module for the accurate determination
    # of the number of days since the epoch
    return (datetime.strptime(date, "%Y-%m-%d") - datetime(1970, 1, 1)).days


# Other feature functions


def get_average_transaction_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate the average transaction amount for the same vendor.

    Args:
        transaction (Transaction): The transaction to analyze.
        all_transactions (list[Transaction]): List of all transactions.

    Returns:
        float: The average transaction amount for the vendor.
    """
    vendor_transactions = [t.amount for t in all_transactions if t.name == transaction.name]

    if not vendor_transactions:
        return 0.0  # Return 0 if there are no transactions for the vendor

    return sum(vendor_transactions) / len(vendor_transactions)  # Compute the average


def get_transaction_rate(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the frequency of transactions for the same vendor"""
    vendor_transactions = [
        t for t in all_transactions if t.name == transaction.name
    ]  # Filter transactions by vendor name
    if len(vendor_transactions) < 2:
        return 0.0  # Return 0 if there are less than 2 transactions
    intervals = [
        (
            datetime.strptime(vendor_transactions[i + 1].date, "%Y-%m-%d")
            - datetime.strptime(vendor_transactions[i].date, "%Y-%m-%d")
        ).days
        for i in range(len(vendor_transactions) - 1)  # Calculate intervals between consecutive transactions
    ]
    if not intervals or sum(intervals) == 0:
        return 0.0  # Return 0 if there are no intervals or the sum is 0
    return 1 / (sum(intervals) / len(intervals))  # Return the frequency


def get_dispersion_transaction_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the dispersion (variance) in transaction amounts for the same vendor."""
    vendor_transactions = [t.amount for t in all_transactions if t.name == transaction.name]

    if len(vendor_transactions) < 2:
        return 0.0  # Return 0 if there are less than 2 transactions

    mean_value = sum(vendor_transactions) / len(vendor_transactions)  # Compute mean
    variance = sum((x - mean_value) ** 2 for x in vendor_transactions) / len(vendor_transactions)  # Compute variance

    return variance


def get_median_variation_transaction_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the median absolute deviation (MAD) of transaction amounts for the same vendor"""
    vendor_transactions = [t.amount for t in all_transactions if t.name == transaction.name]

    if len(vendor_transactions) < 2:
        return 0.0  # Return 0 if there are less than 2 transactions

    median_value = statistics.median(vendor_transactions)  # Compute the median
    mad = statistics.median([abs(amount - median_value) for amount in vendor_transactions])  # Compute MAD

    return float(mad)  # Return MAD


def get_variation_ratio(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the coefficient of variation (CV) of transaction amounts for the same vendor"""
    vendor_transactions = [t.amount for t in all_transactions if t.name == transaction.name]

    if len(vendor_transactions) < 2:
        return 0.0  # Return 0 if there are less than 2 transactions

    mean_value = statistics.mean(vendor_transactions)  # Compute mean
    if mean_value == 0:
        return 0.0  # Avoid division by zero

    # Compute standard deviation (population std, same as np.std with ddof=0)
    variance = sum((x - mean_value) ** 2 for x in vendor_transactions) / len(vendor_transactions)
    std_dev = math.sqrt(variance)  # Compute standard deviation

    return float(std_dev / mean_value)  # Return CV


def get_is_always_recurring(transaction: Transaction) -> bool:
    """
    Check if the transaction is from a known recurring vendor.
    All transactions from these vendors are considered recurring.
    """
    # Use a regular expression with boundaries to match case-insensitive company names
    match = re.search(
        r"\b(netflix|spotify|google play|hulu|disney\+|youtube|adobe|microsoft|walmart\+|amazon prime)\b",
        transaction.name,
        re.IGNORECASE,
    )
    return bool(match)


def get_is_insurance(transaction: Transaction) -> bool:
    """Check if the transaction is from a known insurance company."""
    # Use a regular expression with boundaries to match case-insensitive company names
    match = re.search(
        r"\b(insur|geico|allstate|state farm|progressive|insur|insuranc)\b", transaction.name, re.IGNORECASE
    )
    return bool(match)


def get_is_utility(transaction: Transaction) -> bool:
    """Check if the transaction is from a known utility company."""
    # Use a regular expression with boundaries to match case-insensitive company names
    match = re.search(
        r"\b(water|electricity|gas|internet|cable|energy|utilit|utility|cable|electric|light|phone)\b",
        transaction.name,
        re.IGNORECASE,
    )
    return bool(match)


def get_year(transaction: Transaction) -> int:
    """Get the year for the transaction date."""
    try:
        return datetime.strptime(transaction.date, "%Y-%m-%d").year
    except ValueError:
        return -1


def get_month(transaction: Transaction) -> int:
    """Get the month for the transaction date."""
    try:
        return datetime.strptime(transaction.date, "%Y-%m-%d").month
    except ValueError:
        return -1


def get_day(transaction: Transaction) -> int:
    """Get the day for the transaction date."""
    try:
        return datetime.strptime(transaction.date, "%Y-%m-%d").day
    except ValueError:
        return -1


def get_is_phone(transaction: Transaction) -> bool:
    """Check if the transaction is from a known mobile company."""
    mobile_companies = {"t-mobile", "at&t", "verizon", "boost mobile", "tello mobile", "spectrum"}
    return transaction.name.lower() in mobile_companies


def get_min_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the minimum transaction amount."""
    return min((t.amount for t in all_transactions), default=0.0)


def get_max_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the maximum transaction amount."""
    return max((t.amount for t in all_transactions), default=0.0)


def get_transaction_intervals(transactions: list[Transaction]) -> dict[str, float]:
    """
    Extracts time-based features for recurring transactions.
    - Computes average days between transactions.
    - Computes standard deviation of intervals.
    - Checks for flexible monthly recurrence (±7 days).
    - Identifies if transactions occur on the same weekday.
    - Checks if payment amounts are within ±5% of each other.
    """
    if len(transactions) < 2:
        return {
            "avg_days_between_transactions": 0.0,
            "std_dev_days_between_transactions": 0.0,
            "monthly_recurrence": 0,
            "same_weekday": 0,
            "same_amount": 0,
        }
    # Sort transactions by date
    dates = sorted([
        datetime.strptime(trans.date, "%Y-%m-%d") if isinstance(trans.date, str) else trans.date
        for trans in transactions
    ])

    # calculate days between each consecutive grouped transactions
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

    # compute average and standard deviation of transaction intervals
    avg_days = mean(intervals) if intervals else 0.0
    std_dev_days = stdev(intervals) if len(intervals) > 1 else 0.0

    # check for flexible monthly recurrence (±7 days)
    monthly_count = sum(
        1
        for gap in intervals
        if 23 <= gap <= 38  # 30 ± 7 days
    )
    monthly_recurrence = monthly_count / len(intervals) if intervals else 0.0

    # check if transactions occur on the same weekday
    weekdays = [date.weekday() for date in dates]  # Monday = 0, Sunday = 6
    same_weekday = 1 if len(set(weekdays)) == 1 else 0  # 1 if all transactions happen on the same weekday

    # check if payment amounts are within ±5% of each other
    amounts = [trans.amount for trans in transactions]

    base_amount = amounts[0]
    if base_amount == 0:
        consistent_amount = 0.0
    else:
        consistent_amount = sum(1 for amt in amounts if abs(amt - base_amount) / base_amount <= 0.05) / len(amounts)

    return {
        "avg_days_between_transactions": avg_days,
        "std_dev_days_between_transactions": std_dev_days,
        "monthly_recurrence": monthly_recurrence,
        "same_weekday": same_weekday,
        "same_amount": consistent_amount,
    }


def get_transactions_interval_stability(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Calculate the average interval between transactions for the same vendor."""
    # Filter transactions for the same vendor
    vendor_transactions = [t for t in transactions if t.name == transaction.name]
    if len(vendor_transactions) < 2:
        return 0.0  # No intervals to calculate

    # Sort transactions by date (convert date strings to datetime objects)
    vendor_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))

    # Calculate intervals in days
    intervals = [
        (
            datetime.strptime(vendor_transactions[i + 1].date, "%Y-%m-%d")
            - datetime.strptime(vendor_transactions[i].date, "%Y-%m-%d")
        ).days
        for i in range(len(vendor_transactions) - 1)
    ]
    # Return the average interval
    return sum(intervals) / len(intervals)


def get_n_transactions_same_vendor(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same vendor as transaction."""
    return sum(1 for t in all_transactions if t.name == transaction.name)


# New features to be added


def get_is_amazon_prime(transaction: Transaction) -> bool:
    """Check if the transaction is an Amazon Prime payment."""
    return "amazon prime" in transaction.name.lower()


def get_vendor_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the frequency band of transactions for this vendor (0=rare, 1=occasional, 2=frequent)."""
    count = sum(1 for t in all_transactions if t.name == transaction.name)
    if count > 3:  # 4+ transactions = frequent
        return 2
    elif count > 1:  # 2-3 transactions = occasional
        return 1
    return 0  # 1 transaction = rare


def get_vendor_transaction_recurring(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """
    Checks if a transaction is recurring based on same name, amount, and approximately monthly timing (±2 days).

    Args:
        transaction (Transaction): The transaction to analyze.
        all_transactions (list[Transaction]): List of all transactions.

    Returns:
        int: 1 if the transaction is recurring, 0 otherwise.
    """
    # Filter: same user, same vendor, same amount
    relevant = [
        t
        for t in all_transactions
        if t.user_id == transaction.user_id and t.name == transaction.name and t.amount == transaction.amount
    ]

    if len(relevant) < 3:
        return 0  # Can't detect a pattern with fewer than 3 transactions

    # Sort by date
    relevant = sorted(relevant, key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))
    dates = [datetime.strptime(t.date, "%Y-%m-%d") for t in relevant]

    # Find if dates occur approximately monthly (30 days ± 2 days)
    for i in range(len(dates) - 2):
        d1, d2, d3 = dates[i], dates[i + 1], dates[i + 2]
        interval1 = (d2 - d1).days
        interval2 = (d3 - d2).days

        if 28 <= interval1 <= 32 and 28 <= interval2 <= 32:
            check_date = datetime.strptime(transaction.date, "%Y-%m-%d")
            if check_date in [d1, d2, d3]:
                return 1

    return 0


# Feature 1: Likelihood of Recurrence Based on Last N Transactions


def get_likelihood_of_recurrence(transaction: Transaction, all_transactions: list[Transaction], n: int = 5) -> float:
    """
    Estimate the likelihood of recurrence based on the pattern of the last N transactions.

    Args:
        transaction (Transaction): The transaction to analyze.
        all_transactions (list[Transaction]): List of all transactions.
        n (int): Number of most recent transactions to consider.

    Returns:
        float: Likelihood score between 0.0 and 1.0.
    """
    vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(vendor_transactions) < n:
        return 0.0

    vendor_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))
    intervals = [
        (
            datetime.strptime(vendor_transactions[i + 1].date, "%Y-%m-%d")
            - datetime.strptime(vendor_transactions[i].date, "%Y-%m-%d")
        ).days
        for i in range(len(vendor_transactions) - 1)
    ]

    if len(intervals) < n - 1:
        return 0.0

    recent_intervals = intervals[-(n - 1) :]
    mean_interval = float(np.mean(recent_intervals))
    std_dev_interval = float(np.std(recent_intervals))

    if mean_interval == 0.0:  # Prevent division by zero
        return 0.0

    score = 1.0 if std_dev_interval < 5 else max(0.0, 1.0 - (std_dev_interval / mean_interval))
    return float(score)


def get_transaction_recency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """
    Calculate how many days have passed since the previous transaction from the same vendor.
    Returns -1 if there are no previous transactions for this vendor.
    """
    # Filter transactions for the same vendor and sort by date
    vendor_transactions = [
        t for t in all_transactions if t.name == transaction.name and t.user_id == transaction.user_id
    ]
    vendor_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))

    # Find the index of our transaction
    try:
        idx = next(i for i, t in enumerate(vendor_transactions) if t.id == transaction.id)
    except StopIteration:
        return -1

    # If this is the first transaction for this vendor
    if idx == 0:
        return -1

    # Calculate days between this transaction and the previous one
    prev_date = datetime.strptime(vendor_transactions[idx - 1].date, "%Y-%m-%d")
    current_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    delta = (current_date - prev_date).days

    return delta

    # Calculate days between this transaction and the previous one
    prev_date = datetime.strptime(vendor_transactions[idx - 1].date, "%Y-%m-%d").date()
    current_date = datetime.strptime(transaction.date, "%Y-%m-%d").date()
    delta = (current_date - prev_date).days

    return delta


# Feature 4: Mark AT&T Transactions as Recurring
def get_is_att_transaction(transaction: Transaction) -> bool:
    """
    Mark all AT&T or transactions containing 'AT&T' as recurring.
    """
    return "at&t" in transaction.name.lower()


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int | bool | float]:
    """Get the new features for the transaction."""

    # NOTE: Do NOT add features that are already in the original features.py file.
    # NOTE: Each feature should be on a separate line. Do not use **dict shorthand.
    return {
        "is_amazon_prime": get_is_amazon_prime(transaction),
        "vendor_transaction_frequency": get_vendor_transaction_frequency(transaction, all_transactions),
        "vendor_transaction_recurring": get_vendor_transaction_recurring(transaction, all_transactions),
        "likelihood_of_recurrence": get_likelihood_of_recurrence(transaction, all_transactions),
        "transaction_recency": get_transaction_recency(transaction, all_transactions),
        "is_att_transaction": get_is_att_transaction(transaction),
    }
