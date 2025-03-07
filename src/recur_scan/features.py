from recur_scan.transactions import Transaction
from datetime import datetime


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions)


def get_time_interval_between_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the average time interval (in days) between transactions with the same amount"""
    same_amount_transactions = sorted(
        [t for t in all_transactions if t.amount == transaction.amount],
        key=lambda t: datetime.strptime(t.date, "%Y-%m-%d")
    )
    if len(same_amount_transactions) < 2:
        return 365.0  # Return a large number if there are less than 2 transactions
    intervals = [
        (datetime.strptime(same_amount_transactions[i + 1].date, "%Y-%m-%d") - datetime.strptime(same_amount_transactions[i].date, "%Y-%m-%d")).days
        for i in range(len(same_amount_transactions) - 1)
    ]
    return sum(intervals) / len(intervals)


def get_mobile_company(transaction: Transaction) -> bool:
    """Check if the transaction is from a mobile company (T-Mobile, AT&T, Verizon)"""
    mobile_companies = {"T-Mobile", "AT&T", "Verizon"}
    return transaction.name in mobile_companies


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "time_interval_between_transactions": get_time_interval_between_transactions(transaction, all_transactions),
        "mobile_company": get_mobile_company(transaction),
    }
