from datetime import datetime
from statistics import median, stdev

from recur_scan.transactions import Transaction


def get_total_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the total amount of all transactions"""
    return sum(t.amount for t in all_transactions)


def get_average_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the average amount of all transactions"""
    if not all_transactions:
        return 0.0
    return sum(t.amount for t in all_transactions) / len(all_transactions)


def get_max_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the maximum transaction amount"""
    if not all_transactions:
        return 0.0
    return max(t.amount for t in all_transactions)


def get_min_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the minimum transaction amount"""
    if not all_transactions:
        return 0.0
    return min(t.amount for t in all_transactions)


def get_transaction_count(all_transactions: list[Transaction]) -> int:
    """Get the total number of transactions"""
    return len(all_transactions)


def get_transaction_amount_std(all_transactions: list[Transaction]) -> float:
    """Get the standard deviation of transaction amounts"""
    if len(all_transactions) < 2:  # Standard deviation requires at least two data points
        return 0.0
    return stdev(t.amount for t in all_transactions)


def get_transaction_amount_median(all_transactions: list[Transaction]) -> float:
    """Get the median transaction amount"""
    if not all_transactions:
        return 0.0
    return median(t.amount for t in all_transactions)


def get_transaction_amount_range(all_transactions: list[Transaction]) -> float:
    """Get the range of transaction amounts (max - min)"""
    if not all_transactions:
        return 0.0
    return max(t.amount for t in all_transactions) - min(t.amount for t in all_transactions)


def get_unique_transaction_amount_count(all_transactions: list[Transaction]) -> int:
    """Get the number of unique transaction amounts"""
    return len({t.amount for t in all_transactions})


def get_transaction_amount_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the frequency of the transaction amount in all transactions"""
    return sum(1 for t in all_transactions if t.amount == transaction.amount)


def get_transaction_day_of_week(transaction: Transaction) -> int:
    """Get the day of the week for the transaction (0=Monday, 6=Sunday)"""
    return datetime.strptime(transaction.date, "%Y-%m-%d").weekday()


def get_transaction_time_of_day(transaction: Transaction) -> int:
    """Get the time of day for the transaction (morning, afternoon, evening, night)"""
    try:
        hour = datetime.strptime(transaction.date, "%Y-%m-%d %H:%M:%S").hour
    except ValueError:
        return -1  # Default value for missing time

    if 6 <= hour < 12:
        return 1
    elif 12 <= hour < 18:
        return 2
    elif 18 <= hour < 24:
        return 3
    else:
        return 4


def get_average_transaction_interval(all_transactions: list[Transaction]) -> float:
    """Get the average time interval (in days) between transactions"""
    if len(all_transactions) < 2:
        return 0.0
    intervals = [
        (
            datetime.strptime(all_transactions[i].date, "%Y-%m-%d")
            - datetime.strptime(all_transactions[i - 1].date, "%Y-%m-%d")
        ).days
        for i in range(1, len(all_transactions))
    ]
    return sum(intervals) / len(intervals)
