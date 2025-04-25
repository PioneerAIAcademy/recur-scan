from datetime import date, datetime

import numpy as np
from scipy.stats import entropy

from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date

# Helper Functions


def _aggregate_transactions(transactions: list[Transaction]) -> dict[str, dict[str, list[Transaction]]]:
    """Group transactions by user ID and merchant name for efficient feature computation.

    Args:
        transactions (List[Transaction]): List of all transaction objects.

    Returns:
        Dict[str, Dict[str, List[Transaction]]]: Nested dictionary with user_id as outer key,
        merchant_name as inner key, and list of transactions as values.
    """
    user_merchant_groups: dict[str, dict[str, list[Transaction]]] = {}
    for transaction in transactions:
        user_id = transaction.user_id
        merchant_name = transaction.name
        # Initialize dictionary for user if not present
        if user_id not in user_merchant_groups:
            user_merchant_groups[user_id] = {}
        # Initialize list for merchant if not present
        if merchant_name not in user_merchant_groups[user_id]:
            user_merchant_groups[user_id][merchant_name] = []
        # Append transaction to the appropriate group
        user_merchant_groups[user_id][merchant_name].append(transaction)
    return user_merchant_groups


def _calculate_intervals(dates: list[date]) -> list[int]:
    """Calculate the number of days between consecutive dates in a sorted list.

    Args:
        dates (List[datetime]): List of datetime objects, assumed to be sorted.

    Returns:
        List[int]: List of intervals in days between consecutive dates; empty if fewer than 2 dates.
    """
    intervals: list[int] = []
    # Need at least 2 dates to compute an interval
    if len(dates) < 2:
        return intervals
    # Compute days between each pair of consecutive dates
    for i in range(1, len(dates)):
        current_date = dates[i]
        previous_date = dates[i - 1]
        days_between = (current_date - previous_date).days
        intervals.append(days_between)
    return intervals


def _calculate_statistics(values: list[float]) -> dict[str, float]:
    """Compute mean and standard deviation of a list of numbers.

    Args:
        values (List[float]): List of numerical values (e.g., intervals or amounts).

    Returns:
        Dict[str, float]: Dictionary with 'mean' and 'std' keys; both 0.0 if list is empty.
    """
    stats = {}
    # Handle empty list case
    if len(values) == 0:
        stats["mean"] = 0.0
        stats["std"] = 0.0
        return stats
    # Calculate mean manually
    total = 0.0
    for num in values:
        total += num
    mean_value = total / len(values)
    # Use NumPy for efficient standard deviation calculation
    std_value = float(np.std(values))
    stats["mean"] = mean_value
    stats["std"] = std_value
    return stats


# Individual Feature Functions
# def n_transactions_same_amount(transaction: Transaction, amount_counts: dict[float, int]) -> int:
#     """Count how many transactions across all users have the same amount as the given transaction.

#     Args:
#         transaction (Transaction): The transaction to evaluate.
#         all_transactions (List[Transaction]): List of all transactions (unused here but kept for consistency).
#         amount_counts (Dict[float, int]): Precomputed counts of transactions per amount.

#     Returns:
#         int: Number of transactions with the same amount; 0 if not found in amount_counts.
#     """
#     return amount_counts.get(transaction.amount, 0)


# def percent_transactions_same_amount(
#     transaction: Transaction, all_transactions: list[Transaction], amount_counts: dict[float, int]
# ) -> float:
#     """Calculate the percentage of all transactions that match the given transaction's amount.

#     Args:
#         transaction (Transaction): The transaction to evaluate.
#         all_transactions (List[Transaction]): List of all transactions to compute total count.
#         amount_counts (Dict[float, int]): Precomputed counts of transactions per amount.

#     Returns:
#         float: Ratio of transactions with the same amount to total transactions; 0.0 if no transactions.
#     """
#     n_transactions_same_amount = amount_counts.get(transaction.amount, 0)
#     return n_transactions_same_amount / len(all_transactions) if all_transactions else 0.0


def identical_transaction_ratio_feature(
    transaction: Transaction, all_transactions: list[Transaction], merchant_trans: list[Transaction]
) -> float:
    """Calculate the ratio of merchant-specific transactions with the same amount and name to all transactions.

    Args:
        transaction (Transaction): The transaction to evaluate.
        all_transactions (List[Transaction]): List of all transactions to compute total count.
        merchant_trans (List[Transaction]): List of transactions for this user and merchant.

    Returns:
        float: Ratio of identical transactions to total transactions; 0.0 if no transactions.
    """
    identical_transaction_count = 0
    for t in merchant_trans:
        if t.amount == transaction.amount and t.name == transaction.name:
            identical_transaction_count += 1
    return identical_transaction_count / len(all_transactions) if len(all_transactions) > 0 else 0.0


