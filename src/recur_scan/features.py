from recur_scan.transactions import Transaction
from datetime import datetime
import re
import numpy as np


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


def get_mobile_transaction(transaction: Transaction) -> bool:
    """Check if the transaction is from a mobile company (T-Mobile, AT&T, Verizon)"""
    mobile_companies = {"T-Mobile", "AT&T", "Verizon", "Boost Mobile", "Tello Mobile"}
    return transaction.name in mobile_companies

def get_is_phone(transaction: Transaction) -> bool:
    """Check if the transaction is a phone payment."""
    # use a regular expression with boundaries to match case-insensitive phone
    # and phone-related terms
    match = re.search(r"\b(at&t|t-mobile|verizon)\b", transaction.name, re.IGNORECASE)
    return bool(match)

def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in 99"""
    return (transaction.amount * 100) % 100 == 99

def get_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the frequency of transactions for the same vendor"""
    vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(vendor_transactions) < 2:
        return 0.0
    intervals = [
        (datetime.strptime(vendor_transactions[i + 1].date, "%Y-%m-%d") - datetime.strptime(vendor_transactions[i].date, "%Y-%m-%d")).days
        for i in range(len(vendor_transactions) - 1)
    ]
    if not intervals or sum(intervals) == 0:
        return 0.0
    return 1 / (sum(intervals) / len(intervals))

def get_transaction_amount_variance(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the variance in transaction amounts for the same vendor"""
    vendor_transactions = [t.amount for t in all_transactions if t.name == transaction.name]
    if len(vendor_transactions) < 2:
        return 0.0
    return float(np.var(vendor_transactions))


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int | bool | list[str]]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "time_interval_between_transactions": get_time_interval_between_transactions(transaction, all_transactions),
        "mobile_company": get_mobile_transaction(transaction),
        "is_phone": get_is_phone(transaction),
        "ends_in_99": get_ends_in_99(transaction),
        "transaction_frequency": get_transaction_frequency(transaction, all_transactions),
        "amount": transaction.amount,
        "transaction_amount_variance": get_transaction_amount_variance(transaction, all_transactions),
        
    }
