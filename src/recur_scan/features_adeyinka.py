import statistics
from collections import Counter
from datetime import datetime, timedelta

from recur_scan.features_original import get_n_transactions_same_amount
from recur_scan.transactions import Transaction


# parse date
def parse_date(date_str: str) -> datetime:
    """Parse date string into datetime object"""
    try:
        # Assuming date format is MM/DD/YYYY based on your sample
        return datetime.strptime(date_str, "%m/%d/%Y")
    except ValueError:
        # Fallback if format is different
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            # Return a default date if parsing fails
            return datetime(1970, 1, 1)


def get_average_days_between_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate average days between transactions with the same vendor,
    ensuring only valid and recent dates are considered.
    """
    # Get transactions with the same vendor
    same_vendor_txns = [t for t in all_transactions if t.name == transaction.name]

    # Extract and validate dates
    valid_dates = []
    current_year = datetime.now().year

    for t in same_vendor_txns:
        try:
            parsed_date = parse_date(t.date)

            # Combine conditions into a single validation check
            if (
                parsed_date
                and isinstance(parsed_date, datetime)
                and parsed_date.year <= current_year
                and parsed_date.year > (current_year - 10)
            ):
                valid_dates.append(parsed_date)
        except Exception:
            # Silently ignore any parsing errors
            continue

    # If there are fewer than 2 valid dates, return 0
    if len(valid_dates) < 2:
        return 0.0

    # Sort valid dates in ascending order
    valid_dates.sort()

    # Compute the day differences
    day_diffs = [(valid_dates[i] - valid_dates[i - 1]).days for i in range(1, len(valid_dates))]

    # Return the average difference in days
    return sum(day_diffs) / len(day_diffs) if day_diffs else 0.0


# get_time
def get_time_regularity_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate regularity of time intervals (lower std dev = more regular)"""
    same_vendor_txns = [t for t in all_transactions if t.name == transaction.name]
    if len(same_vendor_txns) <= 2:
        return 0.0

    try:
        # Sort by date
        sorted_txns = sorted(same_vendor_txns, key=lambda t: parse_date(t.date))

        # Calculate days between consecutive transactions
        days_between = []
        for i in range(1, len(sorted_txns)):
            days = (parse_date(sorted_txns[i].date) - parse_date(sorted_txns[i - 1].date)).days
            days_between.append(days)

        # Combine the empty check with standard deviation calculation
        if not days_between or len(days_between) <= 1:
            return 0.0

        std_dev = statistics.stdev(days_between)
        # Convert to a score between 0 and 1 (1 = perfectly regular)
        return 1.0 / (1.0 + std_dev / 5.0)
    except Exception:
        return 0.0


def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring because of the vendor name - check lowercase match"""
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
        "amazon prime",
        "disney+",
        "apple music",
        "xbox game pass",
        "youtube premium",
        "adobe creative cloud",
    }
    return transaction.name.lower() in always_recurring_vendors


# New helper functions for date handling
def _get_days(date: str) -> int:
    """Get the number of days since the epoch of a transaction date."""
    try:
        date_obj = parse_date(date)
        return (date_obj - datetime(1970, 1, 1)).days
    except Exception:
        return 0


# def _get_day(date: str) -> int:
#     """Get the day of the month from a transaction date."""
#     try:
#         date_obj = parse_date(date)
#         return date_obj.day
#     except Exception:
#         return 0


def get_n_transactions_days_apart(
    transaction: Transaction, all_transactions: list[Transaction], n_days_apart: int, n_days_off: int
) -> int:
    """Find how many transactions happen within `n_days_off` of `n_days_apart`."""
    n_txs = 0
    transaction_days = _get_days(transaction.date)

    for t in all_transactions:
        if t.id == transaction.id:
            continue

        t_days = _get_days(t.date)
        days_diff = abs(t_days - transaction_days)

        # Calculate quotient and remainder
        quotient = days_diff / n_days_apart
        remainder = abs(days_diff - round(quotient) * n_days_apart)

        # Combine conditions into a single check
        if remainder <= n_days_off and abs(quotient - round(quotient)) < 0.1:
            n_txs += 1

    return n_txs


def get_transaction_amount_variance(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate standard deviation of transaction amounts for the same vendor."""
    vendor_txns = [t.amount for t in all_transactions if t.name == transaction.name]

    if len(vendor_txns) <= 1:
        return 0.0  # No variance if there's only one transaction

    return statistics.stdev(vendor_txns)


