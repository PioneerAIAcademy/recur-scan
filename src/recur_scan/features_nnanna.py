import re
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


# New features

# def get_recency_of_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """
#     Calculate the recency of the transaction for the same vendor.
#     """
#     # Filter transactions for the same vendor
#     vendor_transactions = [
#         t for t in all_transactions if t.name == transaction.name
#     ]
#     if not vendor_transactions:
#         return 36500.0  # Return a large value if there are no previous transactions

#     # Sort transactions by date
#     vendor_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))

#     # Find the most recent transaction before the current one
#     transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
#     previous_transactions = [
#         t for t in vendor_transactions if datetime.strptime(t.date, "%Y-%m-%d") < transaction_date
#     ]
#     if not previous_transactions:
#         return 36500.0  # Return a large value if there are no previous transactions

#     last_transaction_date = datetime.strptime(previous_transactions[-1].date, "%Y-%m-%d")
#     return (transaction_date - last_transaction_date).days  # Days since the last transaction


# def get_transaction_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """
#     Calculate the transaction consistency score for the same vendor.
#     The score is based on the standard deviation of transaction amounts relative to the mean.
#     """
#     # Filter transactions for the same vendor
#     vendor_transactions = [
#         t.amount for t in all_transactions if t.name == transaction.name
#     ]
#     if len(vendor_transactions) < 2:
#         return 0.0  # Return 0 if there are less than 2 transactions

#     mean = np.mean(vendor_transactions)
#     std_dev = np.std(vendor_transactions)

#     if mean == 0:
#         return 0.0  # Avoid division by zero

#     consistency_score = std_dev / mean  # Lower score indicates higher consistency
#     return float(consistency_score)


# def get_transaction_interval_variance(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """
#     Calculate the variance of intervals (in days) between transactions for the same vendor,
#     using regex to match vendor names for better grouping.
#     """
#     # Compile a regex pattern to match similar vendor names (e.g., "Apple Inc." and "Apple")
#     vendor_pattern = re.compile(re.escape(transaction.name), re.IGNORECASE)

#     # Filter transactions matching the vendor name pattern
#     vendor_transactions = [
#         t for t in all_transactions if vendor_pattern.search(t.name)
#     ]
#     if len(vendor_transactions) < 2:
#         return 36500.0  # Return a large value if there are less than 2 transactions

#     # Sort transactions by date
#     vendor_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))

#     # Calculate intervals in days
#     intervals = [
#         (
#             datetime.strptime(vendor_transactions[i + 1].date, "%Y-%m-%d")
#             - datetime.strptime(vendor_transactions[i].date, "%Y-%m-%d")
#         ).days
#         for i in range(len(vendor_transactions) - 1)
#     ]

#     # Return the variance of intervals, normalized to reduce the impact of outliers
#     return float(np.var(intervals) / (1 + np.mean(intervals))) if intervals else 36500.0


# def get_is_recurring_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
#     """
#     Check if a transaction is recurring by verifying if it occurs on the same date (or within 3 days)
#     every month and has the same amount.
#     """
#     # Filter transactions with the same amount
#     same_amount_transactions = [
#         t for t in all_transactions if t.amount == transaction.amount
#     ]

#     if len(same_amount_transactions) < 2:
#         return False  # Not enough transactions to determine recurrence

#     # Sort transactions by date
#     same_amount_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))

#     # Check if the transaction occurs on the same date or within 3 days every month
#     transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
#     for i in range(len(same_amount_transactions) - 1):
#         current_date = datetime.strptime(same_amount_transactions[i].date, "%Y-%m-%d")
#         next_date = datetime.strptime(same_amount_transactions[i + 1].date, "%Y-%m-%d")

#         # Calculate the difference in days and months
#         day_difference = abs((next_date - current_date).days)
#         month_difference = (next_date.year - current_date.year) * 12 + (next_date.month - current_date.month)

#         # Check if the transaction recurs monthly within 3 days
#         if month_difference == 1 and day_difference <= 3:
#             continue
#         else:
#             return False

#     return True


# def get_is_not_recurring_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
#     """
#     Determine if a transaction is not recurring based on date patterns and vendor type.
#     """
#     # Define mobile companies
#     mobile_companies = {"T-Mobile", "AT&T", "Verizon", "Boost Mobile", "Tello Mobile"}

