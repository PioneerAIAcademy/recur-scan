import re
from datetime import date, datetime
from functools import lru_cache
from recur_scan.transactions import Transaction
import numpy as np  # Import numpy for numerical operations

def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring because of the vendor name - check lowercase match"""
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
    }
    return transaction.name.lower() in always_recurring_vendors


def get_is_insurance(transaction: Transaction) -> bool:
    """Check if the transaction is an insurance payment."""
    # use a regular expression with boundaries to match case-insensitive insurance
    # and insurance-related terms
    match = re.search(r"\b(insurance|insur|insuranc)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_utility(transaction: Transaction) -> bool:
    """Check if the transaction is a utility payment."""
    # use a regular expression with boundaries to match case-insensitive utility
    # and utility-related terms
    match = re.search(r"\b(utility|utilit|energy)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_phone(transaction: Transaction) -> bool:
    """Check if the transaction is a phone payment."""
    # use a regular expression with boundaries to match case-insensitive phone
    # and phone-related terms
    match = re.search(r"\b(at&t|t-mobile|verizon)\b", transaction.name, re.IGNORECASE)
    return bool(match)


@lru_cache(maxsize=1024)
def _parse_date(date_str: str) -> date:
    """Parse a date string into a datetime.date object."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def get_n_transactions_days_apart(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> int:
    """
    Get the number of transactions in all_transactions that are within n_days_off of
    being n_days_apart from transaction
    """
    n_txs = 0
    transaction_date = _parse_date(transaction.date)

    # Pre-calculate bounds for faster checking
    lower_remainder = n_days_apart - n_days_off
    upper_remainder = n_days_off

    for t in all_transactions:
        t_date = _parse_date(t.date)
        days_diff = abs((t_date - transaction_date).days)

        # Skip if the difference is less than minimum required
        if days_diff < n_days_apart - n_days_off:
            continue

        # Check if the difference is close to any multiple of n_days_apart
        remainder = days_diff % n_days_apart

        if remainder <= upper_remainder or remainder >= lower_remainder:
            n_txs += 1

    return n_txs


def _get_day(date: str) -> int:
    """Get the day of the month from a transaction date."""
    return int(date.split("-")[2])


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    """Get the number of transactions in all_transactions that are on the same day of the month as transaction"""
    return len([t for t in all_transactions if abs(_get_day(t.date) - _get_day(transaction.date)) <= n_days_off])


def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in 99"""
    return (transaction.amount * 100) % 100 == 99


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
        "transaction_frequency": get_transaction_frequency(transaction, all_transactions),  # Frequency of transactions for the same vendor        
        "transaction_amount": get_dispersion_transaction_amount(transaction, all_transactions),      
        "ends_in_99": get_ends_in_99(transaction),
        "amount": transaction.amount,
        "same_day_exact": get_n_transactions_same_day(transaction, all_transactions, 0),
        "same_day_off_by_1": get_n_transactions_same_day(transaction, all_transactions, 1),
        "same_day_off_by_2": get_n_transactions_same_day(transaction, all_transactions, 2),
        "14_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 14, 0),
        "14_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 14, 1),
        "7_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 7, 0),
        "7_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 7, 1),
        "is_insurance": get_is_insurance(transaction),
        "is_utility": get_is_utility(transaction),
        "is_phone": get_is_phone(transaction),
        "is_always_recurring": get_is_always_recurring(transaction),
    }