def get_outlier_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Detects if a transaction amount is an outlier with a refined Z-score method."""
    vendor_txns = [t.amount for t in all_transactions if t.name == transaction.name]

    if len(vendor_txns) <= 1:
        return 0.0  # No outliers if only one transaction

    mean_amount = statistics.mean(vendor_txns)
    std_dev = statistics.pstdev(vendor_txns) if len(vendor_txns) > 1 else 0  # Use population std deviation

    if std_dev == 0:
        return 0.0  # No variation, so no outliers

    # Increase outlier sensitivity by using absolute Z-score
    z_score = abs((transaction.amount - mean_amount) / std_dev)

    # Apply a scaling factor to push outliers higher
    adjusted_z_score = z_score * 1.5

    return adjusted_z_score  # Should now exceed 2.0 for clear outliers


def get_recurring_confidence_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate a score indicating how likely this transaction is recurring"""
    frequency = get_n_transactions_same_amount(transaction, all_transactions)
    regularity = get_time_regularity_score(transaction, all_transactions)
    always_recurring = get_is_always_recurring(transaction)

    # Weighted sum of features
    score = (0.4 * frequency) + (0.4 * regularity) + (0.2 * always_recurring)

    return min(score, 1.0)  # Ensure the score is between 0 and 1


def get_subscription_keyword_score(transaction: Transaction) -> float:
    """
    Detect subscription-related keywords in transaction names
    that strongly indicate recurring transactions.
    """
    subscription_keywords = [
        "monthly",
        "subscription",
        "premium",
        "plus",
        "membership",
        "service",
        "plan",
        "bill",
        "energy",
        "utility",
        "insurance",
        "mobile",
        "+",
        "max",
        "prime",
        "fiber",
        "internet",
        "streaming",
    ]

    # Check for exact matches in the always_recurring_vendors list first
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
        "amazon prime",
        "disney+",
        "apple music",
        "xbox game pass",
        "youtube premium",
        "adobe creative cloud",
        "metro by t-mobile",
        "t-mobile",
        "at&t",
        "xfinity",
        "comcast",
        "audible",
        "apple",
        "microsoft",
        "sirius",
        "siriusxm",
        "hbo",
        "progressive",
        "geico",
        "affirm",
        "afterpay",
        "klarna",
        "starz",
        "cps energy",
        "verizon",
        "planet fitness",
    }

    if transaction.name.lower() in always_recurring_vendors:
        return 1.0

    # Check for keywords in the transaction name
    txn_name_lower = transaction.name.lower()
    for keyword in subscription_keywords:
        if keyword in txn_name_lower:
            return 0.8

    return 0.0


def get_same_amount_vendor_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """
    Count transactions with same vendor AND same amount (excluding the transaction itself).
    """
    matching_transactions = [
        t
        for t in all_transactions
        if t.name == transaction.name and abs(t.amount - transaction.amount) < 0.1 and t.id != transaction.id
    ]

    # print(f"Transaction being checked: {transaction}")
    # print(f"Matching transactions: {matching_transactions}")

    return len(matching_transactions)


# New features


def get_amount_consistency_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Measures how consistent the transaction amounts are for the same vendor.
    Returns a score from 0.0 (inconsistent) to 1.0 (very consistent).
    """
    # Filter transactions with the same vendor name
    same_vendor_txns = [t.amount for t in all_transactions if t.name == transaction.name]

    if len(same_vendor_txns) < 2:
        return 0.0

    # Calculate mean and mean absolute deviation
    mean_amount = statistics.mean(same_vendor_txns)
    mad = statistics.mean([abs(x - mean_amount) for x in same_vendor_txns])

    # Normalize: if MAD is very low, consistency is high
    # Add 1 to denominator to avoid division by zero
    consistency_score = 1.0 / (1.0 + mad / (mean_amount + 1e-6))

    # Clamp between 0 and 1
    return min(max(consistency_score, 0.0), 1.0)


# def get_amount_sequence_pattern(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """
#     Detects patterns in amount sequences, like installment payments.
#     Returns high score if amounts follow a pattern.
#     """
#     # Filter and sort transactions with the same vendor by date
#     same_vendor_txns = [t for t in all_transactions if t.name == transaction.name]