#     # Check if the transaction is from a mobile company
#     if transaction.name in mobile_companies:
#         return False  # Mobile company transactions are considered recurring

#     # Filter transactions with the same amount and vendor name
#     same_vendor_transactions = [
#         t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount
#     ]

#     if len(same_vendor_transactions) < 2:
#         return True  # Not enough transactions to determine recurrence

#     # Sort transactions by date
#     same_vendor_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))

#     # Check if the transaction occurs on the same date or within 3 days every month
#     for i in range(len(same_vendor_transactions) - 1):
#         current_date = datetime.strptime(same_vendor_transactions[i].date, "%Y-%m-%d")
#         next_date = datetime.strptime(same_vendor_transactions[i + 1].date, "%Y-%m-%d")

#         # Calculate the difference in days and months
#         day_difference = abs((next_date - current_date).days)
#         month_difference = (next_date.year - current_date.year) * 12 + (next_date.month - current_date.month)

#         # If the transaction does not recur monthly within 3 days, it is not recurring
#         if not (month_difference == 1 and day_difference <= 3):
#             return True

#     return True


# def get_recurring_transaction_by_amount_and_interval(
#     transaction: Transaction,
#     all_transactions: list[Transaction]
# ) -> bool:
#     """
#     Determine if a transaction is recurring based on the same amount and consistent intervals of 13 to 15 days.
#     """
#     # Filter transactions with the same amount
#     same_amount_transactions = [
#         t for t in all_transactions if t.amount == transaction.amount
#     ]

#     if len(same_amount_transactions) < 2:
#         return False  # Not enough transactions to determine recurrence

#     # Sort transactions by date
#     same_amount_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))

#     # Check if the intervals between transactions are consistently 13 to 15 days
#     for i in range(len(same_amount_transactions) - 1):
#         current_date = datetime.strptime(same_amount_transactions[i].date, "%Y-%m-%d")
#         next_date = datetime.strptime(same_amount_transactions[i + 1].date, "%Y-%m-%d")

#         # Calculate the difference in days
#         day_difference = (next_date - current_date).days

#         if not (13 <= day_difference <= 15):
#             return False  # If any interval is outside the range, it's not recurring

#     return True


# def get_recurring_transaction_by_short_interval(
#     transaction: Transaction,
#     all_transactions: list[Transaction]
# ) -> bool:
#     """
#     Determine if a transaction is recurring based on the same amount and consistent intervals of 6 to 8 days.
#     """
#     # Filter transactions with the same amount
#     same_amount_transactions = [
#         t for t in all_transactions if t.amount == transaction.amount
#     ]

#     if len(same_amount_transactions) < 2:
#         return False  # Not enough transactions to determine recurrence

#     # Sort transactions by date
#     same_amount_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))

#     # Check if the intervals between transactions are consistently 6 to 8 days
#     for i in range(len(same_amount_transactions) - 1):
#         current_date = datetime.strptime(same_amount_transactions[i].date, "%Y-%m-%d")
#         next_date = datetime.strptime(same_amount_transactions[i + 1].date, "%Y-%m-%d")

#         # Calculate the difference in days
#         day_difference = (next_date - current_date).days

#         if not (6 <= day_difference <= 8):
#             return False  # If any interval is outside the range, it's not recurring

#     return False


def get_u_dot_express_lane(transactions: list[Transaction]) -> list[Transaction]:
    """
    Filter out transactions with the name 'U-dot-express Lane' unless the amount is 2.50.

    Args:
        transactions (list[Transaction]): List of all transactions.

    Returns:
        list[Transaction]: Filtered list of transactions.
    """
    filtered_transactions = [
        t for t in transactions if not (re.match(r"(?i)^U-dot-express Lane$", t.name) and t.amount != 2.50)
    ]
    return filtered_transactions


# def get_weighted_recency(transactions, current_transaction):
#     """
#     Calculate a weighted recency score for a transaction based on its recency and importance.
#     """
#     recency_scores = []
#     current_transaction_date = datetime.strptime(current_transaction.date, "%Y-%m-%d")  # Convert to datetime
#     for transaction in transactions:
#         if transaction.name == current_transaction.name and transaction != current_transaction:
#             transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")  # Convert to datetime
#             days_diff = (current_transaction_date - transaction_date).days
#             if days_diff <= 0:  # Safeguard to avoid division by zero or negative values
#                 continue
#             recency_scores.append(1 / (1 + days_diff))  # Higher weight for recent transactions
#     return sum(recency_scores)


