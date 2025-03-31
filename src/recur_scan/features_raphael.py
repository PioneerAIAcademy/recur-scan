import difflib
from datetime import datetime

from recur_scan.transactions import Transaction
from recur_scan.utils import get_day, parse_date


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    """
    Get the number of transactions in all_transactions that are on the same day of the month
    as transaction, within a tolerance of ±n_days_off.
    """
    transaction_day = get_day(transaction.date)
    return len([
        t
        for t in all_transactions
        if t.id != transaction.id  # Exclude the transaction itself
        and abs(get_day(t.date) - transaction_day) <= n_days_off
        and t.user_id == transaction.user_id  # Ensure the transaction belongs to the same user
        and t.name == transaction.name  # Ensure the transaction has the same name
    ])


def get_n_transactions_days_apart(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> int:
    """
    Get the number of transactions in all_transactions that are within n_days_off of
    being n_days_apart from transaction.
    """
    transaction_date = parse_date(transaction.date)
    count = 0

    for t in all_transactions:
        days_difference = abs((parse_date(t.date) - transaction_date).days)
        if abs(days_difference - n_days_apart) <= n_days_off:
            count += 1

    return count


def get_pct_transactions_days_apart(
    transaction: Transaction, all_transactions: list[Transaction], n_days_apart: int, n_days_off: int
) -> float:
    """
    Get the percentage of transactions in all_transactions that are within
    n_days_off of being n_days_apart from transaction
    """
    return get_n_transactions_days_apart(transaction, all_transactions, n_days_apart, n_days_off) / len(
        all_transactions
    )


def get_pct_transactions_same_day(
    transaction: Transaction, all_transactions: list[Transaction], n_days_off: int
) -> float:
    """Get the percentage of transactions in all_transactions that are on the same day of the month as transaction"""
    return get_n_transactions_same_day(transaction, all_transactions, n_days_off) / len(all_transactions)


def get_is_common_subscription_amount(transaction: Transaction) -> bool:
    """Returns True if the amount is a common subscription price."""
    common_amounts = {4.99, 5.99, 9.99, 12.99, 14.99, 19.99, 49.99, 99.99}
    return transaction.amount in common_amounts


def get_occurs_same_week(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """Checks if the transaction occurs in the same week of the month across multiple months."""
    transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    transaction_week = transaction_date.day // 7  # Determine which week in the month (0-4)

    same_week_count = sum(
        1
        for t in transactions
        if t.name == transaction.name and datetime.strptime(t.date, "%Y-%m-%d").day // 7 == transaction_week
    )

    return same_week_count >= 2  # True if found at least twice


def get_is_similar_name(
    transaction: Transaction, transactions: list[Transaction], similarity_threshold: float = 0.6
) -> bool:
    """Checks if a transaction has a similar name to other past transactions."""
    for t in transactions:
        similarity = difflib.SequenceMatcher(None, transaction.name.lower(), t.name.lower()).ratio()
        if similarity >= similarity_threshold:
            return True  # If a close match is found, return True
    return False


def get_is_fixed_interval(transaction: Transaction, transactions: list[Transaction], margin: int = 1) -> bool:
    """Returns True if a transaction recurs at fixed intervals (weekly, bi-weekly, monthly)."""
    transaction_dates = sorted([
        datetime.strptime(t.date, "%Y-%m-%d") for t in transactions if t.name == transaction.name
    ])

    if len(transaction_dates) < 2:
        return False  # Not enough transactions to determine intervals

    intervals = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    return all(abs(interval - 30) <= margin for interval in intervals)  # Allow ±1 day for monthly intervals


def get_has_irregular_spike(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """
    Check if the transaction amount is significantly higher than the average amount
    for the same transaction name in the user's transaction history.
    """
    similar_transactions = [t for t in transactions if t.name == transaction.name]
    if not similar_transactions:
        return False

    average_amount = sum(t.amount for t in similar_transactions) / len(similar_transactions)
    return transaction.amount > average_amount * 1.5  # Spike threshold: 50% higher than average


def get_is_first_of_month(transaction: Transaction) -> bool:
    """
    Checks if a transaction occurs on the first day of the month.

    Args:
        transaction (Transaction): The transaction to check.

    Returns:
        bool: True if the transaction occurs on the first day of the month, False otherwise.
    """
    return transaction.date.split("-")[2] == "01"
