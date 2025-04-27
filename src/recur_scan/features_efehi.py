from datetime import datetime

import numpy as np

from recur_scan.transactions import Transaction


def _get_days(date: str) -> int:
    """Get the number of days since the epoch of a transaction date."""
    return (datetime.strptime(date, "%Y-%m-%d") - datetime(1970, 1, 1)).days


def get_transaction_time_of_month(transaction: Transaction) -> int:
    """Categorize the transaction as early, mid, or late in the month."""
    day = int(transaction.date.split("-")[2])
    if day <= 10:
        return 0
    elif day <= 20:
        return 1
    else:
        return 2


def get_transaction_amount_stability(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the standard deviation of transaction amounts for the same name."""
    same_name_transactions = [t.amount for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0
    return float(np.std(same_name_transactions))


def get_time_between_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the average time gap (in days) between transactions with the same name."""
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0
    dates = sorted(_get_days(t.date) for t in same_name_transactions)
    intervals = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
    return sum(intervals) / len(intervals) if intervals else 0.0


def get_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the average frequency (in days) of transactions with the same name."""
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0
    dates = sorted(_get_days(t.date) for t in same_name_transactions)
    intervals = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
    return sum(intervals) / len(intervals)


def get_n_same_name_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Count transactions with the same name."""
    return len([t for t in all_transactions if t.name == transaction.name])


def get_irregular_periodicity(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the standard deviation of time gaps between transactions with the same name."""
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0
    dates = sorted(_get_days(t.date) for t in same_name_transactions)
    intervals = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
    return float(np.std(intervals)) if intervals else 0.0


def get_irregular_periodicity_with_tolerance(
    transaction: Transaction, all_transactions: list[Transaction], tolerance: int = 5
) -> float:
    """Normalized std dev of intervals with tolerance allowance."""
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0
    dates = sorted(_get_days(t.date) for t in same_name_transactions)
    intervals = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
    if not intervals:
        return 0.0
    interval_groups: list[list[int]] = []
    for interval in intervals:
        added = False
        for group in interval_groups:
            if abs(interval - group[0]) <= tolerance:
                group.append(interval)
                added = True
                break
        if not added:
            interval_groups.append([interval])
    largest_group = max(interval_groups, key=len)
    largest_group_std = float(np.std(largest_group)) if len(largest_group) > 1 else 0.0
    median_interval = float(np.median(intervals))
    normalized_std = largest_group_std / median_interval if median_interval > 0 else 0.0
    return normalized_std


def get_user_transaction_frequency(user_id: str, all_transactions: list[Transaction]) -> float:
    """Average frequency of all transactions for a user."""
    user_transactions = [t for t in all_transactions if t.user_id == user_id]
    if len(user_transactions) < 2:
        return 0.0
    dates = sorted(_get_days(t.date) for t in user_transactions)
    intervals = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
    return sum(intervals) / len(intervals) if intervals else 0.0


def get_vendor_recurring_ratio(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Ratio of recurring transactions to total transactions for the same vendor."""
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if not same_name_transactions:
        return 0.0
    recurring_count = len([t for t in same_name_transactions if t.amount == transaction.amount])
    return recurring_count / len(same_name_transactions)


def get_vendor_recurrence_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Consistency of vendor transaction intervals with tolerance."""
    same_name_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(same_name_transactions) < 2:
        return 0.0
    dates = sorted(_get_days(t.date) for t in same_name_transactions)
    intervals = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
    if not intervals:
        return 0.0
    tolerance = 5
    interval_groups: dict[int, list[int]] = {}
    for interval in intervals:
        assigned = False
        for group_interval in interval_groups:
            if abs(interval - group_interval) <= tolerance:
                interval_groups[group_interval].append(interval)
                assigned = True
                break
        if not assigned:
            interval_groups[interval] = [interval]
    most_common_group_size = max(len(group) for group in interval_groups.values())
    return most_common_group_size / len(intervals)


# = First Week (Variance Attack) Features =#


# def days_between_user_txns(transaction: Transaction,
# all_transactions: list[Transaction]) -> float:
#     """Average days between user's transactions with the same merchant."""
#     dates = [
#         datetime.strptime(t.date, "%Y-%m-%d")
#         for t in all_transactions
#         if t.user_id == transaction.user_id and t.name == transaction.name
#     ]
#     if len(dates) < 2:
#         return 999
#     dates.sort()
#     day_diffs = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
#     return sum(day_diffs) / len(day_diffs)

# def price_similarity_to_user_median(transaction: Transaction,
# all_transactions: list[Transaction]) -> float:
#     """How close the transaction amount is to user's median amount at this merchant."""
#     amounts = [
#         t.amount
#         for t in all_transactions
#         if t.user_id == transaction.user_id and t.name == transaction.name
#     ]
#     if not amounts:
#         return 1.0
#     median = statistics.median(amounts)
#     if median == 0:
#         return 1.0
#     return abs(transaction.amount - median) / median

# def is_small_fluctuation(transaction: Transaction,
# all_transactions: list[Transaction]) -> int:
#     """Whether transaction amount is within 5% of user's median."""
#     amounts = [
#         t.amount
#         for t in all_transactions
#         if t.user_id == transaction.user_id and t.name == transaction.name
#     ]
#     if not amounts:
#         return 0
#     median = statistics.median(amounts)
#     if median == 0:
#         return 0
#     fluctuation = abs(transaction.amount - median) / median
#     return int(fluctuation <= 0.05)

# def weekly_recurring_indicator(transaction: Transaction,
# all_transactions: list[Transaction]) -> int:
#     """
#     Detects if the user's transactions with the same
#       merchant happen around 7-day intervals.

#     Returns:
#         1 if there are at least two intervals between
#           transactions that are approximately 1 week apart (5-9 days).
#         0 otherwise.
#     """
#     dates = [
#         datetime.strptime(t.date, "%Y-%m-%d")
#         for t in all_transactions
#         if t.user_id == transaction.user_id and t.name == transaction.name
#     ]
#     if len(dates) < 2:
#         return 0
#     dates.sort()
#     weeklike_count = 0
#     for i in range(1, len(dates)):
#         days_apart = (dates[i] - dates[i-1]).days
#         if 5 <= days_apart <= 9:
#             weeklike_count += 1
#     return int(weeklike_count >= 2)


# def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict:
#     """New feature group focused on reducing variance errors."""
#     return {
#         #"days_between_user_txns": days_between_user_txns(transaction, all_transactions),
#         # "price_similarity_to_user_median": price_similarity_to_user_median(transaction, all_transactions),
#         # "is_small_fluctuation": is_small_fluctuation(transaction, all_transactions),
#         # "weekly_recurring_indicator": weekly_recurring_indicator(transaction, all_transactions),
#     }


# --- Newly Designed Feature Functions ---#


def get_vendor_category_score(transaction: Transaction) -> float:
    """Assign recurrence probability based on vendor type."""
    subscription_vendors = [
        "Apple",
        "Amazon Prime",
        "Amazon Prime Video",
        "Cleo",
        "Albert",
        "Disney+",
        "SiriusXM",
        "Dashpass",
        "Audible",
        "Norton LifeLock",
        "Adobe",
        "BET+",
        "Sony Playstation",
        "Truebill",
        "Instacart",
    ]
    loan_vendors = [
        "AfterPay",
        "Brght Lending",
        "Credit Ninja",
        "CashNetUSA",
        "Lendswift",
        "Greenline Loans",
        "Rise Up Lending",
        "Affirm",
    ]
    insurance_vendors = ["GEICO", "Lemonade Insurance", "Progressive Insurance", "Hugo Insurance", "Tn Farm Mutual"]
    telecom_vendors = ["AT&T", "Sprint", "Verizon", "TMOBILE", "Straight Talk"]
    housing_vendors = ["Waterford Grove"]

    vendor = transaction.name.lower()
    if any(v.lower() in vendor for v in subscription_vendors + loan_vendors):
        return 0.9
    elif any(v.lower() in vendor for v in insurance_vendors + telecom_vendors + housing_vendors):
        return 0.5
    else:
        return 0.2


def rolling_amount_deviation(
    transaction: Transaction, all_transactions: list[Transaction], window_size: int = 3
) -> float:
    """Calculate deviation of the latest transaction amount from the rolling mean of previous amounts."""
    user_txns = sorted(
        [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name],
        key=lambda t: t.date,
    )

    if len(user_txns) < window_size:
        return 0.0

    # Find index of current transaction
    idx = next((i for i, t in enumerate(user_txns) if t.id == transaction.id), None)
    if idx is None or idx < window_size:
        return 0.0

    previous_amounts = [user_txns[i].amount for i in range(idx - window_size, idx)]
    rolling_mean = sum(previous_amounts) / window_size
    deviation = abs(transaction.amount - rolling_mean)

    return deviation


# def get_transaction_frequency_score(transaction, all_transactions) -> float:
#     """Compute how often user transacts with same vendor."""
#     relevant = [
#         datetime.strptime(t.date, "%Y-%m-%d")
#         for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name
#     ]
#     if len(relevant) < 2:
#         return 0.0
#     duration_days = (max(relevant) - min(relevant)).days
#     return len(relevant) / (duration_days / 30.0) if duration_days > 0 else 0.0

# def get_amount_consistency_score(transaction, all_transactions) -> float:
#     """Calculate Coefficient of Variation of amounts."""
#     amounts = [
#         t.amount for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name
#     ]
#     if len(amounts) < 2:
#         return 0.0
#     mean_amt = np.mean(amounts)
#     std_amt = np.std(amounts)
#     return float(std_amt / mean_amt) if mean_amt > 0 else 0.0

# def get_day_of_month_variance(transaction, all_transactions) -> float:
#     """Calculate variance of transaction days."""
#     days = [
#         int(t.date.split("-")[2]) for t in all_transactions
#     if t.user_id == transaction.user_id and t.name == transaction.name
#     ]
#     if len(days) < 2:
#         return 999.0
#     return float(np.var(days))

# def get_interval_variance_score(transaction, all_transactions) -> float:
#     """Calculate variance of days between consecutive transactions."""
#     dates = sorted([
#         datetime.strptime(t.date, "%Y-%m-%d")
#         for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name
#     ])
#     if len(dates) < 2:
#         return 999.0
#     intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
#     return float(np.var(intervals)) if intervals else 999.0

# def get_amount_range_score(transaction) -> float:
#     """Assign recurrence probability based on amount range."""
#     amt = transaction.amount
#     if amt <= 10:
#         return 0.9
#     elif amt <= 50:
#         return 0.7
#     elif amt <= 200:
#         return 0.5
#     elif amt <= 1000:
#         return 0.3
#     else:
#         return 0.2

# def get_user_vendor_recurrence_score(transaction, all_transactions) -> float:
#     """Compute how often a user has recurring transactions with the vendor."""
#     user_txns = [t for t in all_transactions if t.user_id == transaction.user_id]
#     vendor_txns = [t for t in user_txns if t.name == transaction.name]
#     if not vendor_txns:
#         return 0.0
#     recurring_txns = [t for t in vendor_txns if getattr(t, 'recurring', 0) == 1]
#     return len(recurring_txns) / len(vendor_txns)

# --- Feature Extraction Function ---


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict:
    """Generate all new features for a transaction."""
    features = {}

    features["vendor_category_score"] = get_vendor_category_score(transaction)
    features["rolling_amount_deviation"] = rolling_amount_deviation(transaction, all_transactions)
    # features["transaction_frequency_score"] = get_transaction_frequency_score(transaction, all_transactions)
    # features["amount_consistency_score"] = get_amount_consistency_score(transaction, all_transactions)
    # features["day_of_month_variance"] = get_day_of_month_variance(transaction, all_transactions)
    # features["interval_variance_score"] = get_interval_variance_score(transaction, all_transactions)
    # features["amount_range_score"] = get_amount_range_score(transaction)
    # features["user_vendor_recurrence_score"] = get_user_vendor_recurrence_score(transaction, all_transactions)

    return features
