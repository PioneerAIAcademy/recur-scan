import statistics
from datetime import datetime

import numpy as np

from recur_scan.transactions import Transaction


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions)


def get_n_transactions_same_name(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same name as transaction"""
    return len([t for t in all_transactions if t.name == transaction.name])


def get_percent_transactions_same_name(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same name as transaction"""
    if not all_transactions:
        return 0.0
    n_same_name = len([t for t in all_transactions if t.name == transaction.name])
    return n_same_name / len(all_transactions)


def get_avg_amount_same_name(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the average amount of transactions in all_transactions with the same name as transaction"""
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if not same_name_transactions:
        return 0.0
    return sum(t.amount for t in same_name_transactions) / len(same_name_transactions)


def get_std_amount_same_name(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate the standard deviation of amounts for transactions in all_transactions
    that have the same name as the given transaction.

    Args:
        transaction (Transaction): The transaction to compare against.
        all_transactions (list[Transaction]): The list of all transactions.

    Returns:
        float: The standard deviation of amounts for transactions with the same name.
               Returns 0.0 if there are fewer than two such transactions.
    """
    # Filter transactions to find those with the same name
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]

    # If there are fewer than two transactions with the same name, return 0.0
    if len(same_name_transactions) < 2:
        return 0.0

    # Calculate and return the standard deviation of the amounts
    amounts = [t.amount for t in same_name_transactions]
    return statistics.stdev(amounts)


def get_transaction_amount_variability(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the coefficient of variation of transaction amounts with the same name as the given transaction

    Args:
        transaction (Transaction): The transaction to compare against.
        all_transactions (list[Transaction]): The list of all transactions.

    Returns:
        float: The coefficient of variation of transaction amounts with the same name.
               Returns 0.0 if there are fewer than two such transactions.

    Example:
        >>> transactions = [
            Transaction(id=1, user_id="user1", name="Electricity Bill", amount=40, date="2024-01-01"),
        ...     Transaction(id=2, user_id="user1", name="Electricity Bill", amount=45, date="2024-02-01"),
        ...     Transaction(id=3, user_id="user1", name="Electricity Bill", amount=50, date="2024-03-01"),
        ...     Transaction(id=4, user_id="user2", name="Water Bill", amount=30, date="2024-01-01"),
        ...     Transaction(id=5, user_id="user2", name="Water Bill", amount=35, date="2024-02-01"),
        ... ]
        >>> transaction = Transaction(id=1, user_id="user1", name="Electricity Bill", amount=40, date="2024-01-01")
        >>> get_transaction_amount_variability(transaction, transactions)
        0.11180339887498948
    """
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0
    amounts = [t.amount for t in same_name_transactions]
    mean_amount = np.mean(amounts)
    std_amount = np.std(amounts)
    return float(std_amount / mean_amount if mean_amount != 0 else 0.0)


def get_avg_gap_between_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the average gap (in days) between transactions with the same name as the given transaction

    Args:
        transaction (Transaction): The transaction to compare against.
        all_transactions (list[Transaction]): The list of all transactions.

    Returns:
        float: The average gap (in days) between transactions with the same name.
               Returns 0.0 if there are fewer than two such transactions.

    Example:
        >>> transactions = [
        ...     Transaction(id=1, user_id="user1", name="Electricity Bill", amount=$40, date="2024-01-01"),
        ...     Transaction(id=2, user_id="user1", name="Electricity Bill", amount=$45, date="2024-02-01"),
        ...     Transaction(id=3, user_id="user1", name="Electricity Bill", amount=$50, date="2024-03-01"),
        ...     Transaction(id=4, user_id="user2", name="Water Bill", amount=30, date="2024-01-01"),
        ...     Transaction(id=5, user_id="user2", name="Water Bill", amount=35, date="2024-02-01"),
        ... ]
        >>> transaction = Transaction(id=1, user_id="user1", name="Electricity Bill", amount=40, date="2024-01-01")
        >>> get_avg_gap_between_transactions(transaction, transactions)
        30.5
    """
    # Filter transactions to find those with the same name
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]

    # If there are fewer than two transactions with the same name, return 0.0
    if len(same_name_transactions) < 2:
        return 0.0

    # Sort transactions by date
    same_name_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))

    # Calculate gaps between consecutive transactions
    gaps = [
        (
            datetime.strptime(same_name_transactions[i].date, "%Y-%m-%d")
            - datetime.strptime(same_name_transactions[i - 1].date, "%Y-%m-%d")
        ).days
        for i in range(1, len(same_name_transactions))
    ]

    # Calculate and return the average gap
    return sum(gaps) / len(gaps)


