from datetime import datetime

import numpy as np

from recur_scan.transactions import Transaction


def get_time_interval_between_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the average time interval (in days) between transactions with the same amount"""
    same_amount_transactions = sorted(
        [t for t in all_transactions if t.amount == transaction.amount],  # Filter transactions with the same amount
        key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"),  # Sort by date
    )
    if len(same_amount_transactions) < 2:
        return 365.0  # Return a large number if there are less than 2 transactions
    intervals = [
        (
            datetime.strptime(same_amount_transactions[i + 1].date, "%Y-%m-%d")
            - datetime.strptime(same_amount_transactions[i].date, "%Y-%m-%d")
        ).days
        for i in range(len(same_amount_transactions) - 1)  # Calculate intervals between consecutive transactions
    ]
    return sum(intervals) / len(intervals)  # Return the average interval


def get_mobile_transaction(transaction: Transaction) -> bool:
    """Check if the transaction is from a mobile company (T-Mobile, AT&T, Verizon)"""
    mobile_companies = {
        "T-Mobile",
        "AT&T",
        "Verizon",
        "Boost Mobile",
        "Tello Mobile",
    }  # Define a set of mobile companies
    return transaction.name in mobile_companies  # Check if the transaction name is in the set


def get_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the frequency of transactions for the same vendor"""
    vendor_transactions = [
        t for t in all_transactions if t.name == transaction.name
    ]  # Filter transactions by vendor name
    if len(vendor_transactions) < 2:
        return 0.0  # Return 0 if there are less than 2 transactions
    intervals = [
        (
            datetime.strptime(vendor_transactions[i + 1].date, "%Y-%m-%d")
            - datetime.strptime(vendor_transactions[i].date, "%Y-%m-%d")
        ).days
        for i in range(len(vendor_transactions) - 1)  # Calculate intervals between consecutive transactions
    ]
    if not intervals or sum(intervals) == 0:
        return 0.0  # Return 0 if there are no intervals or the sum is 0
    return 1 / (sum(intervals) / len(intervals))  # Return the frequency


def get_dispersion_transaction_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the dispersion in transaction amounts for the same vendor"""
    vendor_transactions = [
        t.amount for t in all_transactions if t.name == transaction.name
    ]  # Get amounts for the same vendor
    if len(vendor_transactions) < 2:
        return 0.0  # Return 0 if there are less than 2 transactions
    return float(np.var(vendor_transactions))  # Return the dispersion


def get_mad_transaction_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the median absolute deviation (MAD) of transaction amounts for the same vendor"""
    vendor_transactions = [
        t.amount for t in all_transactions if t.name == transaction.name
    ]  # Get amounts for the same vendor
    if len(vendor_transactions) < 2:
        return 0.0  # Return 0 if there are less than 2 transactions
    median = np.median(vendor_transactions)  # Calculate the median
    mad = np.median([abs(amount - median) for amount in vendor_transactions])  # Calculate MAD
    return float(mad)  # Return the MAD


def get_coefficient_of_variation(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the coefficient of variation (CV) of transaction amounts for the same vendor"""
    vendor_transactions = [
        t.amount for t in all_transactions if t.name == transaction.name
    ]  # Get amounts for the same vendor
    if len(vendor_transactions) < 2:
        return 0.0  # Return 0 if there are less than 2 transactions
    mean = np.mean(vendor_transactions)  # Calculate the mean
    if mean == 0:
        return 0.0  # Avoid division by zero
    std_dev = np.std(vendor_transactions)  # Calculate the standard deviation
    return float(std_dev / mean)  # Return the coefficient of variation


def get_transaction_interval_consistency(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Calculate the average interval between transactions for the same vendor."""
    # Filter transactions for the same vendor
    vendor_transactions = [t for t in transactions if t.name == transaction.name]
    if len(vendor_transactions) < 2:
        return 0.0  # No intervals to calculate

    # Sort transactions by date (convert date strings to datetime objects)
    vendor_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))

    # Calculate intervals in days
    intervals = [
        (
            datetime.strptime(vendor_transactions[i + 1].date, "%Y-%m-%d")
            - datetime.strptime(vendor_transactions[i].date, "%Y-%m-%d")
        ).days
        for i in range(len(vendor_transactions) - 1)
    ]
    # Return the average interval
    return sum(intervals) / len(intervals)


def get_average_transaction_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate the average transaction amount for the same vendor.

    Args:
        transaction (Transaction): The transaction to analyze.
        all_transactions (list[Transaction]): List of all transactions.

    Returns:
        float: The average transaction amount for the vendor.
    """
    vendor_transactions = [
        t.amount for t in all_transactions if t.name == transaction.name
    ]  # Filter transactions by vendor name
    if not vendor_transactions:
        return 0.0  # Return 0 if there are no transactions for the vendor
    return float(np.mean(vendor_transactions))  # Return the average amount
