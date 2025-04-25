import statistics
from datetime import datetime

from recur_scan.transactions import Transaction


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
