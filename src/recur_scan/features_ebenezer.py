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
    """Get the average amount of transactions in all_transactions
    in the same month as transaction"""
    transaction_month = datetime.strptime(transaction.date, "%Y-%m-%d").month
    same_month_transactions = [
        t for t in all_transactions if datetime.strptime(t.date, "%Y-%m-%d").month == transaction_month
    ]
    if not same_month_transactions:
        return 0.0
    return sum(t.amount for t in same_month_transactions) / len(same_month_transactions)


def get_std_amount_same_month(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the standard deviation of amounts for transactions in all_
    transactions in the same month as transaction"""
    transaction_month = datetime.strptime(transaction.date, "%Y-%m-%d").month
    same_month_transactions = [
        t for t in all_transactions if datetime.strptime(t.date, "%Y-%m-%d").month == transaction_month
    ]
    if len(same_month_transactions) < 2:
        return 0.0
    return statistics.stdev(t.amount for t in same_month_transactions)


def get_n_transactions_same_user_id(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_
    transactions with the same user_id as transaction"""
    return len([t for t in all_transactions if t.user_id == transaction.user_id])


def get_percent_transactions_same_user_id(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in
    all_transactions with the same user_id as transaction"""
    if not all_transactions:
        return 0.0
    n_same_user_id = len([t for t in all_transactions if t.user_id == transaction.user_id])
    return n_same_user_id / len(all_transactions)


def get_percent_transactions_same_day_of_week(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in
    all_transactions on the same day of the week as transaction"""
    if not all_transactions:
        return 0.0
    transaction_day_of_week = datetime.strptime(transaction.date, "%Y-%m-%d").weekday()
    n_same_day_of_week = len([
        t for t in all_transactions if datetime.strptime(t.date, "%Y-%m-%d").weekday() == transaction_day_of_week
    ])
    return n_same_day_of_week / len(all_transactions)


def get_avg_amount_same_day_of_week(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the average amount of transactions in
    all_transactions on the same day of the week as transaction"""
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


# ==================


def get_avg_time_between_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the average time difference (in days) between transactions with the same name."""
    same_name_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name], key=lambda t: datetime.strptime(t.date, "%Y-%m-%d")
    )
    if len(same_name_transactions) < 2:
        return 0.0
    time_differences = [
        (
            datetime.strptime(same_name_transactions[i + 1].date, "%Y-%m-%d")
            - datetime.strptime(same_name_transactions[i].date, "%Y-%m-%d")
        ).days
        for i in range(len(same_name_transactions) - 1)
    ]
    return sum(time_differences) / len(time_differences)


def get_is_recurring(transaction: Transaction, all_transactions: list[Transaction], threshold: int = 30) -> int:
    """Check if the transaction is recurring within a given threshold (e.g., 30 days)."""
    same_name_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name], key=lambda t: datetime.strptime(t.date, "%Y-%m-%d")
    )
    if len(same_name_transactions) < 2:
        return 0
    time_differences = [
        (
            datetime.strptime(same_name_transactions[i + 1].date, "%Y-%m-%d")
            - datetime.strptime(same_name_transactions[i].date, "%Y-%m-%d")
        ).days
        for i in range(len(same_name_transactions) - 1)
    ]
    return int(any(diff <= threshold for diff in time_differences))


