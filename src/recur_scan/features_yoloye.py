from datetime import datetime

from recur_scan.features_original import get_n_transactions_days_apart
from recur_scan.transactions import Transaction


def _get_days(date: str) -> int:
    """Convert a date string (YYYY-MM-DD) into days since epoch (Jan 1, 1970)."""
    return (datetime.strptime(date, "%Y-%m-%d") - datetime(1970, 1, 1)).days


def get_n_transactions_delayed(
    transaction: Transaction, all_transactions: list[Transaction], expected_interval: int, max_delay: int = 5
) -> int:
    """
    Count how many times a transaction happens later than expected but still follows a pattern.
    Parameters:
    - transaction: The transaction to check.
    - all_transactions: List of all transactions.
    - expected_interval: The expected number of days between transactions (e.g., 30 for monthly).
    - max_delay: The number of extra days allowed (default is 5 days).
    Returns:
    - Number of delayed transactions that still fit the expected interval.
    """
    n_txs = 0
    transaction_days = _get_days(transaction.date)

    for t in all_transactions:
        t_days = _get_days(t.date)
        days_diff = t_days - transaction_days

        # Check if the transaction is within the delayed period
        if expected_interval <= days_diff <= expected_interval + max_delay:
            n_txs += 1

    return n_txs


# 🚀 Predefined Intervals for Recurring Transactions
def get_delayed_weekly(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Find delayed weekly transactions (7 days ± 2 days)."""
    return get_n_transactions_delayed(transaction, all_transactions, expected_interval=7, max_delay=2)


def get_delayed_fortnightly(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Find delayed fortnightly transactions (14 days ± 3 days)."""
    return get_n_transactions_delayed(transaction, all_transactions, expected_interval=14, max_delay=3)


def get_delayed_monthly(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Find delayed monthly transactions (30 days ± 5 days)."""
    return get_n_transactions_delayed(transaction, all_transactions, expected_interval=30, max_delay=5)


def get_delayed_quarterly(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Find delayed quarterly transactions (90 days ± 7 days)."""
    return get_n_transactions_delayed(transaction, all_transactions, expected_interval=90, max_delay=7)


def get_delayed_semi_annual(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Find delayed semi-annual transactions (180 days ± 10 days)."""
    return get_n_transactions_delayed(transaction, all_transactions, expected_interval=180, max_delay=10)


def get_delayed_annual(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Find delayed annual transactions (365 days ± 15 days)."""
    return get_n_transactions_delayed(transaction, all_transactions, expected_interval=365, max_delay=15)


def get_n_transactions_early(
    transaction: Transaction, all_transactions: list[Transaction], expected_interval: int, max_early: int = 5
) -> int:
    """
    Count how many times a transaction happens earlier than expected but still follows a pattern.
    Parameters:
    - transaction: The transaction to check.
    - all_transactions: List of all transactions.
    - expected_interval: The expected number of days between transactions (e.g., 30 for monthly).
    - max_early: The number of days a transaction can occur earlier than expected (default is 5 days).
    Returns:
    - Number of early transactions that still fit the expected interval.
    """
    n_txs = 0
    transaction_days = _get_days(transaction.date)

    for t in all_transactions:
        t_days = _get_days(t.date)
        days_diff = t_days - transaction_days

        # Check if the transaction occurs before the expected interval
        if expected_interval - max_early <= days_diff < expected_interval:
            n_txs += 1

    return n_txs


def get_early_weekly(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Detects early weekly payments (7 days - 2 days = within 5-6 days)."""
    return get_n_transactions_early(transaction, all_transactions, expected_interval=7, max_early=2)


def get_early_fortnightly(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Detects early fortnightly payments (14 days - 3 days = within 11-13 days)."""
    return get_n_transactions_days_apart(transaction, all_transactions, 14, 3)


def get_early_monthly(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Detects early monthly payments (30 days - 5 days = within 25-29 days)."""
    return get_n_transactions_days_apart(transaction, all_transactions, 30, 5)


def get_early_quarterly(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Detects early quarterly payments (90 days - 7 days = within 83-89 days)."""
    return get_n_transactions_days_apart(transaction, all_transactions, 90, 7)


def get_early_semi_annual(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Detects early semi-annual payments (180 days - 10 days = within 170-179 days)."""
    return get_n_transactions_days_apart(transaction, all_transactions, 180, 10)


def get_early_annual(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Detects early annual payments (365 days - 15 days = within 350-364 days)."""
    return get_n_transactions_days_apart(transaction, all_transactions, 365, 15)
