from recur_scan.transactions import Transaction
import statistics


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
    """Get the standard deviation of amounts for transactions in all_transactions with the same name as transaction"""
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0
    return statistics.stdev(t.amount for t in same_name_transactions)


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "n_transactions_same_name": get_n_transactions_same_name(transaction, all_transactions),
        "percent_transactions_same_name": get_percent_transactions_same_name(transaction, all_transactions),
        "avg_amount_same_name": get_avg_amount_same_name(transaction, all_transactions),
        "std_amount_same_name": get_std_amount_same_name(transaction, all_transactions),
    }