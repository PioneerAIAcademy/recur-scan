import statistics
from datetime import datetime

from recur_scan.transactions import Transaction


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions)


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


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "avg_days_between_transactions": get_average_days_between_transactions(transaction, all_transactions),
        "time_regularity_score": get_time_regularity_score(transaction, all_transactions),
        "is_always_recurring": get_is_always_recurring(transaction),
        "transaction_amount_variance": get_transaction_amount_variance(transaction, all_transactions),
        "outlier_score": get_outlier_score(transaction, all_transactions),
        "recurring_confidence_score": get_recurring_confidence_score(transaction, all_transactions),
        "subscription_keyword_score": get_subscription_keyword_score(transaction),
        "same_amount_vendor_transactions": get_same_amount_vendor_transactions(transaction, all_transactions),
        # Regular interval features
        "30_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 30, 0),
        "30_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 30, 1),
        "14_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 14, 0),
        "14_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 14, 1),
        "7_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 7, 0),
        "7_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 7, 1),
    }