def is_monthly_recurring_feature(merchant_trans: list[Transaction]) -> float:
    """Determine if transactions occur on roughly the same day each month (≤3 unique days)."""
    if len(merchant_trans) <= 1:
        return 0.0
    days = [date.day for date in [parse_date(t.date) for t in merchant_trans] if date]
    if not days:
        return 0.0
    unique_days = len(set(days))
    return 1.0 - min((unique_days - 1) / 5.0, 1.0)


def is_varying_amount_recurring_feature(interval_stats: dict[str, float], amount_stats: dict[str, float]) -> int:
    """Identify recurring transactions with varying amounts but consistent intervals.

    Args:
        interval_stats (Dict[str, float]): Mean and std of intervals between transactions.
        amount_stats (Dict[str, float]): Mean and std of transaction amounts.

    Returns:
        int: 1 if intervals are consistent (<45 days std) and amounts vary (>0.002 std/mean), 0 otherwise.
    """
    if interval_stats["std"] < 45 and amount_stats["mean"] > 0 and (amount_stats["std"] / amount_stats["mean"]) > 0.002:
        return 1
    return 0


def day_consistency_score_feature(merchant_trans: list[Transaction]) -> float:
    """Measure consistency of transaction days within a month (0 to 1 scale).

    Args:
        merchant_trans (List[Transaction]): List of transactions for this user and merchant.

    Returns:
        float: Score from 0 to 1; higher means more consistent days (lower std).
    """
    days = [date.day for date in [parse_date(t.date) for t in merchant_trans] if date]
    if not days:
        return 0.0
    if len(days) == 1:
        return 0.5
    std = float(np.std(days))
    return 1.0 - min(std / 3.0, 1.0)


def is_near_periodic_interval_feature(interval_stats: dict[str, float]) -> float:
    """Score proximity to periodic intervals (0-1)."""
    if interval_stats["mean"] == 0:
        return 0.0
    mean = interval_stats["mean"]
    std = interval_stats["std"]
    targets = [(7, 2), (30, 3), (365, 10)]
    best_score = 0.0
    for target, tolerance in targets:
        deviation = abs(mean - target) / target
        if std < 5:  # Stricter consistency
            score = 1.0 - min(deviation / (tolerance / target), 1.0)
            best_score = max(best_score, score)
    return best_score


def merchant_amount_std_feature(amount_stats: dict[str, float]) -> float:
    """Calculate normalized standard deviation of transaction amounts for the merchant.

    Args:
        amount_stats (Dict[str, float]): Mean and std of transaction amounts.

    Returns:
        float: Std divided by mean; 0.0 if mean is 0 to avoid division by zero.
    """
    return amount_stats["std"] / amount_stats["mean"] if amount_stats["mean"] > 0 else 0.0


def merchant_interval_std_feature(interval_stats: dict[str, float]) -> float:
    """Extract standard deviation of intervals between transactions.

    Args:
        interval_stats (Dict[str, float]): Mean and std of intervals between transactions.

    Returns:
        float: Standard deviation of intervals; 0.0 if no intervals.
    """
    return interval_stats["std"] if interval_stats["std"] > 0 else 30.0


def merchant_interval_mean_feature(interval_stats: dict[str, float]) -> float:
    """Extract mean of intervals between transactions.

    Args:
        interval_stats (Dict[str, float]): Mean and std of intervals between transactions.

    Returns:
        float: Mean interval in days; 0.0 if no intervals.
    """
    return interval_stats["mean"] if interval_stats["mean"] > 0 else 60.0


def time_since_last_transaction_same_merchant_feature(parsed_dates: list[date]) -> float:
    """Days since earliest transaction or average interval."""
    if not parsed_dates:
        return 0
    now = datetime.now().date()
    if len(parsed_dates) == 1:
        return (now - parsed_dates[0]).days / 365  # Normalize by year
    intervals = _calculate_intervals(parsed_dates)
    return (sum(intervals) / len(intervals)) / 365 if intervals else (now - min(parsed_dates)).days / 365