def get_median_amount_same_name(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the median amount of transactions with the same name."""
    same_name_transactions = [t.amount for t in all_transactions if t.name == transaction.name]
    if not same_name_transactions:
        return 0.0
    return statistics.median(same_name_transactions)


def get_amount_range_same_name(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the range (max - min) of transaction amounts with the same name."""
    same_name_transactions = [t.amount for t in all_transactions if t.name == transaction.name]
    if not same_name_transactions:
        return 0.0
    return max(same_name_transactions) - min(same_name_transactions)


def get_day_of_week(transaction: Transaction) -> int:
    """Get the day of the week for the transaction (0=Monday, 6=Sunday)."""
    return datetime.strptime(transaction.date, "%Y-%m-%d").weekday()


def get_is_weekend(transaction: Transaction) -> int:
    """Check if the transaction occurred on a weekend."""
    day_of_week = datetime.strptime(transaction.date, "%Y-%m-%d").weekday()
    return int(day_of_week >= 5)


def get_user_avg_transaction_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the average transaction amount for the user."""
    user_transactions = [t.amount for t in all_transactions if t.user_id == transaction.user_id]
    if not user_transactions:
        return 0.0
    return sum(user_transactions) / len(user_transactions)


def get_user_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions made by the user."""
    return len([t for t in all_transactions if t.user_id == transaction.user_id])


# crazy feature expected to increase  the recall


def get_amount_variance(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the variance of transaction amounts with the same name."""
    amounts = [t.amount for t in all_transactions if t.name == transaction.name]
    if len(amounts) < 2:
        return 0.0
    return statistics.variance(amounts)


def get_amount_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Check if the transaction amount matches the most frequent amount for the same name."""
    amounts = [t.amount for t in all_transactions if t.name == transaction.name]
    if not amounts:
        return 0
    most_frequent_amount = max(set(amounts), key=amounts.count)
    return int(transaction.amount == most_frequent_amount)


# def get_normalized_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """Normalize the transaction amount by dividing it by the user's average transaction amount."""
#     user_transactions = [t.amount for t in all_transactions if t.user_id == transaction.user_id]
#     if not user_transactions:
#         return 0.0
#     return transaction.amount / (sum(user_transactions) / len(user_transactions))


def get_is_monthly(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Check if the transaction occurs approximately every 30 days."""
    dates = sorted([datetime.strptime(t.date, "%Y-%m-%d") for t in all_transactions if t.name == transaction.name])
    if len(dates) < 2:
        return 0
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    return int(all(25 <= interval <= 35 for interval in intervals))


def get_is_weekly(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Check if the transaction occurs approximately every 7 days."""
    dates = sorted([datetime.strptime(t.date, "%Y-%m-%d") for t in all_transactions if t.name == transaction.name])
    if len(dates) < 2:
        return 0
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    return int(all(5 <= interval <= 9 for interval in intervals))


# from scipy.stats import skew

# def get_amount_skewness(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """Calculate the skewness of transaction amounts with the same name."""
#     amounts = [t.amount for t in all_transactions if t.name == transaction.name]
#     if len(amounts) < 2 or np.var(amounts) < 1e-6:  # Check for insufficient variation
#         return 0.0
#     return skew(amounts)

# from scipy.stats import kurtosis

# def get_amount_kurtosis(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """Calculate the kurtosis of transaction amounts with the same name."""
#     amounts = [t.amount for t in all_transactions if t.name == transaction.name]
#     if len(amounts) < 2 or np.var(amounts) < 1e-6:  # Check for insufficient variation
#         return 0.0
#     return kurtosis(amounts)


def get_keyword_match(transaction: Transaction) -> int:
    """Check if the transaction name contains recurring-related keywords."""
    keywords = ["subscription", "monthly", "rent", "bill", "payment"]
    return int(any(keyword in transaction.name.lower() for keyword in keywords))


def get_new_features(transaction: Transaction, grouped_transactions: list[Transaction]) -> dict:
    features = {}

    # Existing features
    features["n_transactions_same_name"] = float(get_n_transactions_same_name(transaction, grouped_transactions))
    features["percent_transactions_same_name"] = float(
        get_percent_transactions_same_name(transaction, grouped_transactions)
    )
    features["avg_amount_same_name"] = float(get_avg_amount_same_name(transaction, grouped_transactions))
    features["std_amount_same_name"] = float(get_std_amount_same_name(transaction, grouped_transactions))

    # New features
    features["avg_time_between_transactions"] = float(
        get_avg_time_between_transactions(transaction, grouped_transactions)
    )
    features["is_recurring"] = float(get_is_recurring(transaction, grouped_transactions))
    features["median_amount_same_name"] = float(get_median_amount_same_name(transaction, grouped_transactions))
    features["amount_range_same_name"] = float(get_amount_range_same_name(transaction, grouped_transactions))
    features["day_of_week"] = float(get_day_of_week(transaction))
    features["is_weekend"] = float(get_is_weekend(transaction))
    features["user_avg_transaction_amount"] = float(get_user_avg_transaction_amount(transaction, grouped_transactions))
    features["user_transaction_frequency"] = float(get_user_transaction_frequency(transaction, grouped_transactions))

    # Crazy features
    features["amount_variance"] = float(get_amount_variance(transaction, grouped_transactions))
    features["amount_consistency"] = float(get_amount_consistency(transaction, grouped_transactions))
    features["is_monthly"] = float(get_is_monthly(transaction, grouped_transactions))
    features["is_weekly"] = float(get_is_weekly(transaction, grouped_transactions))
    features["keyword_match"] = float(get_keyword_match(transaction))

    return features
