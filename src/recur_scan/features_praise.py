import itertools
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from itertools import pairwise
from statistics import mean

import numpy as np

from recur_scan.transactions import Transaction


def get_average_transaction_amount(all_transactions: list[Transaction]) -> float:
    return sum(t.amount for t in all_transactions) / len(all_transactions)


def get_max_transaction_amount(all_transactions: list[Transaction]) -> float:
    return max(t.amount for t in all_transactions)


def get_min_transaction_amount(all_transactions: list[Transaction]) -> float:
    return min(t.amount for t in all_transactions)


def get_most_frequent_names(all_transactions: list[Transaction]) -> list[str]:
    grouped_transactions = defaultdict(list)
    for transaction in all_transactions:
        grouped_transactions[(transaction.user_id, transaction.name)].append(transaction)
    return [
        name
        for (_user_id, name), transactions in grouped_transactions.items()
        if any(count > 1 for count in Counter(t.amount for t in transactions).values())
    ]


def is_recurring(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    grouped_transactions = defaultdict(list)
    for t in all_transactions:
        grouped_transactions[(t.user_id, t.name)].append(t)
    for (_user_id, name), transactions in grouped_transactions.items():
        if transaction.name == name:
            transactions.sort(key=lambda x: datetime.strptime(x.date, "%Y-%m-%d"))
            for i in range(1, len(transactions)):
                date_diff = datetime.strptime(transactions[i].date, "%Y-%m-%d") - datetime.strptime(
                    transactions[i - 1].date, "%Y-%m-%d"
                )
                if (
                    transactions[i].amount == transactions[i - 1].amount
                    or transactions[i].amount == 1
                    or str(transactions[i].amount).endswith(".99")
                ) and (
                    (timedelta(days=6) <= date_diff <= timedelta(days=8))
                    or (timedelta(days=13) <= date_diff <= timedelta(days=15))
                    or (timedelta(days=28) <= date_diff <= timedelta(days=31))
                    or (timedelta(days=58) <= date_diff <= timedelta(days=62))
                ):
                    return True
    return False


def amount_ends_in_99(transaction: Transaction) -> bool:
    return round(transaction.amount % 1, 2) == 0.99


def amount_ends_in_00(transaction: Transaction) -> bool:
    return round(transaction.amount % 1, 2) == 0.00


def is_recurring_merchant(transaction: Transaction) -> bool:
    recurring_keywords = {
        "at&t",
        "google play",
        "verizon",
        "vz wireless",
        "t-mobile",
        "apple",
        "disney+",
        "amazon prime",
    }
    return any(keyword in transaction.name.lower() for keyword in recurring_keywords)


def get_n_transactions_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    return sum(1 for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount)


def get_percent_transactions_same_merchant_amount(
    transaction: Transaction, all_transactions: list[Transaction]
) -> float:
    return get_n_transactions_same_merchant_amount(transaction, all_transactions) / len(all_transactions)


def get_interval_variance_coefficient(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the coefficient of variation for transaction intervals to measure consistency."""
    same_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount],
        key=lambda x: datetime.strptime(x.date, "%Y-%m-%d"),
    )
    if len(same_transactions) < 3:  # Need at least 3 to establish a pattern
        return 1.0  # High variance (low consistency)
    intervals = [
        (datetime.strptime(t2.date, "%Y-%m-%d") - datetime.strptime(t1.date, "%Y-%m-%d")).days
        for t1, t2 in pairwise(same_transactions)
    ]
    try:
        mean_interval = statistics.mean(intervals)
        if mean_interval == 0:
            return 1.0
        # Lower value means more consistent intervals
        return statistics.stdev(intervals) / mean_interval if mean_interval > 0 else 1.0
    except statistics.StatisticsError:
        return 1.0


def get_avg_days_between_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    same_transactions = sorted(
        (t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount),
        key=lambda x: x.date,
    )
    if len(same_transactions) < 2:
        return 0.0
    intervals = [
        (datetime.strptime(t2.date, "%Y-%m-%d").date() - datetime.strptime(t1.date, "%Y-%m-%d").date()).days
        for t1, t2 in pairwise(same_transactions)
    ]
    return sum(intervals) / len(intervals) if intervals else 0.0


def get_stddev_days_between_same_merchant_amount(
    transaction: Transaction, all_transactions: list[Transaction]
) -> float:
    same_transactions = sorted(
        (t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount),
        key=lambda x: x.date,
    )
    if len(same_transactions) < 2:
        return 0.0
    intervals = [
        (datetime.strptime(t2.date, "%Y-%m-%d").date() - datetime.strptime(t1.date, "%Y-%m-%d").date()).days
        for t1, t2 in pairwise(same_transactions)
    ]
    try:
        return statistics.stdev(intervals)
    except statistics.StatisticsError:
        return 0.0


def get_days_since_last_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    same_transactions = [
        t
        for t in all_transactions
        if t.name == transaction.name and t.amount == transaction.amount and t.date < transaction.date
    ]
    if not same_transactions:
        return 0
    last_date = max(datetime.strptime(t.date, "%Y-%m-%d").date() for t in same_transactions)
    return (datetime.strptime(transaction.date, "%Y-%m-%d").date() - last_date).days


def is_expected_transaction_date(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if transaction occurs on an expected date based on previous patterns"""
    same_transactions = sorted(
        [
            t
            for t in all_transactions
            if t.name == transaction.name and t.amount == transaction.amount and t.date < transaction.date
        ],
        key=lambda x: x.date,
    )

    if len(same_transactions) < 2:
        return False

    # Calculate average interval
    intervals = [
        (datetime.strptime(t2.date, "%Y-%m-%d").date() - datetime.strptime(t1.date, "%Y-%m-%d").date()).days
        for t1, t2 in itertools.pairwise(same_transactions)
    ]

    if not intervals:
        return False

    avg_interval = sum(intervals) / len(intervals)

    # Get the last transaction date before the current one
    last_date = datetime.strptime(same_transactions[-1].date, "%Y-%m-%d").date()
    current_date = datetime.strptime(transaction.date, "%Y-%m-%d").date()

    # Calculate expected date
    expected_date = last_date + timedelta(days=round(avg_interval))

    # Allow for a window of +/- 3 days
    return abs((current_date - expected_date).days) <= 3


def has_incrementing_numbers(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if transaction descriptions contain incrementing numbers (non-recurring pattern)"""
    # Filter transactions by merchant name
    same_merchant_transactions = sorted(
        [t for t in all_transactions if t.user_id == transaction.user_id], key=lambda x: x.date
    )

    if len(same_merchant_transactions) < 3:
        return False

    # Extract numbers from transaction names in order of date
    import re

    number_patterns = []
    for t in same_merchant_transactions:
        numbers = re.findall(r"\d+", t.name)
        if numbers:
            number_patterns.append(int(numbers[-1]))  # Use the last number in the name

    # Check if numbers form a strictly incrementing sequence
    if len(number_patterns) >= 3:
        return all(number_patterns[i + 1] - number_patterns[i] == 1 for i in range(len(number_patterns) - 1))

    return False


def has_consistent_reference_codes(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if transaction descriptions contain consistent reference codes"""
    same_merchant_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]

    if len(same_merchant_transactions) < 2:
        return False

    # Extract potential reference codes (alphanumeric sequences)
    import re

    ref_codes = []
    for t in same_merchant_transactions:
        # Look for patterns like REF:12345 or ID-ABC123
        pattern: str = r"(?:ref|id|no)[-:]\s*([a-zA-Z0-9]+)"
        matches = re.findall(pattern, t.name.lower())
        if matches:
            ref_codes.extend(matches)

    # Check if the same reference code appears multiple times
    if ref_codes:
        counter = Counter(ref_codes)
        # If any reference code appears multiple times, it's likely not a unique transaction
        return any(count > 1 for count in counter.values())

    return False


def calculate_markovian_probability(transaction: Transaction, all_transactions: list[Transaction], n: int = 3) -> float:
    """Calculate the probability of another transaction given the past n transactions."""

    # Filter transactions by the same merchant
    same_merchant_transactions = [t for t in all_transactions if t.name == transaction.name]

    if len(same_merchant_transactions) <= n:
        return 0.0  # Not enough data to calculate probability

    # Extract the last n transactions
    same_merchant_transactions.sort(key=lambda x: datetime.strptime(x.date, "%Y-%m-%d"))
    recent_transactions = same_merchant_transactions[-(n + 1) :]

    # Check if the pattern of the last n transactions matches the current transaction
    pattern_matches = all(
        recent_transactions[i].amount == recent_transactions[i + 1].amount for i in range(len(recent_transactions) - 1)
    )
    return 1.0 if pattern_matches else 0.0


def calculate_streaks(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Calculate the number of consecutive transactions within expected intervals."""
    same_merchant_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name],
        key=lambda x: datetime.strptime(x.date, "%Y-%m-%d"),
    )
    if len(same_merchant_transactions) < 2:
        return 0  # Not enough data to calculate streaks

    # Calculate intervals between transactions
    intervals = [
        (datetime.strptime(t2.date, "%Y-%m-%d") - datetime.strptime(t1.date, "%Y-%m-%d")).days
        for t1, t2 in pairwise(same_merchant_transactions)
    ]

    # Count consecutive intervals within expected ranges (e.g., weekly, monthly)
    streak = 0
    max_streak = 0
    for interval in intervals:
        if 6 <= interval <= 8 or 28 <= interval <= 31:  # Weekly or monthly intervals
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

    return max_streak


def get_ewma_interval_deviation(
    transaction: Transaction, all_transactions: list[Transaction], alpha: float = 0.3
) -> float:
    """Calculate deviation of the most recent interval from the EWMA of past intervals."""
    same_transactions = sorted(
        [
            t
            for t in all_transactions
            if t.name == transaction.name and t.amount == transaction.amount and t.date < transaction.date
        ],
        key=lambda x: x.date,
    )
    if len(same_transactions) < 3:
        return 1.0

    intervals = [
        (datetime.strptime(t2.date, "%Y-%m-%d") - datetime.strptime(t1.date, "%Y-%m-%d")).days
        for t1, t2 in pairwise(same_transactions)
    ]

    ewma = float(intervals[0])
    for interval in intervals[1:]:
        ewma = alpha * interval + (1 - alpha) * ewma

    last_interval = (
        datetime.strptime(transaction.date, "%Y-%m-%d") - datetime.strptime(same_transactions[-1].date, "%Y-%m-%d")
    ).days

    return abs(last_interval - ewma) / ewma if ewma else 1.0


def get_hurst_exponent(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Estimate the Hurst exponent to assess long-term memory in transaction intervals."""
    same_transactions = sorted(
        [
            t
            for t in all_transactions
            if t.name == transaction.name and t.amount == transaction.amount and t.date < transaction.date
        ],
        key=lambda x: x.date,
    )
    if len(same_transactions) < 4:
        return 0.5  # Default to random-walk-like

    intervals: list[float] = [
        (datetime.strptime(t2.date, "%Y-%m-%d") - datetime.strptime(t1.date, "%Y-%m-%d")).days
        for t1, t2 in pairwise(same_transactions)
    ]

    n = len(intervals)
    mean = sum(intervals) / n
    cumulative_deviation: list[float] = [sum(intervals[: i + 1]) - (i + 1) * mean for i in range(n)]
    r = max(cumulative_deviation) - min(cumulative_deviation)
    s = statistics.stdev(intervals)

    if s == 0:
        return 0.5

    hurst = (r / s) ** 0.5
    return float(round(hurst, 3))


def get_fourier_periodicity_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Use FFT to detect dominant frequency component indicating periodic behavior."""
    same_transactions = sorted(
        [
            t
            for t in all_transactions
            if t.name == transaction.name and t.amount == transaction.amount and t.date < transaction.date
        ],
        key=lambda x: x.date,
    )

    if len(same_transactions) < 6:
        return 0.0

    intervals = np.array(
        [
            (datetime.strptime(t2.date, "%Y-%m-%d") - datetime.strptime(t1.date, "%Y-%m-%d")).days
            for t1, t2 in pairwise(same_transactions)
        ],
        dtype=float,
    )

    centered = intervals - np.mean(intervals)
    fft = np.fft.fft(centered)
    magnitude = np.abs(fft[1:])

    score = np.max(magnitude) / np.sum(magnitude) if np.sum(magnitude) else 0.0
    return float(score)


def is_recurring_through_past_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if the transaction is recurring based on past transactions."""
    same_transactions = [t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount]
    if len(same_transactions) < 3:
        return False

    # Check if the transaction occurs at regular intervals (weekly, monthly, etc.)
    intervals = [
        (datetime.strptime(t2.date, "%Y-%m-%d") - datetime.strptime(t1.date, "%Y-%m-%d")).days
        for t1, t2 in pairwise(same_transactions)
    ]

    # Check for regular intervals (e.g., weekly or monthly)
    return any(6 <= interval <= 8 or 28 <= interval <= 31 for interval in intervals)


def get_amount_zscore(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Standardize this transaction's amount relative to the user's overall distribution."""
    user_amounts = [t.amount for t in all_transactions if t.user_id == transaction.user_id]
    if len(user_amounts) < 2:
        return 0.0
    mean = statistics.mean(user_amounts)
    stdev = statistics.stdev(user_amounts)
    return (transaction.amount - mean) / stdev if stdev > 0 else 0.0


def is_amount_outlier(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Flag if amount is more than away from the user's mean."""
    return abs(get_amount_zscore(transaction, all_transactions)) > 2


def get_stddev_amount_same_merchant(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """How variable are amounts at this merchant for the user?"""
    same = [t.amount for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name]
    return statistics.stdev(same) if len(same) >= 2 else 0.0


def get_avg_days_between_same_merchant(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Average gap in days between transactions at this merchant (ignoring amount)."""
    same = sorted(
        [
            datetime.strptime(t.date, "%Y-%m-%d").date()
            for t in all_transactions
            if t.user_id == transaction.user_id and t.name == transaction.name
        ],
    )
    if len(same) < 2:
        return 0.0
    intervals = [(t2 - t1).days for t1, t2 in pairwise(same)]
    return sum(intervals) / len(intervals)


def is_weekend_transaction(transaction: Transaction) -> bool:
    """Did this fall on a Saturday or Sunday?"""
    dow = datetime.strptime(transaction.date, "%Y-%m-%d").weekday()
    return dow >= 5


def is_end_of_month_transaction(transaction: Transaction) -> bool:
    """Is the date the last day of its month?"""
    d = datetime.strptime(transaction.date, "%Y-%m-%d").date()
    return (d + timedelta(days=1)).month != d.month


def get_days_since_first_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Number of days between the user's very first transaction and this one."""
    user_dates = [
        datetime.strptime(t.date, "%Y-%m-%d").date() for t in all_transactions if t.user_id == transaction.user_id
    ]
    if not user_dates:
        return 0
    first = min(user_dates)
    current = datetime.strptime(transaction.date, "%Y-%m-%d").date()
    return (current - first).days


def get_amount_coefficient_of_variation(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Relative variability of amounts for this user."""
    user_amounts = [t.amount for t in all_transactions if t.user_id == transaction.user_id]
    if len(user_amounts) < 2:
        return 0.0
    mean = statistics.mean(user_amounts)
    stdev = statistics.stdev(user_amounts)
    return (stdev / mean) if mean > 0 else 0.0


def get_unique_merchants_count(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """How many distinct merchants has this user transacted with?"""
    return len({t.name for t in all_transactions if t.user_id == transaction.user_id})


def get_amount_quantile(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Position of this amount in the user's distribution (0-1)."""
    user_amounts = sorted(t.amount for t in all_transactions if t.user_id == transaction.user_id)
    rank = sum(1 for a in user_amounts if a <= transaction.amount)
    return rank / len(user_amounts)


def is_consistent_weekday_pattern(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Do same-amount merchant transactions always fall on the same weekday?"""
    same = [
        t
        for t in all_transactions
        if t.user_id == transaction.user_id and t.name == transaction.name and t.amount == transaction.amount
    ]
    if len(same) < 3:
        return False
    weekdays = {datetime.strptime(t.date, "%Y-%m-%d").weekday() for t in same}
    return len(weekdays) == 1


def get_recurrence_score_by_amount(
    transaction: Transaction, all_transactions: list[Transaction], amount_tolerance: float = 1.0
) -> float:
    """
    Estimate if a transaction is recurring based on amount similarity and time intervals.
    Returns a score from 0.0 to 1.0 (higher means more likely recurring).
    """
    # Filter transactions for the same user with similar amounts
    similar_transactions = [
        t
        for t in all_transactions
        if t.user_id == transaction.user_id and abs(t.amount - transaction.amount) <= amount_tolerance
    ]

    if len(similar_transactions) < 3:
        return 0.0  # Not enough data to infer recurrence

    # Sort transactions by date
    dates = sorted(datetime.strptime(t.date, "%Y-%m-%d").date() for t in similar_transactions)
    gaps = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

    if not gaps:
        return 0.0

    # Basic statistics
    mean_gap = statistics.mean(gaps)
    std_dev = statistics.stdev(gaps) if len(gaps) > 1 else 0.0

    # Compare mean gap to common frequencies
    common_frequencies = [7, 14, 28, 30, 31]
    closest_gap = min(common_frequencies, key=lambda x: abs(x - mean_gap))
    deviation = abs(mean_gap - closest_gap)

    # Scoring
    regularity_score = max(0.0, 1.0 - (std_dev / mean_gap if mean_gap else 1.0))
    alignment_score = max(0.0, 1.0 - deviation / closest_gap)

    return round((regularity_score + alignment_score) / 2, 2)


def compare_recent_to_historical_average(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Compare the transaction amount to the historical average for the same merchant and user.
    Returns a similarity score (1.0 = perfect match, lower = more different).
    """
    # Filter out current and future transactions, keep only past ones
    past_transactions = [
        t
        for t in all_transactions
        if t.user_id == transaction.user_id and t.name == transaction.name and t.date < transaction.date
    ]

    if len(past_transactions) < 3:
        return 0.0  # Not enough past data to compare reliably

    # Calculate historical mean and standard deviation
    amounts = [t.amount for t in past_transactions]
    mean = statistics.mean(amounts)
    stdev = statistics.stdev(amounts) if len(amounts) > 1 else 0.0

    # If standard deviation is very low (i.e., consistent values), check for closeness
    if stdev == 0:
        return 1.0 if transaction.amount == mean else 0.0

    # Use a normalized difference (z-score like), inverted to give a similarity score
    z = abs(transaction.amount - mean) / stdev
    score = max(0.0, 1.0 - min(z / 2, 1.0))  # Score tapers off beyond 2 stdevs

    return round(score, 2)


def get_days_since_last_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """
    Returns the number of days since this user's **previous** transaction (any merchant).
    A larger value means more “stale” activity before this one.
    """
    user_past = [
        datetime.strptime(t.date, "%Y-%m-%d").date()
        for t in all_transactions
        if t.user_id == transaction.user_id and t.date < transaction.date
    ]
    if not user_past:
        return 0  # no prior history
    last = max(user_past)
    current = datetime.strptime(transaction.date, "%Y-%m-%d").date()
    return (current - last).days


def get_normalized_recency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Normalizes days since last transaction by the user's average inter transaction interval.
    Returns 0.0 if no history, or days_since_last / avg_interval otherwise.
    Values ≫1 indicate unusually long gaps, ≪1 unusually tight.
    """
    # collect and sort all dates for this user
    dates = sorted(
        datetime.strptime(t.date, "%Y-%m-%d").date() for t in all_transactions if t.user_id == transaction.user_id
    )
    if len(dates) < 2:
        return 0.0

    # compute all inter transaction gaps
    gaps = [(b - a).days for a, b in pairwise(dates)]
    avg_gap = mean(gaps) if gaps else 0

    days_since = get_days_since_last_transaction(transaction, all_transactions)
    return days_since / avg_gap if avg_gap > 0 else 0.0


def get_transaction_recency_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Compute how recent the transaction is relative to the user's transaction history.
    Returns a value between 0.0 (very old) and 1.0 (most recent).
    """
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]

    if not user_transactions:
        return 0.0

    # Convert dates and sort
    user_transactions = sorted(user_transactions, key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))
    dates = [datetime.strptime(t.date, "%Y-%m-%d") for t in user_transactions]
    target_date = datetime.strptime(transaction.date, "%Y-%m-%d")

    earliest = dates[0]
    latest = dates[-1]

    if latest == earliest:
        return 1.0  # Only one transaction exists

    return (target_date - earliest).days / (latest - earliest).days


def get_n_transactions_last_30_days(
    transaction: Transaction, all_transactions: list[Transaction], window_days: int = 3
) -> int:
    """Count how many transactions this user made in the `window_days` before this transaction (excluding it)."""
    user_id = transaction.user_id
    cur_date = datetime.strptime(transaction.date, "%Y-%m-%d").date()
    window_start = cur_date - timedelta(days=window_days)

    return sum(
        1
        for t in all_transactions
        if t.user_id == user_id and window_start <= datetime.strptime(t.date, "%Y-%m-%d").date() < cur_date
    )


def get_ratio_transactions_last_30_days(
    transaction: Transaction, all_transactions: list[Transaction], window_days: int = 30
) -> float:
    """Fraction of all the user's transactions that happened in the `window_days` before this one."""
    user_id = transaction.user_id
    user_transactions = [t for t in all_transactions if t.user_id == user_id]

    total = len(user_transactions)
    if total == 0:
        return 0.0

    count_last_30 = get_n_transactions_last_30_days(transaction, user_transactions, window_days)
    return count_last_30 / total


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int | bool | float]:
    """Get the new features for the transaction."""
    return {
        "markovian_probability_praise": calculate_markovian_probability(transaction, all_transactions),
        "streaks_praise": calculate_streaks(transaction, all_transactions),
        #        "ewma_interval_deviation_praise": get_ewma_interval_deviation(transaction, all_transactions),
        #        "hurst_exponent_praise": get_hurst_exponent(transaction, all_transactions),
        "fourier_periodicity_score_praise": get_fourier_periodicity_score(transaction, all_transactions),
        "is_recurring_through_past_transactions_praise": is_recurring_through_past_transactions(
            transaction, all_transactions
        ),
        "get_amount_zscore_praise": get_amount_zscore(transaction, all_transactions),
        "is_amount_outlier_praise": is_amount_outlier(transaction, all_transactions),
        #       "get_stddev_amount_same_merchant_praise": get_stddev_amount_same_merchant(
        #           transaction, all_transactions
        #       ),
        "get_avg_days_between_same_merchant_praise": get_avg_days_between_same_merchant(transaction, all_transactions),
        "is_weekend_transaction_praise": is_weekend_transaction(transaction),
        "is_end_of_month_transaction_praise": is_end_of_month_transaction(transaction),
        "get_days_since_first_transaction_praise": get_days_since_first_transaction(transaction, all_transactions),
        "get_amount_coefficient_of_variation_praise": get_amount_coefficient_of_variation(
            transaction, all_transactions
        ),
        "get_unique_merchants_count_praise": get_unique_merchants_count(transaction, all_transactions),
        #    "get_amount_quantile_praise": get_amount_quantile(transaction, all_transactions),
        "is_consistent_weekday_pattern_praise": is_consistent_weekday_pattern(transaction, all_transactions),
        "get_recurrence_score_by_amount_praise": get_recurrence_score_by_amount(transaction, all_transactions),
        #    "compare_recent_to_historical_average_praise": compare_recent_to_historical_average(
        #        transaction, all_transactions
        #    ),
        #    "get_days_since_last_transaction_praise": get_days_since_last_transaction(transaction, all_transactions),
        "get_normalized_recency_praise": get_normalized_recency(transaction, all_transactions),
        #    "get_transaction_recency_score_praise": get_transaction_recency_score(transaction, all_transactions),
        "get_n_transactions_last_30_days_praise": get_n_transactions_last_30_days(transaction, all_transactions),
        #    "get_ratio_transactions_last_30_days_praise": get_ratio_transactions_last_30_days(
        # transaction, all_transactions
        # ),
    }
