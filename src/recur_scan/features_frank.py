import re
from collections import Counter, defaultdict
from collections.abc import Sequence
from datetime import timedelta
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

    if not amounts:
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
    similarity_score = max(1.0, 10.0 - (abs(days_since - avg_interval) / avg_interval) * 9)

    return round(similarity_score, 2)  # Round for stability


def enhanced_n_similar_last_n_days(
    transaction: Transaction, all_transactions: list[Transaction], days: int = 90
) -> float:
    """Counts similar transactions within a given time window, scaled from 1 to 10."""

    similar_transactions = [
        t
        for t in all_transactions
        if abs(parse_date(t.date) - parse_date(transaction.date)).days <= days
        and abs(t.amount - transaction.amount) / transaction.amount <= 0.051  # Slightly increased tolerance
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


# def detect_recurring_company(company_name: str) -> dict[str, float]:
#     """
#     Detects if a company is likely to offer recurring payments (e.g., subscriptions, utilities).
#      Returns a dictionary of features:
#     - is_recurring_company: 1 if the company is known to offer recurring payments, else 0
#     - is_utility_company: 1 if the company is a utility provider, else 0
#     - recurring_score: Confidence score (0 to 1) based on keyword matches
#     """
#     cleaned_name = clean_company_name(company_name)

#     # Check if the company is a known recurring company
#     is_recurring_company = 1 if RECURRING_PATTERN.search(cleaned_name) else 0

#     # Check if the company is a utility provider
#     is_utility_company = 1 if UTILITY_PATTERN.search(cleaned_name) else 0

#     # Calculate a recurring score based on keyword matches
#     recurring_score = 0.0
#     if is_recurring_company:
#         recurring_score = 1.0
#     elif is_utility_company:
#         recurring_score = 0.8  # Utilities are highly likely to be recurring
#     else:
#         # Check for partial matches (e.g., "Netflix Inc.")
#         for keyword in KNOWN_RECURRING_COMPANIES:
#             if keyword in cleaned_name:
#                 recurring_score = max(recurring_score, 0.7)  # Partial match confidence

#     return {
#         "is_recurring_company": is_recurring_company,
#         "is_utility_company": is_utility_company,
#         "recurring_score": recurring_score,
#     }


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

    return max(0.0, 1 - (abs(current_interval - median_interval) / median_interval))  # Ensure result is non-negative


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