#     if len(same_vendor_txns) < 3:
#         return 0.0

#     try:
#         # Sort by date
#         sorted_txns = sorted(same_vendor_txns, key=lambda t: parse_date(t.date))

#         # Extract amounts
#         amounts = [t.amount for t in sorted_txns]

#         # Check for identical amounts (most common recurring pattern)
#         unique_amounts = set(amounts)
#         if len(unique_amounts) == 1:
#             return 1.0

#         # Check for two alternating amounts
#         if len(unique_amounts) == 2:
#             # Get the two unique amounts
#             amt1, amt2 = list(unique_amounts)

#             # Check if they alternate
#             expected_pattern = [amt1, amt2] * (len(amounts) // 2 + 1)
#             expected_pattern = expected_pattern[:len(amounts)]

#             matches = sum(1 for i in range(len(amounts)) if abs(amounts[i] - expected_pattern[i]) < 0.01)
#             if matches / len(amounts) > 0.8:
#                 return 0.9

#         # Check for simple arithmetic progression
#         diffs = [amounts[i] - amounts[i-1] for i in range(1, len(amounts))]
#         if len(diffs) >= 2:
#             avg_diff = sum(diffs) / len(diffs)
#             if avg_diff != 0:
#                 # Check if differences are consistent (within 10%)
#                 consistency = sum(1 for d in diffs if abs(d - avg_diff) < abs(avg_diff * 0.1)) / len(diffs)
#                 if consistency > 0.8:
#                     return 0.8

#         return 0.0
#     except Exception:
#         return 0.0


def get_day_of_month_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Detect if transactions consistently occur on similar days of the month"""
    same_vendor_txns = [t for t in all_transactions if t.name == transaction.name]
    if len(same_vendor_txns) < 3:
        return 0.0

    try:
        # Extract days of month
        days = [parse_date(t.date).day for t in same_vendor_txns]

        # Group by day and count occurrences
        day_counts = Counter(days)
        most_common_day, most_common_count = day_counts.most_common(1)[0]

        # Calculate consistency score
        consistency = most_common_count / len(days)
        return consistency
    except Exception:
        return 0.0


# def get_weekly_recurrence_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """Detect if transactions follow weekly patterns (7, 14, 28 days)"""
#     same_vendor_txns = [t for t in all_transactions if t.name == transaction.name]
#     if len(same_vendor_txns) < 3:
#         return 0.0

#     try:
#         # Sort by date
#         sorted_txns = sorted(same_vendor_txns, key=lambda t: parse_date(t.date))

#         # Calculate days between transactions
#         intervals = [(parse_date(sorted_txns[i].date) - parse_date(sorted_txns[i-1].date)).days
#                      for i in range(1, len(sorted_txns))]

#         # Check how many intervals are close to weekly multiples
#         weekly_intervals = sum(1 for interval in intervals if
#                            any(abs(interval - (7 * w)) <= 2 for w in [1, 2, 3, 4]))

#         return weekly_intervals / len(intervals) if intervals else 0.0
#     except Exception:
#         return 0.0


# def get_amount_date_correlation(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """Detect patterns where transaction amounts correlate with certain dates"""
#     same_vendor_txns = [t for t in all_transactions if t.name == transaction.name]
#     if len(same_vendor_txns) < 4:
#         return 0.0

#     try:
#         # Create map of day of month to amounts
#         day_amounts = {}
#         for t in same_vendor_txns:
#             day = parse_date(t.date).day
#             if day not in day_amounts:
#                 day_amounts[day] = []
#             day_amounts[day].append(t.amount)

#         # Check if specific days have consistent amounts
#         correlation_score = 0.0
#         for day, amounts in day_amounts.items():
#             if len(amounts) >= 2:
#                 # Calculate variance of amounts for this day
#                 mean_amount = sum(amounts) / len(amounts)
#                 variance = sum((a - mean_amount) ** 2 for a in amounts) / len(amounts)

#                 # Lower variance means higher correlation
#                 if variance < 1.0:
#                     correlation_score += len(amounts) / len(same_vendor_txns)

#         return min(correlation_score, 1.0)
#     except Exception:
#         return 0.0


def is_bnpl_service(transaction: Transaction) -> float:
    """Identify Buy Now Pay Later services which often have recurring payments"""
    bnpl_services = {"rise up lending"}

    if "credit ninja" in transaction.name.lower():
        return 1.0
    if "credit genie" in transaction.name.lower():
        return 1.0

    return 1.0 if transaction.name.lower() in bnpl_services else 0.0


def get_recent_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate frequency of transactions with this vendor in the last 90 days"""
    same_vendor_txns = [t for t in all_transactions if t.name == transaction.name]

    try:
        current_date = parse_date(transaction.date)
        ninety_days_ago = current_date - timedelta(days=90)

        # Count transactions in last 90 days
        recent_count = sum(1 for t in same_vendor_txns if parse_date(t.date) >= ninety_days_ago)

        # Normalize to a 0-1 scale (more than 6 in 90 days = 1.0)
        return min(recent_count / 6.0, 1.0)
    except Exception:
        return 0.0