def is_deposit_feature(transaction: Transaction, merchant_trans: list[Transaction]) -> int:
    """Identify if the transaction might be a recurring deposit based on amount and frequency.

    Args:
        transaction (Transaction): The transaction to evaluate.
        merchant_trans (List[Transaction]): List of transactions for this user and merchant.

    Returns:
        int: 1 if amount is positive and there are ≥3 transactions, 0 otherwise.
    """
    is_deposit = 0
    if transaction.amount > 0 and len(merchant_trans) >= 3:
        is_deposit = 1
    return is_deposit


def day_of_week_feature(transaction: Transaction) -> float:
    """Day of the week (0-6, Monday-Sunday)."""
    date = parse_date(transaction.date)
    return date.weekday() / 6 if date else 0


def transaction_month_feature(transaction: Transaction) -> float:
    """Month of the transaction (1-12)."""
    date = parse_date(transaction.date)
    return (date.month - 1) / 11 if date else 0


def rolling_amount_mean_feature(merchant_trans: list[Transaction]) -> float:
    """Rolling mean of last 3 transaction amounts."""
    amounts = [t.amount for t in merchant_trans[-3:]]  # Last 3 transactions
    return sum(amounts) / len(amounts) if amounts else 0.0


def low_amount_variation_feature(amount_stats: dict[str, float]) -> int:
    """Indicator for low amount variation (std/mean ≤ 0.1)."""
    ratio = amount_stats["std"] / amount_stats["mean"] if amount_stats["mean"] > 0 else float("inf")
    return 1 if ratio <= 0.1 else 0


def recurrence_likelihood_feature(
    merchant_trans: list[Transaction], interval_stats: dict[str, float], amount_stats: dict[str, float]
) -> float:
    interval_std = interval_stats["std"]
    interval_score = 1 / (interval_std / 10.0 + 1)
    mean_amount = amount_stats["mean"]
    divisor = amount_stats["std"] / max(mean_amount, 0.01) + 1
    amount_score = 1 / divisor if divisor != 0 else 0.0
    frequency_score = min(len(merchant_trans) / 5.0, 1.0)
    return interval_score * amount_score * frequency_score


def is_single_transaction_feature(merchant_trans: list[Transaction]) -> int:
    """Check if there is only one transaction for this user-merchant pair.

    Args:
        merchant_trans (List[Transaction]): List of transactions for the user and merchant.

    Returns:
        int: 1 if there is only one transaction, 0 otherwise.
    """
    return 1 if len(merchant_trans) == 1 else 0


def interval_variability_feature(interval_stats: dict[str, float]) -> float:
    """Calculate the coefficient of variation for transaction intervals.

    Args:
        interval_stats (Dict[str, float]): Dictionary with 'mean' and 'std' of intervals.

    Returns:
        float: Coefficient of variation (std / mean), or 0 if mean is 0.
    """
    mean = interval_stats["mean"]
    if mean == 0:
        return 1.0  # High variability for singletons
    return min(interval_stats["std"] / mean, 2.0)  # Cap at 2 for extreme cases


def merchant_amount_frequency_feature(merchant_trans: list[Transaction]) -> int:
    """Count the number of unique transaction amounts for the user-merchant pair.

    Args:
        merchant_trans (List[Transaction]): List of transactions for the user and merchant.

    Returns:
        int: Number of unique transaction amounts.
    """
    unique_amounts = {trans.amount for trans in merchant_trans}
    return len(unique_amounts)


def non_recurring_irregularity_score(
    merchant_trans: list[Transaction], interval_stats: dict[str, float], amount_stats: dict[str, float]
) -> float:
    """Calculate a score indicating likelihood of a transaction being non-recurring based on irregularity.

    Args:
        merchant_trans (List[Transaction]): List of transactions for the user and merchant.
        interval_stats (Dict[str, float]): Mean and std of intervals between transactions.
        amount_stats (Dict[str, float]): Mean and std of transaction amounts.

    Returns:
        float: Score between 0 and 1; higher values indicate more irregularity (non-recurring).
    """
    # Component 1: Interval variability (std/mean, capped at 1.0)
    mean_interval = interval_stats["mean"]
    interval_var = interval_stats["std"] / mean_interval if mean_interval > 0 else 0.0
    interval_score = min(interval_var, 1.0)

    # Component 2: Amount variability (std/mean from amount_stats, higher → more non-recurring)
    amount_var = amount_stats["std"] / amount_stats["mean"] if amount_stats["mean"] > 0 else 0.0
    amount_score = min(amount_var, 1.0)  # Cap at 1.0, high variability = non-recurring

    # Component 3: Inverse frequency (lower frequency → more non-recurring)
    frequency_score = 1.0 - min(len(merchant_trans) / 5.0, 1.0)

    # Weighted average
    weights = [0.4, 0.3, 0.3]  # Interval, amount, frequency
    total_score = weights[0] * interval_score + weights[1] * amount_score + weights[2] * frequency_score
    return min(total_score, 1.0)  # Ensure score stays in 0-1 range


