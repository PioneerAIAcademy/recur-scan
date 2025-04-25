from difflib import SequenceMatcher

from recur_scan.transactions import Transaction
from recur_scan.utils import get_day, parse_date


def get_n_transactions_same_description(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same description as transaction"""
    return len([t for t in all_transactions if t.name == transaction.name])  # type: ignore


def get_percent_transactions_same_description(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same description as transaction"""
    if not all_transactions:
        return 0.0
    n_same_description = len([t for t in all_transactions if t.name == transaction.name])  # type: ignore
    return n_same_description / len(all_transactions)


def get_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the average number of days between occurrences of this transaction."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 2:
        return 0.0  # Not enough data to calculate frequency

    dates = sorted([parse_date(t.date).toordinal() for t in same_transactions])
    intervals = [dates[i] - dates[i - 1] for i in range(1, len(dates))]
    return sum(intervals) / len(intervals)


def get_day_of_month_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the consistency of the day of the month for transactions with the same name."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 2:
        return 0.0  # Not enough data to calculate consistency

    days = [get_day(t.date) for t in same_transactions]
    most_common_day = max(set(days), key=days.count)
    return sum(1 for day in days if day == most_common_day) / len(days)


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    """Calculate a comprehensive set of features for detecting recurring transactions.

    Args:
        transaction: The transaction to analyze
        all_transactions: List of all transactions in the dataset

    Returns:
        Dictionary of feature names and their values
    """
    features = {}

    features["amount_consistency"] = get_amount_consistency(transaction, all_transactions)
    features["amount_variance"] = get_amount_variance(transaction, all_transactions)
    features["monthly_pattern_score"] = get_monthly_pattern_score(transaction, all_transactions)
    features["weekly_pattern_score"] = get_weekly_pattern_score(transaction, all_transactions)
    features["biweekly_pattern_score"] = get_biweekly_pattern_score(transaction, all_transactions)
    features["quarterly_pattern_score"] = get_quarterly_pattern_score(transaction, all_transactions)
    features["yearly_pattern_score"] = get_yearly_pattern_score(transaction, all_transactions)
    features["avg_description_similarity"] = get_avg_description_similarity(transaction, all_transactions)
    features["contains_subscription_keywords"] = contains_subscription_keywords(transaction)
    features["same_category_ratio"] = get_same_category_ratio(transaction, all_transactions)
    features["merchant_consistency"] = get_merchant_consistency(transaction, all_transactions)
    features["recurring_score"] = get_recurring_score(transaction, all_transactions, features)

    return features


def get_amount_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate how consistent the amount is for transactions with the same name."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 2:
        return 0.0

    amounts = [t.amount for t in same_transactions]
    most_common_amount = max(set(amounts), key=amounts.count)
    return sum(1 for amount in amounts if amount == most_common_amount) / len(amounts)


def get_amount_variance(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the normalized variance in amounts for transactions with the same name."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 2:
        return 1.0  # High variance (bad) when not enough data

    amounts = [t.amount for t in same_transactions]
    mean_amount = sum(amounts) / len(amounts)
    if mean_amount == 0:
        return 1.0
    variance = sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)
    # Normalize by the square of the mean to get a relative measure
    return min(variance / (mean_amount**2), 1.0)


def get_monthly_pattern_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Score how well the transaction fits a monthly pattern."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 3:
        return 0.0

    dates = sorted([parse_date(t.date) for t in same_transactions])
    # Convert to days since first transaction
    first_date = dates[0]
    days_since_first = [(d - first_date).days for d in dates]

    # Check if intervals are close to 28-31 days
    intervals = [days_since_first[i] - days_since_first[i - 1] for i in range(1, len(days_since_first))]
    monthly_intervals = [i for i in intervals if 25 <= i <= 35]
    return len(monthly_intervals) / len(intervals) if intervals else 0.0


def get_weekly_pattern_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Score how well the transaction fits a weekly pattern."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 3:
        return 0.0

    dates = sorted([parse_date(t.date) for t in same_transactions])
    # Get day of week consistency (0=Monday, 6=Sunday)
    weekdays = [d.weekday() for d in dates]
    most_common_weekday = max(set(weekdays), key=weekdays.count)
    weekday_consistency = sum(1 for wd in weekdays if wd == most_common_weekday) / len(weekdays)

    # Check if intervals are close to 7 days
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    weekly_intervals = [i for i in intervals if 6 <= i <= 8]
    interval_match = len(weekly_intervals) / len(intervals) if intervals else 0.0

    return (weekday_consistency + interval_match) / 2


def get_biweekly_pattern_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Score how well the transaction fits a biweekly (every two weeks) pattern."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 3:
        return 0.0

    dates = sorted([parse_date(t.date) for t in same_transactions])

    # Check if intervals are close to 14 days
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    biweekly_intervals = [i for i in intervals if 13 <= i <= 15]
    return len(biweekly_intervals) / len(intervals) if intervals else 0.0


def get_quarterly_pattern_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Score how well the transaction fits a quarterly pattern."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 3:
        return 0.0

    dates = sorted([parse_date(t.date) for t in same_transactions])
    # Check if intervals are close to 90 days
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    quarterly_intervals = [i for i in intervals if 85 <= i <= 95]
    return len(quarterly_intervals) / len(intervals) if intervals else 0.0


def get_yearly_pattern_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Score how well the transaction fits a yearly pattern."""
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_transactions) < 2:
        return 0.0

    dates = sorted([parse_date(t.date) for t in same_transactions])
    # Check if intervals are close to 365 days
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    yearly_intervals = [i for i in intervals if 360 <= i <= 370]
    return len(yearly_intervals) / len(intervals) if intervals else 0.0


def get_description_similarity(transaction: Transaction, other_transaction: Transaction) -> float:
    """Calculate text similarity between transaction descriptions."""
    name1 = transaction.name.lower()
    name2 = other_transaction.name.lower()

    # Remove common prefixes/suffixes that might vary in recurring transactions
    common_prefixes = ["payment to ", "payment for ", "subscription to ", "recurring ", "auto "]
    common_suffixes = [" subscription", " payment", " monthly", " weekly", " charge"]

    for prefix in common_prefixes:
        if name1.startswith(prefix):
            name1 = name1[len(prefix) :]
        if name2.startswith(prefix):
            name2 = name2[len(prefix) :]

    for suffix in common_suffixes:
        if name1.endswith(suffix):
            name1 = name1[: -len(suffix)]
        if name2.endswith(suffix):
            name2 = name2[: -len(suffix)]

    return SequenceMatcher(None, name1, name2).ratio()


def get_avg_description_similarity(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get average similarity of this transaction to others with similar names."""
    # Find transactions with some basic similarity
    potential_matches = [
        t
        for t in all_transactions
        if t.id != transaction.id  # Don't compare with self
        and get_description_similarity(transaction, t) > 0.6
    ]

    if not potential_matches:
        return 0.0

    similarities = [get_description_similarity(transaction, t) for t in potential_matches]
    return sum(similarities) / len(similarities)


def contains_subscription_keywords(transaction: Transaction) -> float:
    """Check if the transaction description contains keywords related to subscriptions."""
    subscription_keywords = [
        "subscription",
        "monthly",
        "recurring",
        "membership",
        "premium",
        "plan",
        "auto-pay",
        "renewal",
        "bill pay",
        "service fee",
    ]

    name = transaction.name.lower()
    matches = sum(1 for keyword in subscription_keywords if keyword in name)
    # Return a normalized score
    return min(matches / 3, 1.0)  # Cap at 1.0 for 3+ matches


def get_same_category_ratio(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the ratio of transactions with the same name that have the same category."""
    if not hasattr(transaction, "category") or transaction.category is None:
        return 0.0

    same_name_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(same_name_transactions) < 2:
        return 0.0

    same_category = [t for t in same_name_transactions if hasattr(t, "category") and t.category == transaction.category]
    return len(same_category) / len(same_name_transactions)


def get_merchant_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the consistency of merchant information for similar transactions."""
    if not hasattr(transaction, "merchant_id") or transaction.merchant_id is None:
        return 0.0

    similar_transactions = [t for t in all_transactions if get_description_similarity(transaction, t) > 0.8]
    if len(similar_transactions) < 2:
        return 0.0

    merchant_ids = [getattr(t, "merchant_id", None) for t in similar_transactions]
    merchant_ids = [m for m in merchant_ids if m is not None]
    if not merchant_ids:
        return 0.0

    most_common_merchant = max(set(merchant_ids), key=merchant_ids.count)
    return sum(1 for mid in merchant_ids if mid == most_common_merchant) / len(merchant_ids)


def get_recurring_score(
    transaction: Transaction, all_transactions: list[Transaction], features: dict[str, float] | None = None
) -> float:
    """Combine multiple metrics to create a stronger recurring probability score."""
    if features is None:
        # Calculate base features if not provided
        day_consistency = get_day_of_month_consistency(transaction, all_transactions)
        amount_consistency = get_amount_consistency(transaction, all_transactions)
        amount_variance = get_amount_variance(transaction, all_transactions)
        monthly_pattern = get_monthly_pattern_score(transaction, all_transactions)
        weekly_pattern = get_weekly_pattern_score(transaction, all_transactions)
        biweekly_pattern = get_biweekly_pattern_score(transaction, all_transactions)
    else:
        # Use pre-calculated features
        # day_consistency = features["day_of_month_consistency"]
        day_consistency = features.get("day_of_month_consistency", 0.0)
        amount_consistency = features["amount_consistency"]
        amount_variance = features["amount_variance"]
        monthly_pattern = features["monthly_pattern_score"]
        weekly_pattern = features["weekly_pattern_score"]
        biweekly_pattern = features.get("biweekly_pattern_score", 0.0)

    # Count how many similar transactions we have
    same_transactions = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    count_factor = min(len(same_transactions) / 5, 1.0)  # Scales up to 5 occurrences

    # Check for time patterns - take the strongest pattern
    time_pattern_score = max(monthly_pattern, weekly_pattern, biweekly_pattern)

    # Combine into final score - weights should be tuned based on testing
    score = (
        0.15 * day_consistency
        + 0.20 * amount_consistency
        + 0.15 * (1 - amount_variance)  # Lower variance is better
        + 0.20 * time_pattern_score
        + 0.30 * count_factor  # More occurrences increases confidence
    )

    return score