# def get_transaction_clusters(transactions, vendor_name):
#     """
#     Cluster transactions for a specific vendor based on time intervals.
#     """
#     vendor_transactions = [t for t in transactions if t.name == vendor_name]
#     intervals = [
#         (datetime.strptime(vendor_transactions[i + 1].date, "%Y-%m-%d") -
#          datetime.strptime(vendor_transactions[i].date, "%Y-%m-%d")).days
#         for i in range(len(vendor_transactions) - 1)
#     ]
#     return intervals


# def get_normalized_transaction_amount(transactions, current_transaction):
#     """
#     Normalize the transaction amount for a given transaction.
#     """
#     amounts = [t.amount for t in transactions if t.name == current_transaction.name]
#     mean_amount = sum(amounts) / len(amounts)
#     std_dev = (sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5
#     return (current_transaction.amount - mean_amount) / std_dev if std_dev != 0 else 0


# def get_frequency_consistency(transactions, vendor_name):
#     """
#     Calculate the consistency of transaction frequency for a vendor.
#     """
#     vendor_transactions = [t for t in transactions if t.name == vendor_name]
#     intervals = [
#         (datetime.strptime(vendor_transactions[i + 1].date, "%Y-%m-%d") -
#          datetime.strptime(vendor_transactions[i].date, "%Y-%m-%d")).days
#         for i in range(len(vendor_transactions) - 1)
#     ]
#     if len(intervals) < 2:
#         return 0.0
#     mean_interval = sum(intervals) / len(intervals)
#     variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
#     return 1 / (1 + variance)  # Higher score for lower variance


# def get_vendor_recurrence_score(transactions, vendor_name):
#     """
#     Calculate a recurrence score for a vendor based on transaction patterns.
#     """
#     vendor_transactions = [t for t in transactions if t.name == vendor_name]
#     if len(vendor_transactions) < 2:
#         return 0.0
#     intervals = [
#         (datetime.strptime(vendor_transactions[i + 1].date, "%Y-%m-%d") -
#          datetime.strptime(vendor_transactions[i].date, "%Y-%m-%d")).days
#         for i in range(len(vendor_transactions) - 1)
#     ]
#     return sum(1 / (1 + abs(interval - intervals[0])) for interval in intervals) / len(intervals)

# def is_outlier(transaction, transactions):
#     """
#     Determine if a transaction is an outlier based on its amount.
#     """
#     amounts = [t.amount for t in transactions]
#     mean_amount = sum(amounts) / len(amounts)
#     std_dev = (sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5
#     return abs(transaction.amount - mean_amount) > 2 * std_dev


# def get_temporal_pattern_score(transaction):
#     """
#     Calculate a score based on the temporal pattern of a transaction (e.g., day of the week).
#     """
#     transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")  # Convert to datetime
#     day_of_week = transaction_date.weekday()  # 0 = Monday, 6 = Sunday
#     return 1 if day_of_week in [0, 6] else 0.5  # Higher score for weekends