def get_n_transactions_same_month(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions in the same month as transaction"""
    transaction_month = datetime.strptime(transaction.date, "%Y-%m-%d").month
    return len([t for t in all_transactions if datetime.strptime(t.date, "%Y-%m-%d").month == transaction_month])


def get_percent_transactions_same_month(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions in the same month as transaction"""
    if not all_transactions:
        return 0.0
    transaction_month = datetime.strptime(transaction.date, "%Y-%m-%d").month
    n_same_month = len([
        t for t in all_transactions if datetime.strptime(t.date, "%Y-%m-%d").month == transaction_month
    ])
    return n_same_month / len(all_transactions)


def get_avg_amount_same_month(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the average amount of transactions in all_transactions in the same month as transaction"""
    transaction_month = datetime.strptime(transaction.date, "%Y-%m-%d").month
    same_month_transactions = [
        t for t in all_transactions if datetime.strptime(t.date, "%Y-%m-%d").month == transaction_month
    ]
    if not same_month_transactions:
        return 0.0
    return sum(t.amount for t in same_month_transactions) / len(same_month_transactions)


def get_std_amount_same_month(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the standard deviation of amounts for transactions in all_transactions in the same month as transaction"""
    transaction_month = datetime.strptime(transaction.date, "%Y-%m-%d").month
    same_month_transactions = [
        t for t in all_transactions if datetime.strptime(t.date, "%Y-%m-%d").month == transaction_month
    ]
    if len(same_month_transactions) < 2:
        return 0.0
    return statistics.stdev(t.amount for t in same_month_transactions)


def get_n_transactions_same_user_id(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same user_id as transaction"""
    return len([t for t in all_transactions if t.user_id == transaction.user_id])


def get_percent_transactions_same_user_id(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same user_id as transaction"""
    if not all_transactions:
        return 0.0
    n_same_user_id = len([t for t in all_transactions if t.user_id == transaction.user_id])
    return n_same_user_id / len(all_transactions)


def get_n_transactions_same_day_of_week(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions on the same day of the week as transaction"""
    transaction_day_of_week = datetime.strptime(transaction.date, "%Y-%m-%d").weekday()
    return len([
        t for t in all_transactions if datetime.strptime(t.date, "%Y-%m-%d").weekday() == transaction_day_of_week
    ])


def get_percent_transactions_same_day_of_week(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions on the same day of the week as transaction"""
    if not all_transactions:
        return 0.0
    transaction_day_of_week = datetime.strptime(transaction.date, "%Y-%m-%d").weekday()
    n_same_day_of_week = len([
        t for t in all_transactions if datetime.strptime(t.date, "%Y-%m-%d").weekday() == transaction_day_of_week
    ])
    return n_same_day_of_week / len(all_transactions)


def get_avg_amount_same_day_of_week(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the average amount of transactions in all_transactions on the same day of the week as transaction"""
    transaction_day_of_week = datetime.strptime(transaction.date, "%Y-%m-%d").weekday()
    same_day_of_week_transactions = [
        t for t in all_transactions if datetime.strptime(t.date, "%Y-%m-%d").weekday() == transaction_day_of_week
    ]
    if not same_day_of_week_transactions:
        return 0.0
    return sum(t.amount for t in same_day_of_week_transactions) / len(same_day_of_week_transactions)


def get_std_amount_same_day_of_week(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the standard deviation of amounts for transactions in all_transactions
    on the same day of the week as transaction"""
    transaction_day_of_week = datetime.strptime(transaction.date, "%Y-%m-%d").weekday()
    same_day_of_week_transactions = [
        t for t in all_transactions if datetime.strptime(t.date, "%Y-%m-%d").weekday() == transaction_day_of_week
    ]
    if len(same_day_of_week_transactions) < 2:
        return 0.0
    return statistics.stdev(t.amount for t in same_day_of_week_transactions)


def get_n_transactions_within_amount_range(
    transaction: Transaction, all_transactions: list[Transaction], percentage: float = 0.1
) -> int:
    """Get the number of transactions in all_transactions within a certain amount range of transaction"""
    lower_bound = transaction.amount * (1 - percentage)
    upper_bound = transaction.amount * (1 + percentage)
    return len([t for t in all_transactions if lower_bound <= t.amount <= upper_bound])


def get_percent_transactions_within_amount_range(
    transaction: Transaction, all_transactions: list[Transaction], percentage: float = 0.1
) -> float:
    """Get the percentage of transactions in all_transactions within a certain amount range of transaction"""
    if not all_transactions:
        return 0.0
    lower_bound = transaction.amount * (1 - percentage)
    upper_bound = transaction.amount * (1 + percentage)
    n_within_range = len([t for t in all_transactions if lower_bound <= t.amount <= upper_bound])
    return n_within_range / len(all_transactions)


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "n_transactions_same_name": get_n_transactions_same_name(transaction, all_transactions),
        "percent_transactions_same_name": get_percent_transactions_same_name(transaction, all_transactions),
        "avg_amount_same_name": get_avg_amount_same_name(transaction, all_transactions),
        "std_amount_same_name": get_std_amount_same_name(transaction, all_transactions),
        "n_transactions_same_month": get_n_transactions_same_month(transaction, all_transactions),
        "percent_transactions_same_month": get_percent_transactions_same_month(transaction, all_transactions),
        "avg_amount_same_month": get_avg_amount_same_month(transaction, all_transactions),
        "std_amount_same_month": get_std_amount_same_month(transaction, all_transactions),
        "n_transactions_same_user_id": get_n_transactions_same_user_id(transaction, all_transactions),
        "percent_transactions_same_user_id": get_percent_transactions_same_user_id(transaction, all_transactions),
        "n_transactions_same_day_of_week": get_n_transactions_same_day_of_week(transaction, all_transactions),
        "percent_transactions_same_day_of_week": get_percent_transactions_same_day_of_week(
            transaction, all_transactions
        ),
        "avg_amount_same_day_of_week": get_avg_amount_same_day_of_week(transaction, all_transactions),
        "std_amount_same_day_of_week": get_std_amount_same_day_of_week(transaction, all_transactions),
        "n_transactions_within_amount_range": get_n_transactions_within_amount_range(transaction, all_transactions),
        "percent_transactions_within_amount_range": get_percent_transactions_within_amount_range(
            transaction, all_transactions
        ),
        "avg_gap_between_transactions": get_avg_gap_between_transactions(transaction, all_transactions),  # New feature
    }