def get_phone_bill_indicator(transaction: Transaction) -> float:
    """
    Detect phone bill payments
    (addressing Sprint and similar)
    """
    telecom_providers = {
        "sprint",
        "t-mobile",
        "verizon",
        "at&t",
        "cricket",
        "boost",
        "metropcs",
        "phone",
        "mobile",
        "wireless",
        "cellular",
        "telecom",
        "communications",
    }

    name_lower = transaction.name.lower()

    # Check for telecom keywords
    has_telecom_keyword = any(provider in name_lower for provider in telecom_providers)

    # Check for typical bill amounts
    is_typical_amount = 10.0 <= transaction.amount <= 200.0

    # Combine factors
    score = (0.7 * has_telecom_keyword) + (0.3 * is_typical_amount)
    return min(score, 1.0)


# def get_loan_payment_indicator(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     """
#     Detect loan payment patterns
#     (addressing Lendswift and similar)
#     """
#     # Common loan keywords
#     loan_keywords = [
#         "loan", "lend", "lending", "finance", "financial", "capital", "credit",
#         "payment", "installment", "swift", "fast", "quick", "cash", "money", "fund"
#     ]

#     # Check for keywords in name
#     name_lower = transaction.name.lower()
#     keyword_score = 0.0
#     for keyword in loan_keywords:
#         if keyword in name_lower:
#             keyword_score += 0.2
#     keyword_score = min(keyword_score, 0.6)

#     # Usually consistent amounts
#     same_vendor_txns = [t for t in all_transactions if t.name == transaction.name]
#     amount_consistency = 0.0

#     if len(same_vendor_txns) >= 2:
#         try:
#             amounts = [t.amount for t in same_vendor_txns]
#             most_common_amount = Counter(amounts).most_common(1)[0][0]

#             # Check how many match the most common amount
#             exact_matches = sum(1 for a in amounts if abs(a - most_common_amount) < 0.01)
#             amount_consistency = exact_matches / len(amounts)
#         except:
#             amount_consistency = 0.0

#     # Combine factors
#     score = keyword_score + (0.4 * amount_consistency)
#     return min(score, 1.0)


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int | bool | float]:
    return {
        "amount_consistency_score": get_amount_consistency_score(transaction, all_transactions),
        "day_of_month_consistency": get_day_of_month_consistency(transaction, all_transactions),
        "bnpl_service": is_bnpl_service(transaction),
        "recent_transaction_frequency": get_recent_transaction_frequency(transaction, all_transactions),
        "phone_bill_indicator": get_phone_bill_indicator(transaction),
        # "loan_payment_indicator": get_loan_payment_indicator(transaction, all_transactions),
    }
