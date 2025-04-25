from recur_scan.transactions import Transaction
from recur_scan.utils import get_day, parse_date


def get_n_transactions_same_description(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same description as transaction"""
    return len([t for t in all_transactions if t.name == transaction.name])  # type: ignore


def get_percent_transactions_same_description(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same description as transaction"""
    if not all_transactions:
        return 0.0
    n_same_description = len([t for t in all_transactions if t.name == transaction.name])  # type: ignore
    return n_same_description / len(all_transactions)


def get_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the average number of days between occurrences of this transaction."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 2:
        return 0.0  # Not enough data to calculate frequency

    dates = sorted([parse_date(t.date).toordinal() for t in same_transactions])
    intervals = [dates[i] - dates[i - 1] for i in range(1, len(dates))]
    return sum(intervals) / len(intervals)


def get_day_of_month_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the consistency of the day of the month for transactions with the same name."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 2:
        return 0.0  # Not enough data to calculate consistency

    days = [get_day(t.date) for t in same_transactions]
    most_common_day = max(set(days), key=days.count)
    return sum(1 for day in days if day == most_common_day) / len(days)
