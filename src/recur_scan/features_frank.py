import itertools
import re
from collections import Counter, defaultdict
from collections.abc import Sequence
from datetime import date, timedelta
from difflib import SequenceMatcher
from statistics import StatisticsError, mean, median, stdev

import numpy as np

from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date


def transactions_per_month(all_transactions: list[Transaction]) -> float:
    """Calculates the average transactions per month with consistency check."""
    if not all_transactions:
        return 0.0

    transaction_dates = sorted(parse_date(t.date) for t in all_transactions)
    min_date, max_date = transaction_dates[0], transaction_dates[-1]
    total_months = (max_date.year - min_date.year) * 12 + (max_date.month - min_date.month) + 1

    avg_per_month = len(all_transactions) / total_months if total_months > 0 else 0.0

    # Consistency Check: If most transactions fall within ±2 days of the same date each month, boost the score
    days_of_month = [date.day for date in transaction_dates]
    most_common_day = max(set(days_of_month), key=days_of_month.count)
    consistency = days_of_month.count(most_common_day) / len(days_of_month)

    return avg_per_month * consistency  # Prioritizes stable patterns


def transactions_per_week(all_transactions: list[Transaction]) -> float:
    """Calculates the average transactions per week with consistency check."""
    if not all_transactions:
        return 0.0

    transaction_dates = sorted(parse_date(t.date) for t in all_transactions)
    total_days = (transaction_dates[-1] - transaction_dates[0]).days
    total_weeks = total_days / 7 if total_days > 0 else 1

    avg_per_week = len(all_transactions) / total_weeks if total_weeks > 0 else 0.0

    # Consistency Check: If most transactions happen on the same weekday, boost the score
    weekdays = [date.weekday() for date in transaction_dates]  # 0=Monday, 6=Sunday
    most_common_weekday = max(set(weekdays), key=weekdays.count)
    consistency = weekdays.count(most_common_weekday) / len(weekdays)

    return avg_per_week * consistency  # Prioritizes transactions on a stable schedule


# 1. Recurrence Interval Variance:
def recurrence_interval_variance(all_transactions: list[Transaction]) -> float:
    """
    Returns the standard deviation (variance) of the days between consecutive transactions for the same vendor.
    A lower variance indicates a regular, recurring pattern.
    """
    if len(all_transactions) < 2:
        return 0.0

    all_transactions = sorted(all_transactions, key=lambda t: parse_date(t.date))
    intervals = [
        (parse_date(all_transactions[i].date) - parse_date(all_transactions[i - 1].date)).days
        for i in range(1, len(all_transactions))
    ]

    return stdev(intervals) if len(intervals) > 1 else 0.0


