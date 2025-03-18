from recur_scan.transactions import Transaction
from datetime import datetime
import re
import numpy as np  # Import numpy for numerical operations

def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])  # Count transactions with the same amount

def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0  # Return 0 if there are no transactions
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])  # Count transactions with the same amount
    return n_same_amount / len(all_transactions)  # Calculate the percentage

def get_time_interval_between_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the average time interval (in days) between transactions with the same amount"""
    same_amount_transactions = sorted(
        [t for t in all_transactions if t.amount == transaction.amount],  # Filter transactions with the same amount
        key=lambda t: datetime.strptime(t.date, "%Y-%m-%d")  # Sort by date
    )
    if len(same_amount_transactions) < 2:
        return 365.0  # Return a large number if there are less than 2 transactions
    intervals = [
        (datetime.strptime(same_amount_transactions[i + 1].date, "%Y-%m-%d") - datetime.strptime(same_amount_transactions[i].date, "%Y-%m-%d")).days
        for i in range(len(same_amount_transactions) - 1)  # Calculate intervals between consecutive transactions
    ]
    return sum(intervals) / len(intervals)  # Return the average interval

def get_mobile_transaction(transaction: Transaction) -> bool:
    """Check if the transaction is from a mobile company (T-Mobile, AT&T, Verizon)"""
    mobile_companies = {"T-Mobile", "AT&T", "Verizon", "Boost Mobile", "Tello Mobile"}  # Define a set of mobile companies
    return transaction.name in mobile_companies  # Check if the transaction name is in the set

def get_is_phone(transaction: Transaction) -> bool:
    """Check if the transaction is a phone payment."""
    match = re.search(r"\b(at&t|t-mobile|verizon)\b", transaction.name, re.IGNORECASE)  # Use regex to match phone-related terms
    return bool(match)  # Return True if a match is found

def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in 99"""
    return (transaction.amount * 100) % 100 == 99  # Check if the amount ends in 99

def get_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the frequency of transactions for the same vendor"""
    vendor_transactions = [t for t in all_transactions if t.name == transaction.name]  # Filter transactions by vendor name
    if len(vendor_transactions) < 2:
        return 0.0  # Return 0 if there are less than 2 transactions
    intervals = [
        (datetime.strptime(vendor_transactions[i + 1].date, "%Y-%m-%d") - datetime.strptime(vendor_transactions[i].date, "%Y-%m-%d")).days
        for i in range(len(vendor_transactions) - 1)  # Calculate intervals between consecutive transactions
    ]
    if not intervals or sum(intervals) == 0:
        return 0.0  # Return 0 if there are no intervals or the sum is 0
    return 1 / (sum(intervals) / len(intervals))  # Return the frequency

def get_dispersion_transaction_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the dispersion in transaction amounts for the same vendor"""
    vendor_transactions = [t.amount for t in all_transactions if t.name == transaction.name]  # Get amounts for the same vendor
    if len(vendor_transactions) < 2:
        return 0.0  # Return 0 if there are less than 2 transactions
    return float(np.var(vendor_transactions))  # Return the dispersion

def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int | bool | list[str]]:
    """Get a dictionary of features for a transaction"""
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),  # Number of transactions with the same amount
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),  # Percentage of transactions with the same amount
        "time_interval_between_transactions": get_time_interval_between_transactions(transaction, all_transactions),  # Average time interval between transactions with the same amount
        "mobile_company": get_mobile_transaction(transaction),  # Check if the transaction is from a mobile company
        "is_phone": get_is_phone(transaction),  # Check if the transaction is a phone payment
        "ends_in_99": get_ends_in_99(transaction),  # Check if the amount ends in 99
        "transaction_frequency": get_transaction_frequency(transaction, all_transactions),  # Frequency of transactions for the same vendor
        "amount": transaction.amount,  # Transaction amount
        "transaction_amount": get_dispersion_transaction_amount(transaction, all_transactions),  # Dispersion in transaction amounts for the same vendor
        
    }