def is_monthly_apple_storage(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the transaction is for Apple, the amount ends in .99, and it occurs monthly
    with slight variations in timing.
    """
    if transaction.name != "Apple":
        return False

    # Find the most common .99 amount for Apple
    from collections import Counter

    amounts = [t.amount for t in all_transactions if t.name == "Apple" and str(t.amount).endswith(".99")]
    if not amounts:
        return False
    most_common_amount, _ = Counter(amounts).most_common(1)[0]
    if transaction.amount != most_common_amount:
        return False

    # Filter transactions for the same vendor and amount
    vendor_transactions = [t for t in all_transactions if t.name == "Apple" and t.amount == most_common_amount]
    if len(vendor_transactions) < 2:
        return False

    vendor_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))
    for i in range(len(vendor_transactions) - 1):
        current_date = datetime.strptime(vendor_transactions[i].date, "%Y-%m-%d")
        next_date = datetime.strptime(vendor_transactions[i + 1].date, "%Y-%m-%d")
        if not (28 <= (next_date - current_date).days <= 31):
            return False

    return True


def get_cobblestone_recurrence_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate a recurrence score for Cobblestone Wash transactions.
    The score is the fraction of intervals between primary-amount transactions that are close to monthly.
    """
    if transaction.name != "Cobblestone Wash":
        return 0.0

    # Find the most common amount (primary recurring amount)
    from collections import Counter

    amounts = [t.amount for t in all_transactions if t.name == "Cobblestone Wash"]
    if not amounts:
        return 0.0
    primary_amount, _ = Counter(amounts).most_common(1)[0]

    # Filter for primary amount transactions
    recurring_transactions = [
        t for t in all_transactions if t.name == "Cobblestone Wash" and t.amount == primary_amount
    ]
    if len(recurring_transactions) < 2:
        return 0.0

    # Sort by date
    recurring_transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))
    intervals = [
        (
            datetime.strptime(recurring_transactions[i + 1].date, "%Y-%m-%d")
            - datetime.strptime(recurring_transactions[i].date, "%Y-%m-%d")
        ).days
        for i in range(len(recurring_transactions) - 1)
    ]

    # Count intervals that are close to monthly (28-31 days)
    good_intervals = sum(27 <= days <= 35 for days in intervals)
    score = good_intervals / len(intervals) if intervals else 0.0

    # Only return a high score if this transaction is for the primary amount
    return score if transaction.amount == primary_amount else 0.5 * score


def is_consistent_transaction_amount(
    transaction: Transaction, all_transactions: list[Transaction], threshold: float = 0.2
) -> bool:
    """
    Check if the transaction amounts for the same vendor are consistent.
    """
    # Filter transactions for the same vendor
    vendor_transactions = [t.amount for t in all_transactions if t.name == transaction.name]
    if len(vendor_transactions) < 2:
        return True  # Not enough data to determine inconsistency

    # Calculate the coefficient of variation (CV)
    mean = np.mean(vendor_transactions)
    std_dev = np.std(vendor_transactions)
    if mean == 0:
        return False  # Avoid division by zero

    cv = std_dev / mean  # Coefficient of variation
    return bool(cv <= threshold)  # Return True if CV is within the threshold


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    """
    Generate new features for the transaction.

    Args:
        transaction (Transaction): The transaction to analyze.
        all_transactions (list[Transaction]): List of all transactions.

    Returns:
        dict: A dictionary containing the new features.
    """
    return {
        # "recency_nnanna": get_recency_of_transaction(transaction, all_transactions),
        # "transaction_consistency_nnanna": get_transaction_consistency(transaction, all_transactions),
        # "transaction_interval_variance_nnanna": get_transaction_interval_variance(transaction, all_transactions),
        # "recurring_transaction_nnanna": float(get_is_recurring_transaction(transaction, all_transactions)),
        # "not_recurring_transaction_nnanna": float(get_is_not_recurring_transaction(transaction, all_transactions)),
        # "recurring_by_amount_interval_nnanna":
        #   get_recurring_transaction_by_amount_and_interval(transaction, all_transactions),
        # "recurring_by_short_interval_nnanna":
        #     get_recurring_transaction_by_short_interval(transaction, all_transactions),
        "u_dot_express_lane_nnanna": float(
            bool(re.match(r"(?i)^U-dot-express Lane$", transaction.name)) and transaction.amount != 2.50
        ),
        #    "recency_nnanna": get_weighted_recency(all_transactions, transaction),
        # "cluster_nnanna": float(
        #     np.mean(get_transaction_clusters(all_transactions, transaction.name))
        # ) if get_transaction_clusters(all_transactions, transaction.name) else 0.0,
        #    "normalized_amount_nnanna": get_normalized_transaction_amount(all_transactions, transaction),
        #    "frequency_consistency_nnanna": get_frequency_consistency(all_transactions, transaction.name),
        #    "recurrence_score_nnanna": get_vendor_recurrence_score(all_transactions, transaction.name),
        #    "outlier_nnanna": float(is_outlier(transaction, all_transactions)),
        #    "temporal_pattern_score_nnanna": get_temporal_pattern_score(transaction),
        "monthly_apple_storage_nnanna": float(is_monthly_apple_storage(transaction, all_transactions)),
        "cobblestone_recurrence_score_nnanna": get_cobblestone_recurrence_score(transaction, all_transactions),
        "consistent_transaction_amount_nnanna": float(is_consistent_transaction_amount(transaction, all_transactions)),
    }