def transaction_pattern_complexity(merchant_trans: list[Transaction], interval_stats: dict[str, float]) -> float:
    """Calculate a complexity score for the transaction pattern, higher for non-recurring.

    Args:
        merchant_trans (List[Transaction]): List of transactions for the user and merchant.
        interval_stats (Dict[str, float]): Mean and std of intervals between transactions.

    Returns:
        float: Score between 0 and 1; higher indicates more complex/non-recurring patterns.
    """
    parsed_dates = [date for date in [parse_date(t.date) for t in merchant_trans] if date is not None]
    intervals = _calculate_intervals(parsed_dates)
    if not intervals:
        return 0.0

    # Component 1: Interval entropy (distribution complexity)
    bins = [min(max(1, int(i / 7)), 52) for i in intervals]
    value_counts = np.bincount(bins, minlength=53)[1:]
    interval_entropy = float(entropy(value_counts / value_counts.sum()) / np.log(52) if value_counts.sum() > 0 else 0.0)

    # Component 2: Interval variability (std/mean from interval_stats)
    mean_interval = interval_stats["mean"]
    interval_var = float(interval_stats["std"] / mean_interval if mean_interval > 0 else 0.0)
    interval_var_score = min(interval_var, 1.0)  # Cap at 1.0 for normalization

    # Component 3: Amount diversity
    amounts = [t.amount for t in merchant_trans]
    amount_entropy = float(min(len(set(amounts)) / 10.0, 1.0) if amounts else 0.0)

    # Component 4: Inverse frequency
    frequency_score = float(1.0 - min(len(merchant_trans) / 5.0, 1.0))

    # Weighted average
    weights = [0.4, 0.3, 0.2, 0.1]  # Entropy, variability, amount, frequency
    total_score = (
        weights[0] * interval_entropy
        + weights[1] * interval_var_score
        + weights[2] * amount_entropy
        + weights[3] * frequency_score
    )
    return float(min(total_score, 1.0))  # Ensure score stays in 0-1 range


def date_irregularity_dominance(
    merchant_trans: list[Transaction], interval_stats: dict[str, float], amount_stats: dict[str, float]
) -> float:
    """Score emphasizing date irregularity for non-recurring transactions.

    Args:
        merchant_trans (List[Transaction]): Transactions for the user and merchant.
        interval_stats (Dict[str, float]): Mean and std of intervals.
        amount_stats (Dict[str, float]): Mean and std of amounts.

    Returns:
        float: Score 0-1; higher indicates stronger non-recurring due to irregular dates.
    """
    # Explicitly filter None values for mypy
    parsed_dates = [date for date in [parse_date(t.date) for t in merchant_trans] if date is not None]
    intervals = _calculate_intervals(parsed_dates)
    n_trans = len(merchant_trans)
    if n_trans <= 1:
        return 0.5

    bins = [min(max(1, int(i / 7)), 52) for i in intervals]
    value_counts = np.bincount(bins, minlength=53)[1:]
    entropy_score = float(entropy(value_counts / value_counts.sum()) / np.log(52) if value_counts.sum() > 0 else 0.0)
    mean = interval_stats["mean"]
    deviation = min(abs(mean - target) / target for target in [7, 30, 365])
    deviation_score = float(min(deviation * 3, 1.0))
    frequency_score = float(1.0 - min(n_trans / 5.0, 1.0))
    amount_consistency = float(
        1.0 - min(amount_stats["std"] / amount_stats["mean"] if amount_stats["mean"] > 0 else 0.0, 1.0)
    )
    weights = [0.5, 0.3, 0.1, 0.1]
    return float(
        min(
            weights[0] * entropy_score
            + weights[1] * deviation_score
            + weights[2] * frequency_score
            + weights[3] * amount_consistency,
            1.0,
        )
    )