# 2. Normalized Days Difference:
def normalized_days_difference(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Computes the difference between the current transaction's days since last and the median interval,
    normalized by the standard deviation of intervals. Returns 0 if not enough data.
    """
    if len(all_transactions) < 2:
        return 0.0

    all_transactions = sorted(all_transactions, key=lambda t: parse_date(t.date))
    intervals = [
        (parse_date(all_transactions[i].date) - parse_date(all_transactions[i - 1].date)).days
        for i in range(1, len(all_transactions))
    ]

    med_interval = median(intervals)
    std_interval = stdev(intervals) if len(intervals) > 1 else 0.0
    days_since_last = (parse_date(transaction.date) - parse_date(all_transactions[-1].date)).days

    return (days_since_last - med_interval) / std_interval if std_interval != 0 else 0.0


# 6. Amount Stability Score:
def amount_stability_score(all_transactions: list[Transaction]) -> float:
    """
    Returns the ratio of the median transaction amount to its standard deviation for the vendor.
    A higher ratio indicates that amounts are stable.
    """
    amounts = [t.amount for t in all_transactions]
    if len(amounts) < 2:
        return 0.0
    med = median(amounts)
    try:
        std_amt = stdev(amounts)
    except Exception:
        std_amt = 0.0
    if std_amt == 0:
        return 1.0  # Perfect stability if no variation.
    return med / std_amt


# 7. Amount Z-Score:
def amount_z_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Computes the Z-score of the current transaction's amount relative to the vendor's historical amounts.
    """
    amounts = [t.amount for t in all_transactions]
    if len(amounts) < 2:
        return 0.0
    med = median(amounts)
    try:
        std_amt = stdev(amounts)
    except Exception:
        std_amt = 0.0
    if std_amt == 0:
        return 0.0
    return (transaction.amount - med) / std_amt


def vendor_recurrence_trend(all_transactions: list[Transaction]) -> float:
    """
    Groups a vendor's transactions by (year, month) and counts transactions per month.
    Fits a simple linear regression (using np.polyfit) to these monthly counts.
    Returns the slope as an indicator of trend.
    If there is no increase, returns 0.0 (i.e. non-negative slope).
    """
    if len(all_transactions) < 2:
        return 0.0

    all_transactions = sorted(all_transactions, key=lambda t: parse_date(t.date))

    monthly_counts: defaultdict[tuple[int, int], int] = defaultdict(int)

    for t in all_transactions:
        parsed_date = parse_date(t.date)  # Convert string date to datetime.date object
        key = (parsed_date.year, parsed_date.month)  # Extract year and month correctly
        monthly_counts[key] += 1

    keys = sorted(monthly_counts.keys(), key=lambda k: (k[0], k[1]))
    counts = [monthly_counts[k] for k in keys]

    if len(counts) < 2:
        return 0.0

    x = np.arange(len(counts))
    slope, _ = np.polyfit(x, counts, 1)

    return max(float(slope), 0.0)  # Ensure non-negative slope


def weekly_spending_cycle(all_transactions: list[Transaction]) -> float:
    """
    Measures how much transaction amounts vary on a weekly basis with a flexible 2-3 day shift.
    Groups past transactions into weeks with slight flexibility
    (e.g., Friday transactions might count for Thursday-Saturday).
    Computes the coefficient of variation (std/mean) of weekly averages.
    A lower value suggests a stable weekly spending pattern.
    """
    if not all_transactions:
        return 0.0

    weekly_amounts = defaultdict(list)

    for t in all_transactions:
        week_number = (parse_date(t.date) - timedelta(days=parse_date(t.date).weekday() % 3)).isocalendar()[1]
        # This adjusts week grouping, allowing slight shifts in weekday alignment (±2-3 days)
        weekly_amounts[week_number].append(t.amount)

    weekly_avgs = [mean(amounts) for amounts in weekly_amounts.values() if amounts]
    if len(weekly_avgs) < 2:
        return 0.0

    avg = mean(weekly_avgs)
    variation = stdev(weekly_avgs) if len(weekly_avgs) > 1 else 0.0
    return variation / avg if avg != 0 else 0.0


def seasonal_spending_cycle(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Measures how much transaction amounts vary by month for a given vendor.
    Groups past transactions by month, computes each month's average, then returns
    the coefficient of variation (std/mean) of these averages.
    A lower value suggests a stable, seasonal pattern.
    """
    vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
    if not vendor_transactions:
        return 0.0
    monthly_amounts = defaultdict(list)
    for t in vendor_transactions:
        monthly_amounts[parse_date(t.date).month].append(t.amount)
    monthly_avgs = [mean(amounts) for amounts in monthly_amounts.values() if amounts]
    if len(monthly_avgs) < 2:
        return 0.0
    avg = mean(monthly_avgs)
    variation = stdev(monthly_avgs) if len(monthly_avgs) > 1 else 0.0
    return variation / avg if avg != 0 else 0.0


def get_days_since_last_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of days since the last transaction with the same merchant"""
    same_merchant_transactions = [
        t for t in all_transactions if t.name == transaction.name and parse_date(t.date) < parse_date(transaction.date)
    ]

    if not same_merchant_transactions:
        return -1  # No previous transaction with the same merchant

    last_transaction = max(same_merchant_transactions, key=lambda t: parse_date(t.date))
    return (parse_date(transaction.date) - parse_date(last_transaction.date)).days


def get_same_amount_ratio(
    transaction: Transaction, all_transactions: list[Transaction], tolerance: float = 0.05
) -> float:
    """
    Calculate the ratio of transactions with amounts within ±tolerance of the current transaction's amount.

    Args:
        transaction: The current transaction.
        all_transactions: List of all transactions for the same vendor.
        tolerance: Allowed variation in amounts (e.g., 0.05 for ±5%).

    Returns:
        Ratio of transactions with amounts within ±tolerance of the current transaction's amount.
    """
    if not all_transactions:
        return 0.0

    # Get the current transaction's amount
    current_amount = transaction.amount

    # Calculate the range of acceptable amounts
    lower_bound = current_amount * (1 - tolerance)
    upper_bound = current_amount * (1 + tolerance)

    # Count transactions within the acceptable range
    n_similar_amounts = sum(1 for t in all_transactions if lower_bound <= t.amount <= upper_bound)

    # Calculate the ratio
    return n_similar_amounts / len(all_transactions)


def trimmed_mean(values: Sequence[float], trim_percent: float = 0.1) -> float:
    """
    Compute a trimmed mean: remove the lowest and highest trim_percent of values.
    If there aren't enough values to trim, returns the standard mean.
    """
    converted_values = [float(x) for x in values]
    n = len(converted_values)
    if n == 0:
        return 0.0
    k = int(n * trim_percent)
    trimmed_values = sorted(converted_values)[k : n - k] if n > 2 * k else converted_values
    return mean(trimmed_values)


def calculate_cycle_consistency(transactions: list[Transaction]) -> float:
    """Determines how frequently transactions align with their detected cycle."""
    if len(transactions) < 3:
        return 0.0  # Need at least 3 to check consistency

    transactions.sort(key=lambda t: parse_date(t.date))  # Ensure transactions are sorted
    dates = [parse_date(t.date) for t in transactions]
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

    if not intervals:
        return 0.0

    median_interval = median(intervals)

    # Allow for up to 25% variation in the expected cycle interval
    tolerance = 0.25 * median_interval

    consistent_count = sum(1 for interval in intervals if abs(interval - median_interval) <= tolerance)

    return consistent_count / len(intervals)


def safe_interval_consistency(all_transactions: list[Transaction]) -> float:
    """
    Compute interval consistency for a given transaction using the intervals
    from previous transactions with the same vendor.

    The consistency is computed as:
        1 - (stdev(trimmed_intervals) / mean(trimmed_intervals))
    where trimmed_intervals are the intervals after clipping at the 5th and 95th percentiles.

    Returns 0 if there are fewer than 6 intervals or if the mean of the trimmed intervals is zero.
    """

    if len(all_transactions) < 2:
        # Not enough transactions to compute intervals
        return 0.0

    # Sort the filtered transactions by date
    dates = sorted([t.date for t in all_transactions])

    # Compute intervals (in days) between consecutive transactions
    intervals = [(parse_date(dates[i]) - parse_date(dates[i - 1])).days for i in range(1, len(dates))]

    if len(intervals) <= 5:
        # Not enough intervals to compute a robust consistency measure
        return 0.0

    # Clip intervals to remove outliers (5th to 95th percentile)
    lower_bound = np.percentile(intervals, 5)
    upper_bound = np.percentile(intervals, 95)
    trimmed_intervals = np.clip(intervals, lower_bound, upper_bound)

    m: float = float(mean(trimmed_intervals))
    if m == 0:
        return 0.0

    return float(1 - (stdev(trimmed_intervals) / m))


def get_vendor_recurrence_score(all_transactions: list[Transaction], total_transactions: int) -> float:
    """Compute a general recurrence score for a vendor instead of binary flags."""
    if total_transactions == 0:
        return 0.0
    return len(all_transactions) / total_transactions  # Proportion of transactions from this vendor


def enhanced_amt_iqr(all_transactions: list[Transaction]) -> float:
    """Interquartile range of amounts, scaled to 1-10."""
    amounts = [t.amount for t in all_transactions]

    if not amounts or max(amounts) == 0:
        return 1.0

    iqr = float(np.subtract(*np.percentile(amounts, [75, 25])))  # Convert NumPy float to Python float

    return min(10.0, 1.0 + (iqr / max(amounts)) * 9)


def enhanced_days_since_last(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Dynamically determines recurrence cycles and scores transactions based on how well they fit."""

    from statistics import mean

    previous_dates = sorted([
        parse_date(t.date) for t in all_transactions if t.id != transaction.id and t.name == transaction.name
    ])

    if not previous_dates:
        return 1.0  # No previous transactions → lowest score

    # Calculate the average gap between transactions
    intervals = [(previous_dates[i] - previous_dates[i - 1]).days for i in range(1, len(previous_dates))]

    if not intervals:
        return 1.0  # Only one previous transaction → lowest score

    avg_interval = mean(intervals)  # Average time gap between transactions
    days_since = (parse_date(transaction.date) - previous_dates[-1]).days

    # Score based on how closely it matches the expected recurrence interval
    similarity_score = max(1.0, 10.0 - (abs(days_since - avg_interval) / max(avg_interval, 1)) * 9)

    return round(similarity_score, 2)  # Round for stability


def enhanced_n_similar_last_n_days(
    transaction: Transaction, all_transactions: list[Transaction], days: int = 90
) -> float:
    """Counts similar transactions within a given time window, scaled from 1 to 10."""

    similar_transactions = [
        t
        for t in all_transactions
        if abs(parse_date(t.date) - parse_date(transaction.date)).days <= days
        and abs(t.amount - transaction.amount) / max(transaction.amount, 1) <= 0.051  # Slightly increased tolerance
    ]

    count = len(similar_transactions)
    return min(10.0, count)  # Cap at 10


# Define common subscription cycles (allowing ±3 days flexibility)
COMMON_CYCLES = [7, 14, 30, 90, 365]
CYCLE_RANGE = 3  # Allowed variation in cycle detection


def detect_common_interval(intervals: list[int]) -> bool:
    """
    Checks if the transaction intervals match common subscription cycles (with flexibility).
    """
    return any(any(abs(interval - cycle) <= CYCLE_RANGE for interval in intervals) for cycle in COMMON_CYCLES)


def transaction_frequency(transactions: list[Transaction]) -> float:
    """Returns transaction frequency per month."""
    if len(transactions) < 2:
        return 0.0

    dates = sorted([parse_date(t.date) for t in transactions])
    total_days = (dates[-1] - dates[0]).days
    months = max(total_days / 30, 1)
    return float(len(transactions) / months)


def robust_interval_median(transactions: list[Transaction]) -> float:
    """Returns the median interval between transactions."""
    if len(transactions) < 2:
        return 0.0

    dates = sorted([parse_date(t.date) for t in transactions])
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    return float(median(intervals)) if intervals else 0.0


def robust_interval_iqr(transactions: list[Transaction]) -> float:
    """Returns the interquartile range (IQR) of transaction intervals."""
    if len(transactions) < 2:
        return 0.0

    dates = sorted([parse_date(t.date) for t in transactions])
    intervals = sorted([(dates[i] - dates[i - 1]).days for i in range(1, len(dates))])

    if len(intervals) > 1:
        return float(np.percentile(intervals, 75, method="midpoint") - np.percentile(intervals, 25, method="midpoint"))
    return 0.0


def amount_variability_ratio(transactions: list[Transaction]) -> float:
    """Returns the variability ratio of transaction amounts."""
    if len(transactions) < 2:
        return 0.0

    amounts = [t.amount for t in transactions]
    median_amount = median(amounts)

    if len(amounts) > 1:
        iqr_amounts = float(
            np.percentile(amounts, 75, method="midpoint") - np.percentile(amounts, 25, method="midpoint")
        )
        return iqr_amounts / median_amount if median_amount > 0 else 0.0
    return 0.0


def most_common_interval(transactions: list[Transaction]) -> float:
    """Returns the most common interval between transactions."""
    if len(transactions) < 2:
        return 0.0

    dates = sorted([parse_date(t.date) for t in transactions])
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

    if intervals:
        counter = Counter(intervals)
        return float(counter.most_common(1)[0][0])  # Get the most frequent interval
    return 0.0


def matches_common_cycle(transactions: list[Transaction]) -> float:
    """Returns 1 if transactions match a common cycle, otherwise 0."""
    if len(transactions) < 2:
        return 0.0

    dates = sorted([parse_date(t.date) for t in transactions])
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

    return 1.0 if detect_common_interval(intervals) else 0.0


def recurring_confidence(transactions: list[Transaction]) -> float:
    """Returns confidence score (0-1) for transactions being recurring."""
    if not transactions:
        return 0.0

    company_names = [t.name for t in transactions]
    confidence = 0.0

    for name in company_names:
        utility_score = is_utility_company(name)
        recurrence_score = recurring_score(name)

        confidence = max(confidence, recurrence_score, utility_score)

    return float(confidence)


def coefficient_of_variation_intervals(transactions: list[Transaction]) -> float:
    """Returns the coefficient of variation of transaction intervals."""
    median_interval = robust_interval_median(transactions)
    iqr = robust_interval_iqr(transactions)

    return iqr / median_interval if median_interval > 0 else 0.0


# Predefined lists of known recurring companies and keywords
KNOWN_RECURRING_COMPANIES = {
    "netflix",
    "spotify",
    "amazon prime",
    "hulu",
    "disney+",
    "youtube",
    "adobe",
    "microsoft",
    "verizon",
    "at&t",
    "t-mobile",
    "comcast",
    "spectrum",
    "onlyfans",
    "albert",
    "ipsy",
    "experian",
    "walmart+",
    "sirius xm",
    "pandora",
    "sezzle",
    "apple",
    "amazon+",
    "BET+",
    "HBO",
    "Credit Genie",
    "amazon kids+",
    "paramount+",
    "afterpay",
    "cricut",
}

UTILITY_KEYWORDS = {
    "energy",
    "power",
    "electric",
    "utility",
    "gas",
    "water",
    "sewer",
    "trash",
    "internet",
    "phone",
    "cable",
    "wifi",
    "broadband",
    "telecom",
    "member",
    "fitness",
    "gym",
    "insurance",
    "rent",
    "hoa",
    "subscription",
    "mobile",
    "pay",
    "light",
    "tv",
}

# Precompile regex patterns for performance
RECURRING_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(keyword) for keyword in KNOWN_RECURRING_COMPANIES) + r")\b", re.IGNORECASE
)

UTILITY_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(keyword) for keyword in UTILITY_KEYWORDS) + r")\b", re.IGNORECASE
)


def clean_company_name(name: str) -> str:
    """Normalize company name for better matching."""
    return re.sub(r"[^a-zA-Z0-9\s]", "", name).strip().lower()


def is_utility_company(company_name: str) -> int:
    """Returns 1 if the company is a utility provider, else 0."""
    cleaned_name = clean_company_name(company_name)
    return 1 if UTILITY_PATTERN.search(cleaned_name) else 0


def is_recurring_company(company_name: str) -> int:
    """Returns 1 if the company is known for recurring payments, else 0."""
    cleaned_name = clean_company_name(company_name)
    return 1 if RECURRING_PATTERN.search(cleaned_name) else 0


def recurring_score(company_name: str) -> float:
    """
    Returns a confidence score (0 to 1) based on keyword matches indicating
    whether a company is likely offering recurring payments.
    """
    cleaned_name = clean_company_name(company_name)

    if RECURRING_PATTERN.search(cleaned_name):
        return 1.0
    if UTILITY_PATTERN.search(cleaned_name):
        return 0.8  # Utilities are highly likely to be recurring

    # Check for partial matches with known recurring companies
    for keyword in KNOWN_RECURRING_COMPANIES:
        if keyword in cleaned_name:
            return 0.7  # Partial match confidence

    return 0.0


def get_subscription_score(all_transactions: list[Transaction]) -> float:
    """Improved subscription detection with vendor similarity and gradual amount changes."""
    if len(all_transactions) < 2:
        return 0.0

    # Sort transactions by date
    all_transactions.sort(key=lambda t: parse_date(t.date))
    dates = [t.date for t in all_transactions]
    amounts = [t.amount for t in all_transactions]
    vendors = [t.name for t in all_transactions]  # Vendor names

    # Compute intervals (days)
    intervals = [(parse_date(dates[i]) - parse_date(dates[i - 1])).days for i in range(1, len(dates))]
    if not intervals:
        return 0.0

    median_interval = float(median(intervals))

    # Subscription cycles with ±3-day tolerance
    base_cycles = [7, 14, 30, 90, 365]
    cycle_ranges = {cycle: (cycle - 3, cycle + 3) for cycle in base_cycles}

    # Find the closest cycle
    detected_cycle = min(
        base_cycles,
        key=lambda c: abs(median_interval - c)
        if cycle_ranges[c][0] <= median_interval <= cycle_ranges[c][1]
        else float("inf"),
    )

    # Interval consistency (adaptive threshold)
    interval_threshold = 0.15 * detected_cycle
    interval_consistency = sum(
        1 for interval in intervals if abs(interval - median_interval) <= interval_threshold
    ) / len(intervals)

    # Amount consistency (adaptive threshold with rolling deviation)
    median_amount = median(amounts)
    std_dev = float(np.std(amounts))  # ✅ Convert np.float64 to Python float
    threshold = max(0.15 * median_amount, std_dev * 0.5)
    amount_consistency = sum(1 for amount in amounts if abs(amount - median_amount) <= threshold) / len(amounts)

    # Vendor similarity (if same vendor is used consistently)
    unique_vendors = len(set(vendors))
    vendor_consistency = 1.0 if unique_vendors == 1 else max(0.2, 1.0 - (unique_vendors / len(vendors)))

    # Final subscription score (weighted combination)
    subscription_score = (interval_consistency * 0.4) + (amount_consistency * 0.4) + (vendor_consistency * 0.2)

    return min(1.0, subscription_score)  # Ensure score is between 0 and 1


def get_amount_consistency(all_transactions: list[Transaction]) -> float:
    """Detects how consistent transaction amounts are over time."""
    amounts = [t.amount for t in all_transactions]
    if len(amounts) < 2:
        return 0.0

    median_amount = median(amounts)
    std_dev = float(np.std(amounts))  # Explicit conversion
    threshold = max(0.15 * median_amount, std_dev * 0.5)

    amount_consistency = sum(1 for amount in amounts if abs(amount - median_amount) <= threshold) / len(amounts)

    return min(1.0, amount_consistency)


def irregular_interval_score(all_transactions: list[Transaction]) -> float:
    """Computes how irregular the intervals between transactions are (0 to 1)."""
    if not all_transactions or len(all_transactions) < 2:
        return 0.0

    sorted_transactions = sorted(all_transactions, key=lambda t: t.date)
    dates = [parse_date(t.date) for t in sorted_transactions]
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

    if len(intervals) > 1:
        interval_std = stdev(intervals)
        mean_interval = sum(intervals) / len(intervals)
        return min(interval_std / (mean_interval + 1e-8), 1.0)
    return 0.0


def inconsistent_amount_score(all_transactions: list[Transaction]) -> float:
    """Computes how inconsistent the transaction amounts are (0 to 1)."""
    if not all_transactions or len(all_transactions) < 2:
        return 0.0

    amounts = [t.amount for t in all_transactions]

    if len(amounts) > 1:
        amount_std = stdev(amounts)
        mean_amount = sum(amounts) / len(amounts)
        return min(amount_std / (mean_amount + 1e-8), 1.0)
    return 0.0


def non_recurring_score(all_transactions: list[Transaction]) -> float:
    """
    Determines the probability of transactions being non-recurring (0 to 1).
    """
    interval_score = irregular_interval_score(all_transactions)
    amount_score = inconsistent_amount_score(all_transactions)

    if interval_score > 0.7 and amount_score > 0.7:
        return 1.0  # Highly non-recurring
    elif interval_score > 0.4 or amount_score > 0.4:
        return 0.7  # Moderately non-recurring
    return 0.0  # Recurring


def amount_variability_score(all_transactions: list[Transaction]) -> float:
    """Scores how much transaction amounts vary (1-10)."""
    if len(all_transactions) < 2:
        return 1.0  # Single transactions are inherently non-recurring

    unique_amounts = len({t.amount for t in all_transactions})
    ratio = unique_amounts / len(all_transactions)

    return min(10.0, ratio * 10)  # Scale to 1-10


def date_irregularity_score(all_transactions: list[Transaction]) -> float:
    """Scores how irregular the transaction dates are (1-10)."""
    if len(all_transactions) < 2:
        return 1.0  # Single transactions = non-recurring

    months = [parse_date(t.date).month for t in all_transactions]
    try:
        date_std = stdev(months) if len(months) >= 2 else 0
    except StatisticsError:
        date_std = 0

    return min(10.0, (date_std / 2) * 10)  # Scale to 1-10, assuming >2 std dev is max irregularity


# Helper: Calculate days between dates in a transaction list
def _get_intervals(transactions: list[Transaction]) -> list[int]:
    """Extract intervals between transaction dates."""
    sorted_dates = sorted([t.date for t in transactions])  # No need to parse
    return [(parse_date(sorted_dates[i]) - parse_date(sorted_dates[i - 1])).days for i in range(1, len(sorted_dates))]


def proportional_timing_deviation(
    transaction: Transaction, transactions: list[Transaction], days_flexibility: int = 7
) -> float:
    """Measures deviation from historical median interval, allowing a flexible timing window."""

    if len(transactions) < 2:
        return 0.0  # Not enough data to determine deviation

    intervals = _get_intervals(transactions)

    if not intervals or all(i == 0 for i in intervals):
        return 0.0  # Avoid division by zero when all intervals are zero

    median_interval: float = float(median(intervals))
    current_interval: int = (parse_date(transaction.date) - parse_date(transactions[-1].date)).days

    # Allow a ±7 day window for delay flexibility
    if abs(current_interval - median_interval) <= days_flexibility:
        return 1.0  # Fully consistent if within range

    return max(
        0.0, 1 - (abs(current_interval - max(median_interval, 1)) / max(median_interval, 1))
    )  # Ensure result is non-negative


def amount_similarity(transaction: Transaction, transactions: list[Transaction], tolerance: float = 0.05) -> float:
    """
    Calculate the ratio of transactions with amounts within ±tolerance of the current transaction's amount.
    """
    if not transactions:
        return 0.0
    current_amount = transaction.amount
    lower_bound = current_amount * (1 - tolerance)
    upper_bound = current_amount * (1 + tolerance)
    similar_count = sum(1 for t in transactions if lower_bound <= t.amount <= upper_bound)
    return float(similar_count) / float(len(transactions))


def amount_coefficient_of_variation(transactions: list[Transaction]) -> float:
    """
    Measures amount consistency using the population standard deviation.
    Returns (population stdev / mean). If not enough data, returns 0.0.
    """
    amounts = [t.amount for t in transactions]
    if len(amounts) < 2 or mean(amounts) == 0:
        return 0.0
    # Use population std (ddof=0) to match test expectations.
    pop_std = np.std(amounts, ddof=0)
    return float(pop_std / mean(amounts))


def detect_variable_subscription(all_transactions: list[Transaction]) -> float:
    """
    Detect if this might be a variable subscription (amount varies but follows a pattern).
    Returns a confidence score between 0 and 1.
    """
    if len(all_transactions) < 3:
        return 0.0

    amounts = [t.amount for t in all_transactions]

    # Calculate percentage changes between consecutive amounts
    pct_changes = []
    for i in range(len(amounts) - 1):
        if amounts[i] != 0:
            pct_change = abs((amounts[i + 1] - amounts[i]) / amounts[i])
            pct_changes.append(pct_change)

    if not pct_changes:
        return 0.0

    # If changes are relatively consistent and small, likely a variable subscription
    avg_change = np.mean(pct_changes)
    std_change = np.std(pct_changes)

    # Score based on stability of changes
    if avg_change > 0.5:  # Too much variation
        return 0.0

    stability_score = 1.0 - min(float(std_change / avg_change) if avg_change > 0 else 1.0, 1.0)
    return float(stability_score)


def is_business_day_aligned(all_transactions: list[Transaction], holidays: list[date] | None = None) -> float:
    if holidays is None:
        holidays = []
    business_days = 0
    total_days = 0

    for t in all_transactions:
        txn_date = parse_date(t.date)
        if txn_date and txn_date.weekday() < 5 and txn_date not in holidays:  # Skip holidays
            business_days += 1
        total_days += 1

    return float(business_days / total_days) if total_days > 0 else 0.0


def detect_multi_tier_subscription(all_transactions: list[Transaction]) -> float:
    """
    Detect if transactions alternate between different fixed amounts,
    indicating a multi-tier subscription pattern.
    Returns a confidence score between 0 and 1.
    """
    if len(all_transactions) < 4:
        return 0.0

    # Group amounts and count occurrences
    amount_counts: defaultdict = defaultdict(int)
    for t in all_transactions:
        amount_counts[round(t.amount, 2)] += 1

    # Look for multiple recurring amounts
    recurring_amounts = [amt for amt, count in amount_counts.items() if count >= 2]

    if len(recurring_amounts) < 2:
        return 0.0

    # Extract and sort transaction amounts
    amounts = [round(t.amount, 2) for t in sorted(all_transactions, key=lambda x: parse_date(x.date))]

    # Initialize pattern score
    pattern_score = 0

    # Look for alternating patterns (e.g., 5.00, 10.00, 5.00)
    for i in range(len(amounts) - 2):
        if amounts[i] == amounts[i + 2] and amounts[i] in recurring_amounts:
            pattern_score += 1

    # Return normalized pattern score (between 0 and 1)
    return min(1.0, pattern_score / (len(amounts) - 2))


def detect_annual_price_adjustment(all_transactions: list[Transaction]) -> float:
    """
    Detect if there are consistent annual price increases, typical of subscription services.
    """
    if len(all_transactions) < 2:
        return 0.0

    # Sort transactions by date
    sorted_transactions = sorted(all_transactions, key=lambda x: parse_date(x.date))
    amounts = [t.amount for t in sorted_transactions]

    # Calculate year-over-year changes
    yearly_changes = []
    for i in range(len(amounts) - 1):
        if amounts[i] > 0:
            pct_change = (amounts[i + 1] - amounts[i]) / amounts[i]
            if 0 < pct_change < 0.5:  # Allow wider range
                yearly_changes.append(pct_change)

    if not yearly_changes:
        return 0.0

    # Score based on consistency
    avg_change = np.mean(yearly_changes)
    std_change = np.std(yearly_changes)

    consistency_score = 1.0 - min(float(std_change / avg_change) if avg_change > 0 else 1.0, 1.0)
    return float(consistency_score)


def detect_pay_period_alignment(all_transactions: list[Transaction]) -> float:
    """
    Detect if transactions align with common pay periods (bi-weekly, monthly).
    """
    if len(all_transactions) < 2:
        return 0.0

    sorted_transactions = sorted(all_transactions, key=lambda x: parse_date(x.date))
    dates = [parse_date(t.date) for t in sorted_transactions if parse_date(t.date)]

    if len(dates) < 2:
        return 0.0

    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

    if not intervals:
        return 0.0

    biweekly_matches = sum(1 for i in intervals if 12 <= i <= 16)
    monthly_matches = sum(1 for i in intervals if 28 <= i <= 32)

    biweekly_score = biweekly_matches / len(intervals)
    monthly_score = monthly_matches / len(intervals)

    return float(max(biweekly_score, monthly_score))


def is_earnin_tip_subscription(transactions: list[Transaction]) -> float:
    """
    Detects Earnin tip subscriptions based on low, recurring amounts and consistent frequency (e.g., bi-weekly).
    """
    if not transactions or not all("earnin" in t.name.lower() for t in transactions):
        return 0.0

    amounts = [t.amount for t in transactions]
    low_amounts = [a for a in amounts if 1.0 <= a <= 10.0]  # Low range of amounts

    if len(low_amounts) < len(amounts) * 0.7:  # At least 70% of payments must be low
        return 0.0

    dates = [parse_date(t.date) for t in transactions]
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

    consistent_frequency = sum(14 <= interval <= 30 for interval in intervals) / len(intervals)

    if consistent_frequency >= 0.7:  # At least 70% consistency in frequency
        return 1.0
    return 0.0


def is_amazon_prime_like_subscription(transactions: list[Transaction]) -> float:
    """Detect recurring patterns specific to Amazon Prime, Audible, or Amazon Music subscriptions."""
    if not transactions or not any("amazon" in t.name.lower() for t in transactions):
        return 0.0

    # Filter names for likely Prime-related descriptions
    prime_related = [
        t for t in transactions if any(keyword in t.name.lower() for keyword in ["prime", "video", "audible", "music"])
    ]
    if len(prime_related) < 2:
        return 0.0

    amounts = [t.amount for t in prime_related]
    dates = [parse_date(t.date) for t in prime_related]

    median_amt = median(amounts)
    if median_amt < 3 or median_amt > 20:
        return 0.0  # Out of expected range

    # Look for monthly patterns (27-33 day interval)
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    if not intervals:
        return 0.0
    monthly_pattern = sum(1 for d in intervals if 27 <= d <= 33) / len(intervals)

    amount_consistency = sum(1 for amt in amounts if abs(amt - median_amt) <= 1.5) / len(amounts)

    # Weighted confidence score
    return 0.6 * monthly_pattern + 0.4 * amount_consistency


def is_amazon_retail_irregular(transactions: list[Transaction]) -> float:
    """Detect irregular retail purchases from Amazon store with high amount variance."""
    if not transactions or not any("amazon" in t.name.lower() for t in transactions):
        return 0.0

    # Skip obvious subscription names
    if any(keyword in t.name.lower() for t in transactions for keyword in ["prime", "audible", "video", "music"]):
        return 0.0

    amounts = [t.amount for t in transactions]
    if len(amounts) < 2:
        return 0.0

    std_dev = np.std(amounts)
    if std_dev > 20:  # High deviation in retail behavior
        return 1.0
    return 0.0


def is_apple_subscription_like(transactions: list[Transaction]) -> float:
    """
    Detects Apple service charges that resemble recurring payments
    based on amount consistency and monthly timing.
    """
    if not transactions or not any("apple" in t.name.lower() for t in transactions):
        return 0.0

    apple_txns = [t for t in transactions if "apple" in t.name.lower()]
    if len(apple_txns) < 2:
        return 0.0

    amounts = [t.amount for t in apple_txns]
    dates = [parse_date(t.date) for t in apple_txns]
    median_amt = median(amounts)

    if median_amt < 1 or median_amt > 50:
        return 0.0

    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    if not intervals:
        return 0.0

    monthly_pattern_score = sum(1 for d in intervals if 27 <= d <= 33) / len(intervals)
    amount_consistency_score = sum(1 for amt in amounts if abs(amt - median_amt) <= 1.5) / len(amounts)

    return 0.6 * monthly_pattern_score + 0.4 * amount_consistency_score


def is_apple_irregular_purchase(transactions: list[Transaction]) -> float:
    """
    Detect irregular purchase behavior for Apple purchases.
    """
    if not transactions or not any("apple" in t.name.lower() for t in transactions):
        return 0.0

    amounts = [t.amount for t in transactions]
    dates = [parse_date(t.date) for t in transactions if parse_date(t.date)]

    if not amounts or not dates:
        return 0.0

    amount_std = np.std(amounts)
    interval_days = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    interval_std = float(np.std(interval_days)) if interval_days else 0.0

    if amount_std > 5.0 or interval_std > 5.0:
        return 1.0

    return 0.0


def is_cleo_ai_cash_advance_like(transactions: list[Transaction]) -> float:
    """Detect irregular, one-time cash advances or repayments from Cleo AI."""
    cleo_ai_txns = [t for t in transactions if "cleo ai" in t.name.lower()]
    if len(cleo_ai_txns) < 2:
        return 0.0

    amounts = [t.amount for t in cleo_ai_txns]
    std_dev = np.std(amounts)
    if std_dev > 5 and max(amounts) > 10:
        return 1.0
    return 0.0


def is_brigit_subscription_like(transactions: list[Transaction]) -> float:
    if not transactions or not any("brigit" in t.name.lower() for t in transactions):
        return 0.0

    subscription_txns = [t for t in transactions if 8.0 <= t.amount <= 15.5 and round(t.amount % 1, 2) == 0.99]

    if len(subscription_txns) < 2:
        return 0.0

    subscription_txns.sort(key=lambda t: parse_date(t.date))
    intervals = [
        (parse_date(subscription_txns[i].date) - parse_date(subscription_txns[i - 1].date)).days
        for i in range(1, len(subscription_txns))
    ]

    monthly_pattern = sum(1 for d in intervals if 27 <= d <= 33) / len(intervals)
    return min(1.0, 0.6 * monthly_pattern + 0.4 * len(subscription_txns) / len(transactions))


def is_brigit_repayment_like(transactions: list[Transaction]) -> float:
    """Detects Brigit cash advance repayments — irregular in amount and date."""
    repayments = [t for t in transactions if "brigit" in t.name.lower() and not str(t.amount).endswith("0.99")]

    if len(repayments) < 2:
        return 0.0

    amounts = [t.amount for t in repayments]
    dates = [parse_date(t.date) for t in repayments]
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

    std_dev_amt = float(np.std(amounts))
    variability_score = std_dev_amt / (np.mean(amounts) + 1e-5)
    irregular_timing = sum(1 for d in intervals if d > 10 or d < 5) / len(intervals) if intervals else 0.0
    return min(1.0, 0.5 * float(variability_score) + 0.5 * float(irregular_timing))


def is_always_recurring_vendor(transactions: list[Transaction]) -> float:
    """
    Marks known fixed recurring vendors as recurring (e.g., Sprint, Waterford Grove, RightNow)
    regardless of amount or interval consistency.
    """
    always_recurring_vendors = {"sprint", "waterford grove", "rightnow", "bet", "sezzle", "american water works"}

    for t in transactions:
        name = t.name.lower()
        if any(vendor in name for vendor in always_recurring_vendors):
            return 1.0

    return 0.0


def is_utilities_or_insurance_like(transactions: list[Transaction]) -> float:
    """
    Detects recurring payments for utilities, telecom, insurance —
    even with inconsistent dates and amounts.
    """
    if len(transactions) < 3:
        return 0.0

    vendor_name = transactions[0].name.lower()
    utility_keywords = [
        "insurance",
        "telecom",
        "electric",
        "utility",
        "power",
        "gas",
        "water",
        "mtn",
        "glo",
        "airtel",
        "sprint",
        "at&t",
        "verizon",
        "rent",
        "lease",
        "housing",
        "mortgage",
        "trash",
        "rightnow",
        "waterford grove",
    ]

    if not any(keyword in vendor_name for keyword in utility_keywords):
        return 0.0

    # Sort by date
    transactions.sort(key=lambda t: parse_date(t.date))
    dates = [parse_date(t.date) for t in transactions]
    amounts = [t.amount for t in transactions]

    # Check for soft recurring interval: 20 to 40 days
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    soft_interval_count = sum(1 for i in intervals if 20 <= i <= 40)
    interval_score = soft_interval_count / len(intervals) if intervals else 0.0

    # Check if amounts are loosely consistent (e.g., 25% tolerance from median)
    median_amt = median(amounts)
    tolerance = 0.25 * median_amt
    amount_score = sum(1 for amt in amounts if abs(amt - median_amt) <= tolerance) / len(amounts)

    # Overall score weighted more on recurrence, not consistency
    return min(1.0, 0.5 * interval_score + 0.3 * amount_score + 0.2)


def fixed_amount_fuzzy_interval_subscription(transactions: list[Transaction]) -> float:
    """
    Detects subscriptions with fixed recurring amounts but inconsistent time intervals.
    Useful for Cleo AI, Grammarly, Canva, etc.
    """
    if len(transactions) < 3:
        return 0.0

    vendor_name = transactions[0].name.lower()
    fuzzy_fixed_subs = {"cleo ai", "cleo"}

    if not any(v in vendor_name for v in fuzzy_fixed_subs):
        return 0.0

    amounts = [t.amount for t in transactions]
    median_amt = median(amounts)
    tolerance = 0.10 * median_amt  # tighter than utilities

    # Check how many are within tight tolerance of median
    fixed_amount_count = sum(1 for a in amounts if abs(a - median_amt) <= tolerance)
    amount_consistency = fixed_amount_count / len(amounts)

    # If >= 70% of charges are nearly identical, call it a fixed-amount sub
    return 1.0 if amount_consistency >= 0.7 else 0.0


def detect_vendor_name_variations(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Detects if the same vendor appears with different name variations (e.g., Credit Ninja vs Creditninja).
    Returns a similarity score between 0 and 1.
    """
    current_vendor = re.sub(r"[^a-zA-Z0-9]", "", transaction.name.lower())

    # Get all unique vendor names
    all_vendors = {re.sub(r"[^a-zA-Z0-9]", "", t.name.lower()) for t in all_transactions}

    # Find the most similar vendor name
    max_similarity = max(
        (SequenceMatcher(None, current_vendor, vendor).ratio() for vendor in all_vendors if vendor != current_vendor),
        default=0.0,
    )

    return max_similarity


def payment_schedule_change_detector(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Detects if there's been a change in payment schedule (e.g., from bi-weekly to weekly).
    Returns a score indicating the likelihood of a schedule change.
    """
    if len(all_transactions) < 4:  # Need enough history
        return 0.0

    # Sort transactions by date
    sorted_txns = sorted([t for t in all_transactions if t.name == transaction.name], key=lambda x: parse_date(x.date))

    if len(sorted_txns) < 4:
        return 0.0

    # Calculate intervals between consecutive payments
    intervals = [
        (parse_date(sorted_txns[i].date) - parse_date(sorted_txns[i - 1].date)).days for i in range(1, len(sorted_txns))
    ]

    # Look at the last 3 intervals vs previous intervals
    recent_intervals = intervals[-3:]
    historical_intervals = intervals[:-3]

    if not historical_intervals:
        return 0.0

    # Calculate the difference between recent and historical median intervals
    historical_median = median(historical_intervals)
    recent_median = median(recent_intervals)

    # Normalize the difference
    max_interval = max(historical_median, recent_median)
    if max_interval == 0:
        return 0.0

    return abs(historical_median - recent_median) / max_interval


def amount_progression_pattern(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Detects if there's a pattern in how payment amounts change over time
    (e.g., gradual increase/decrease or sudden changes).
    """
    if len(all_transactions) < 3:
        return 0.0

    # Get transactions for the same vendor
    vendor_txns = sorted([t for t in all_transactions if t.name == transaction.name], key=lambda x: parse_date(x.date))

    if len(vendor_txns) < 3:
        return 0.0

    # Calculate percentage changes between consecutive amounts
    changes = [
        (t2.amount - t1.amount) / t1.amount if t1.amount != 0 else 0 for t1, t2 in itertools.pairwise(vendor_txns)
    ]

    try:
        # Calculate the consistency of these changes
        change_std = stdev(changes)
        return 1.0 / (1.0 + change_std)  # Normalize to [0,1]
    except StatisticsError:
        return 0.0


def vendor_reliability_score(transactions: list[Transaction]) -> float:
    """
    Scores how reliable a vendor's recurring behavior is, based on:
    - Transaction frequency (density)
    - Amount consistency
    - Interval consistency
    """
    if len(transactions) < 3:
        return 0.0

    # Sort by date
    transactions.sort(key=lambda t: parse_date(t.date))
    dates = [parse_date(t.date) for t in transactions]
    amounts = [t.amount for t in transactions]

    days_span = (dates[-1] - dates[0]).days
    if days_span < 1:
        return 0.0

    # Transactions per month (density)
    txns_per_month = len(transactions) / (days_span / 30)
    tx_density_score = min(txns_per_month / 5, 1.0)  # Cap at 5/month

    # Amount consistency (lower std = higher score)
    amount_std = np.std(amounts)
    amount_mean = np.mean(amounts)
    amount_consistency = 1.0 / (1.0 + amount_std / (amount_mean + 1e-6))

    # Interval consistency (in days)
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    if not intervals:
        return 0.0
    interval_std = np.std(intervals)
    interval_mean = np.mean(intervals)
    interval_consistency = 1.0 / (1.0 + interval_std / (interval_mean + 1e-6))

    # Combine scores with weights
    return float(0.4 * tx_density_score + 0.3 * amount_consistency + 0.3 * interval_consistency)


def _detect_seasonality(intervals: list[int]) -> float:
    """
    Detects whether transaction intervals align with common recurring cycles.
    Returns a confidence score between 0.0 and 1.0 based on how well intervals match:
    - Weekly (7 ±1)
    - Biweekly (14 ±2)
    - Monthly (30 ±3)
    """
    if not intervals:
        return 0.0

    recurring_bands = {"weekly": (7, 1), "biweekly": (14, 2), "monthly": (30, 3)}

    match_count = 0
    for interval in intervals:
        for _, (target, tolerance) in recurring_bands.items():
            if abs(interval - target) <= tolerance:
                match_count += 1
                break  # Stop once matched

    return match_count / len(intervals)


def temporal_pattern_stability_score(transactions: list[Transaction]) -> float:
    """
    Measures consistency and predictability in transaction timing using:
    - Overall interval regularity
    - Recent (last 3 months) stability
    - Seasonality detection
    """
    if len(transactions) < 3:
        return 0.0

    # Sort by date
    dates = sorted([parse_date(t.date) for t in transactions])
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    if not intervals:
        return 0.0

    # Temporal regularity (across all intervals)
    mean_interval = np.mean(intervals)
    std_interval = np.std(intervals)
    temporal_score = 1.0 / (1.0 + std_interval / (mean_interval + 1e-6))

    # Rolling pattern in recent activity (last 90 days)
    recent_intervals = [i for i in intervals if i <= 90]
    rolling_score = (
        1.0 / (1.0 + np.std(recent_intervals) / (np.mean(recent_intervals) + 1e-6)) if recent_intervals else 0.0
    )

    # Seasonality (e.g., ~30-day or ~7-day cycles)
    seasonal_score = _detect_seasonality(intervals)

    # Combine scores with tuned weights
    return float(0.4 * temporal_score + 0.3 * rolling_score + 0.3 * seasonal_score)


def is_non_recurring(transactions: list[Transaction]) -> float:
    # Too few transactions = likely not recurring
    if len(transactions) < 2:
        return 1.0

    transactions.sort(key=lambda t: parse_date(t.date))
    dates = [parse_date(t.date) for t in transactions]
    amounts = [t.amount for t in transactions]

    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    avg_amount = mean(amounts)

    irregular_intervals = sum(1 for i in intervals if i < 7 or i > 35) / len(intervals)
    high_amount_variation = sum(1 for amt in amounts if abs(amt - avg_amount) / avg_amount > 0.2) / len(amounts)

    # If both interval and amount are irregular, return 1.0 (non-recurring)
    return round((irregular_intervals + high_amount_variation) / 2, 2)


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int | bool | float]:
    """Get the new features for the transaction."""

    # NOTE: Do NOT add features that are already in the original features.py file.
    # NOTE: Each feature should be on a separate line. Do not use **dict shorthand.
    return {
        # 3
        "is_non_recurring": is_non_recurring(all_transactions),
        # "is_afterpay_installment": is_afterpay_installments(all_transactions),
        # "is_brigit_non_recurring_payment": is_brigit_non_recurring_payment(all_transactions),
        "temporal_pattern_stability_score": temporal_pattern_stability_score(all_transactions),
        # "amount_stability_cluster_score": amount_stability_cluster_score(all_transactions),
        "vendor_reliability_score": vendor_reliability_score(all_transactions),
        "amount_progression_pattern": amount_progression_pattern(transaction, all_transactions),
        "payment_schedule_change_detector": payment_schedule_change_detector(transaction, all_transactions),
        # "detect_parallel_loans": detect_parallel_loans(transaction, all_transactions),
        "detect_vendor_name_variations": detect_vendor_name_variations(transaction, all_transactions),
        # ... existing features ...
        # 1
        "detect_variable_subscription": detect_variable_subscription(all_transactions),
        "is_business_day_aligned": is_business_day_aligned(all_transactions),
        "detect_multi_tier_subscription": detect_multi_tier_subscription(all_transactions),
        "detect_annual_price_adjustment": detect_annual_price_adjustment(all_transactions),
        "detect_pay_period_alignment": detect_pay_period_alignment(all_transactions),
        # 2
        # "is_albert_irregular_purchase": is_albert_irregular_purchase(all_transactions),
        # "is_brigit_recurring_payment": is_brigit_recurring_payment(all_transactions),
        "is_earnin_tip_subscription": is_earnin_tip_subscription(all_transactions),
        "is_cleo_ai_cash_advance_like": is_cleo_ai_cash_advance_like(all_transactions),
        "is_apple_irregular_purchase": is_apple_irregular_purchase(all_transactions),
        "is_apple_subscription_like": is_apple_subscription_like(all_transactions),
        "is_amazon_prime_like_subscription": is_amazon_prime_like_subscription(all_transactions),
        "is_amazon_retail_irregular": is_amazon_retail_irregular(all_transactions),
        "fixed_amount_fuzzy_interval_subscription": fixed_amount_fuzzy_interval_subscription(all_transactions),
        "is_utilities_or_insurance_like": is_utilities_or_insurance_like(all_transactions),
        "is_always_recurring_vendor": is_always_recurring_vendor(all_transactions),
        "is_brigit_repayment_like": is_brigit_repayment_like(all_transactions),
        "is_brigit_subscription_like": is_brigit_subscription_like(all_transactions),
    }


# def dominant_amount_pattern_score(transactions: list[Transaction]) -> float:
#     """
#     Detects recurring patterns based on a combination of:
#     - Consistent cents endings (e.g., .99, .88, .95)
#     - Dollar amounts within a narrow range (tight clustering)

#     This is especially useful for services like Amazon, Apple, FloatMe, where amounts are inconsistent
#     but hover around specific dollar+cents patterns.
#     """
#     if len(transactions) < 3:
#         return 0.0

#     # Extract dollar and cents
#     cents = [int(round(t.amount % 1 * 100)) for t in transactions]
#     dollars = [int(t.amount) for t in transactions]

#     # --- Cents Consistency ---
#     cent_counts = Counter(cents)
#     most_common_cent, cent_count = cent_counts.most_common(1)[0]
#     cent_confidence = cent_count / len(transactions)

#     # --- Dollar Tightness ---
#     median_dollar = median(dollars)
#     dollar_tolerance = max(1, 0.10 * median_dollar)  # ±10% or ±$1, whichever is greater
#     dollar_consistency_count = sum(1 for d in dollars if abs(d - median_dollar) <= dollar_tolerance)
#     dollar_confidence = dollar_consistency_count / len(transactions)

#     # --- Combined Score Logic ---
#     if cent_confidence >= 0.6 and dollar_confidence >= 0.6:
#         # Strong recurring pattern in cents AND dollar proximity
#         return (cent_confidence + dollar_confidence) / 2
#     elif cent_confidence >= 0.7:
#         # Only cents dominate strongly
#         return cent_confidence
#     elif dollar_confidence >= 0.75:
#         # Only dollar amount clusters strongly
#         return dollar_confidence * 0.9  # slightly down-weight since cents aren't consistent
#     else:
#         return 0.0

# def dominant_cents_pattern_scores(transactions: list[Transaction]) -> float:
#     """
#     Detect recurring patterns in the cents portion of transaction amounts
#     where only the cents value is consistent (e.g., 9.77, 15.77, 43.77),
#     but dates and dollar amounts vary. Useful for Amazon, Apple, FloatMe.
#     """
#     if len(transactions) < 3:
#         return 0.0

#     # Extract cents part as integer
#     cents = [int(round(t.amount % 1 * 100)) for t in transactions]

#     # Count frequency of each cents value
#     cent_counts = Counter(cents)
#     most_common_cent, freq = cent_counts.most_common(1)[0]

#     # Confidence score: fraction of transactions with the dominant cents
#     confidence = freq / len(transactions)

#     # Return score if pattern is significantly dominant
#     return round(confidence, 4) if confidence >= 0.6 else 0.0

# def is_albert_recurring_subscription(transactions: list[Transaction]) -> float:
#     """
#     Detect recurring subscriptions in Albert (fixed range).
#     """
#     if not transactions or not any("albert" in t.name.lower() for t in transactions):
#         return 0.0

#     # Extract transaction amounts and dates
#     amounts = [t.amount for t in transactions]
#     dates = [parse_date(t.date) for t in transactions]

#     # Calculate median amount for consistency
#     median_amt = median(amounts)

#     # Check if the amount is within the recurring range for Albert
#     if 4.0 <= median_amt <= 7.0:
#         # Check for recurring interval consistency (e.g., monthly)
#         intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
#         if intervals and all(27 <= interval <= 33 for interval in intervals):
#             return 1.0  # Likely recurring subscription (within specified range and interval)

#     return 0.0


# def detect_parallel_loans(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """
#     Detects if a customer has multiple active loans from different lenders in the same period.
#     Returns a score indicating the likelihood of parallel loans.
#     """
#     current_date = parse_date(transaction.date)
#     window_days = 30  # Look for parallel loans within a 30-day window


#     # Get transactions within the window
#     window_transactions = [
#         t
#         for t in all_transactions
#         if abs((parse_date(t.date) - current_date).days) <= window_days
#         and t.name != transaction.name  # Different lender
#     ]

#     if not window_transactions:
#         return 0.0

#     # Calculate the ratio of different lenders in the window
#     unique_lenders = len({t.name for t in window_transactions})
#     return unique_lenders / len(window_transactions)


# def amount_stability_cluster_score(transactions: list[Transaction]) -> float:
#     """
#     Measures amount reliability using:
#     - Fixed-range tolerance stability
#     - KMeans clustering to detect dominant price bands
#     """
#     if len(transactions) < 3:
#         return 0.0

#     amounts = [t.amount for t in transactions]
#     mean_amt = np.mean(amounts)
#     std_amt = np.std(amounts)
#     tolerance = 0.05 * mean_amt  # 5% band

#     # Score how many amounts fall near the mean
#     within_band = sum(1 for a in amounts if abs(a - mean_amt) <= tolerance)
#     band_score = within_band / len(amounts)

#     # Use KMeans to detect dominant clusters
#     if len(set(amounts)) > 1:
#         arr = np.array(amounts).reshape(-1, 1)
#         k = min(3, len(set(amounts)))
#         km = KMeans(n_clusters=k, random_state=42)
#         labels = km.fit_predict(arr)

#         current_cluster = km.predict([[transactions[-1].amount]])[0]
#         dominant_cluster_size = np.bincount(labels)[current_cluster]
#         cluster_score = dominant_cluster_size / len(amounts)
#     else:
#         cluster_score = 1.0  # All same amounts

#     return 0.5 * band_score + 0.5 * cluster_score

# def is_albert_irregular_purchase(transactions: list[Transaction]) -> float:
#     if not transactions or not any("albert" in t.name.lower() for t in transactions):
#         return 0.0

#     amounts = [t.amount for t in transactions]
#     dates = [parse_date(t.date) for t in transactions]

#     # High variance detection
#     std_dev = np.std(amounts)
#     if std_dev > 3.0:
#         return 1.0  # Likely irregular purchase

#     intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
#     if len(intervals) >= 2 and np.std(intervals) > 30:  # <-- changed 3 → 2
#         return 1.0

#     return 0.0


# def is_brigit_non_recurring_payment(transactions: list[Transaction]) -> float:
#     """
#     Detect non-recurring payments in Brigit, such as one-off or irregular transactions.
#     """
#     if not transactions or not any("brigit" in t.name.lower() for t in transactions):
#         return 0.0

#     amounts = [t.amount for t in transactions]
#     dates = [parse_date(t.date) for t in transactions]

#     # Define typical recurring amounts for Brigit
#     typical_amounts = [8.99, 14.99]

#     # Check if amounts are significantly different from typical recurring amounts
#     if not all(any(abs(amount - typical_amt) > 1.0 for typical_amt in typical_amounts) for amount in amounts):
#         return 0.0

#     # Calculate intervals between transactions
#     intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

#     # Check for irregular intervals (not adhering to a monthly cycle)
#     if not all(interval > 35 or interval < 25 for interval in intervals):
#         return 0.0

#     return 1.0


# def is_afterpay_installments(transactions: list[Transaction]) -> float:
#     # Filter for Afterpay
#     filtered = [t for t in transactions if "afterpay" in t.name.lower()]
#     if len(filtered) < 4:
#         return 0.0

#     # Sort by date
#     filtered.sort(key=lambda t: parse_date(t.date))

#     # Get dates and amounts
#     dates = [parse_date(t.date) for t in filtered]
#     amounts = [t.amount for t in filtered]

#     # Interval pattern
#     intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
#     if not intervals:
#         return 0.0

#     interval_score = sum(1 for i in intervals if 10 <= i <= 17) / len(intervals)

#     # Amount similarity (within ±5%)
#     avg_amount = mean(amounts)
#     amount_score = sum(1 for amt in amounts if abs(amt - avg_amount) / avg_amount <= 0.05) / len(amounts)

#     # Combine both
#     pattern_score = (interval_score + amount_score) / 2
#     return round(pattern_score, 2)

# CHANGES STARTS HERE OF THE ADDING OF NEW FEATURES

# def detect_holiday_shift_pattern(all_transactions: list[Transaction]) -> float:
#     """
#     Detect if transaction dates shift around holidays but maintain overall regularity.
#     Returns a confidence score between 0 and 1.
#     """
#     if len(all_transactions) < 4:
#         return 0.0

#     # Define major holidays (month, day)
#     holidays = [
#         (1, 1),  # New Year's
#         (12, 25),  # Christmas
#         (11, 25),  # Thanksgiving (approximate)
#         (7, 4),  # Independence Day
#         (5, 31),  # Memorial Day (approximate)
#         (9, 1),  # Labor Day (approximate)
#     ]

#     # Sort transactions by date
#     sorted_transactions = sorted(all_transactions, key=lambda x: parse_date(x.date))
#     dates = [parse_date(t.date) for t in sorted_transactions if parse_date(t.date)]

#     if not dates:
#         return 0.0

#     # Check for date shifts around holidays
#     shifts = []
#     for i in range(len(dates) - 1):
#         days_diff = (dates[i + 1] - dates[i]).days

#         # Check if either date is near a holiday
#         near_holiday = False
#         for holiday_month, holiday_day in holidays:
#             for current_date in [dates[i], dates[i + 1]]:
#                 if current_date.month == holiday_month and abs(current_date.day - holiday_day) <= 3:
#                     near_holiday = True

#         if near_holiday:
#             shifts.append(days_diff)

#     if not shifts:
#         return 0.0

#     # Calculate shift consistency
#     avg_shift = np.mean(shifts)
#     std_shift = np.std(shifts)

#     # Higher score if shifts are consistent
#     consistency_score = 1.0 - min(float(std_shift / avg_shift) if avg_shift > 0 else 1.0, 1.0)
#     return float(consistency_score)


# def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int | bool | float]:
#     """Get the new features for the transaction."""

#     # Initialize features dictionary
#     features = {
#         "is_amazon_prime": get_is_amazon_prime(transaction),
#     }

#     # Add seasonal variation detection
#     amounts = [t.amount for t in all_transactions]
#     if len(amounts) >= 12:  # Need at least a year of data
#         features["seasonal_variation"] = detect_seasonal_variation(amounts)

#     # Add business day alignment
#     features["business_day_alignment"] = is_business_day_aligned(transaction, all_transactions)

#     # Add variable subscription detection
#     features["is_variable_subscription"] = detect_variable_subscription(transaction, all_transactions)

#     # Add reference number pattern detection
#     features["has_sequential_reference"] = has_sequential_reference_numbers(transaction, all_transactions)

#     # Add payment method consistency
#     features["payment_method_consistency"] = get_payment_method_consistency(transaction, all_transactions)

# def is_cleo_subscription_like(transactions: list[Transaction]) -> float:
#     """Detect recurring Cleo app-related charges (Cleo Plus, Cleo Builder)."""
#     if not transactions or not any("cleo" in t.name.lower() for t in transactions):
#         return 0.0

#     # Focus on subscription-based Cleo charges (not AI cash advances)
#     subscription_txns = [t for t in transactions if "cleo ai" not in t.name.lower()]
#     if len(subscription_txns) < 2:
#         return 0.0

#     amounts = [t.amount for t in subscription_txns]
#     dates = [parse_date(t.date) for t in subscription_txns]
#     median_amt = median(amounts)

#     # Filter out non-subscription size transactions
#     if median_amt < 2 or median_amt > 15:
#         return 0.0

#     intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
#     if not intervals:
#         return 0.0

#     monthly_pattern = sum(1 for d in intervals if 27 <= d <= 33) / len(intervals)
#     amount_consistency = sum(1 for amt in amounts if abs(amt - median_amt) <= 1.5) / len(amounts)

#     return 0.6 * monthly_pattern + 0.4 * amount_consistency


#     # Add new advanced features
#     features["multi_tier_subscription"] = detect_multi_tier_subscription(transaction, all_transactions)
#     features["annual_price_adjustment"] = detect_annual_price_adjustment(transaction, all_transactions)
#     features["holiday_shift_pattern"] = detect_holiday_shift_pattern(transaction, all_transactions)
#     features["pay_period_alignment"] = detect_pay_period_alignment(transaction, all_transactions)

#     return features
