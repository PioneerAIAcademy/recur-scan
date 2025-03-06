from recur_scan.transactions import Transaction
import datetime

def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions)


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        **get_day_of_week_features(transaction),
    }

def get_day_of_week_features(transaction: Transaction) -> dict[str, int]:
    """Extract day of the week and day of the month for transaction."""
    date_obj = datetime.datetime.strptime(transaction.date, "%Y-%m-%d")
    return {
        "day_of_month": date_obj.day,
        "weekday": date_obj.weekday()  # Monday = 0, Sunday = 6
    }