import datetime
import itertools
import re
import statistics
from datetime import date
from functools import lru_cache

from recur_scan.transactions import Transaction

# Allowed feature value type
FeatureValue = float | int | bool | str

# ------------------------- Original Feature Functions -------------------------


def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring because of the vendor name - check lowercase match"""
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
    }
    return transaction.name.lower() in always_recurring_vendors


def get_is_insurance(transaction: Transaction) -> bool:
    """Check if the transaction is an insurance payment."""
    match = re.search(r"\b(insurance|insur|insuranc)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_utility_regex(transaction: Transaction) -> bool:
    """Check if the transaction is a utility payment using regex."""
    match = re.search(r"\b(utility|utilit|energy)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_phone_regex(transaction: Transaction) -> bool:
    """Check if the transaction is a phone payment using regex."""
    match = re.search(r"\b(at&t|t-mobile|verizon)\b", transaction.name, re.IGNORECASE)
    return bool(match)


@lru_cache(maxsize=1024)
def _parse_date(date_str: str) -> date:
    """Parse a date string into a datetime.date object."""
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def get_n_transactions_days_apart(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> int:
    """
    Get the number of transactions in all_transactions that are within n_days_off of
    being n_days_apart from transaction
    """
    n_txs = 0
    transaction_date = _parse_date(transaction.date)
    lower_remainder = n_days_apart - n_days_off
    upper_remainder = n_days_off
    for t in all_transactions:
        t_date = _parse_date(t.date)
        days_diff = abs((t_date - transaction_date).days)
        if days_diff < n_days_apart - n_days_off:
            continue
        remainder = days_diff % n_days_apart
        if remainder <= upper_remainder or remainder >= lower_remainder:
            n_txs += 1
    return n_txs


def get_pct_transactions_days_apart(
    transaction: Transaction, all_transactions: list[Transaction], n_days_apart: int, n_days_off: int
) -> float:
    return get_n_transactions_days_apart(transaction, all_transactions, n_days_apart, n_days_off) / len(
        all_transactions
    )


def _get_day(date_str: str) -> int:
    """Get the day of the month from a transaction date."""
    return int(date_str.split("-")[2])


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    """Get the number of transactions in all_transactions that are on the same day of the month as transaction"""
    return len([t for t in all_transactions if abs(_get_day(t.date) - _get_day(transaction.date)) <= n_days_off])


def get_pct_transactions_same_day(
    transaction: Transaction, all_transactions: list[Transaction], n_days_off: int
) -> float:
    return get_n_transactions_same_day(transaction, all_transactions, n_days_off) / len(all_transactions)


def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in .99 using string formatting after rounding."""
    amount_str = f"{round(transaction.amount, 2):.2f}"
    return amount_str.endswith("99")


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return sum(1 for t in all_transactions if t.amount == transaction.amount)


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    if not all_transactions:
        return 0.0
    return get_n_transactions_same_amount(transaction, all_transactions) / len(all_transactions)


def amount_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in .99 using string formatting after rounding."""
    amount_str = f"{round(transaction.amount, 2):.2f}"
    return amount_str.endswith("99")


def amount_ends_in_00(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in .00 using string formatting after rounding."""
    amount_str = f"{round(transaction.amount, 2):.2f}"
    return amount_str.endswith("00")


def is_recurring_merchant(transaction: Transaction) -> bool:
    """Check if the transaction's merchant is a known recurring company"""
    recurring_keywords = {
        "at&t",
        "google play",
        "verizon",
        "vz wireless",
        "vzw",
        "t-mobile",
        "apple",
        "disney+",
        "disney mobile",
        "hbo max",
        "amazon prime",
        "netflix",
        "spotify",
        "hulu",
        "la fitness",
        "cleo ai",
        "atlas",
        "google storage",
        "google drive",
        "youtube premium",
        "afterpay",
        "amazon+",
        "walmart+",
        "amazonprime",
        "duke energy",
        "adobe",
        "healthy.line",
        "canva pty limite",
        "brigit",
        "cleo",
        "microsoft",
        "earnin",
    }
    merchant_name = transaction.name.lower()
    return any(keyword in merchant_name for keyword in recurring_keywords)


def get_n_transactions_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions with the same merchant and amount"""
    return sum(1 for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount)


def get_percent_transactions_same_merchant_amount(
    transaction: Transaction, all_transactions: list[Transaction]
) -> float:
    if not all_transactions:
        return 0.0
    n_same = get_n_transactions_same_merchant_amount(transaction, all_transactions)
    return n_same / len(all_transactions)


def get_avg_days_between_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the average days between transactions with the same merchant and amount"""
    same_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount],
        key=lambda x: x.date,
    )
    if len(same_transactions) < 2:
        return 0.0
    intervals = [
        (
            datetime.datetime.strptime(t2.date, "%Y-%m-%d").date()
            - datetime.datetime.strptime(t1.date, "%Y-%m-%d").date()
        ).days
        for t1, t2 in itertools.pairwise(same_transactions)
    ]
    return sum(intervals) / len(intervals) if intervals else 0.0


def get_stddev_days_between_same_merchant_amount(
    transaction: Transaction, all_transactions: list[Transaction]
) -> float:
    """Calculate the standard deviation of days between transactions with the same merchant and amount"""
    same_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount],
        key=lambda x: x.date,
    )
    if len(same_transactions) < 2:
        return 0.0
    intervals = [
        (
            datetime.datetime.strptime(t2.date, "%Y-%m-%d").date()
            - datetime.datetime.strptime(t1.date, "%Y-%m-%d").date()
        ).days
        for t1, t2 in itertools.pairwise(same_transactions)
    ]
    try:
        return statistics.stdev(intervals)
    except statistics.StatisticsError:
        return 0.0


def get_days_since_last_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of days since the last transaction with the same merchant and amount"""
    same_transactions = [
        t
        for t in all_transactions
        if t.name == transaction.name and t.amount == transaction.amount and t.date < transaction.date
    ]
    if not same_transactions:
        return 0
    last_date = max(datetime.datetime.strptime(t.date, "%Y-%m-%d").date() for t in same_transactions)
    transaction_date = datetime.datetime.strptime(transaction.date, "%Y-%m-%d").date()
    return (transaction_date - last_date).days


def get_recurring_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> str:
    """Determine if the transaction is recurring daily, weekly, or monthly"""
    same_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount],
        key=lambda x: x.date,
    )
    if len(same_transactions) < 2:
        return "none"
    intervals = [
        (
            datetime.datetime.strptime(t2.date, "%Y-%m-%d").date()
            - datetime.datetime.strptime(t1.date, "%Y-%m-%d").date()
        ).days
        for t1, t2 in itertools.pairwise(same_transactions)
    ]
    if not intervals:
        return "none"
    avg_interval = sum(intervals) / len(intervals)
    if avg_interval <= 1:
        return "daily"
    elif avg_interval <= 7:
        return "weekly"
    elif avg_interval <= 30:
        return "monthly"
    else:
        return "none"


def get_is_always_recurring_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Determine if the transaction is always recurring"""
    same_transactions = [t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount]
    return len(same_transactions) > 1


def is_insurance_related(transaction: Transaction) -> bool:
    """Determine if the transaction is related to insurance"""
    insurance_keywords = {"insurance", "ins", "policy"}
    merchant_name = transaction.name.lower()
    return any(keyword in merchant_name for keyword in insurance_keywords)


def get_is_utility(transaction: Transaction) -> bool:
    """Determine if the transaction is related to utilities"""
    utility_keywords = {"utility", "utilities", "electric", "water", "gas", "power", "energy"}
    merchant_name = transaction.name.lower()
    return any(keyword in merchant_name for keyword in utility_keywords)


def get_is_phone(transaction: Transaction) -> bool:
    """Determine if the transaction is related to phone services"""
    merchant_name = transaction.name.lower()
    return ("at&t" in merchant_name) or ("t-mobile" in merchant_name) or ("verizon" in merchant_name)


def is_subscription_amount(transaction: Transaction) -> bool:
    """Check if the transaction amount is one of the common subscription amounts"""
    subscription_amounts = {0.99, 1.99, 2.99, 4.99, 9.99, 10.99, 11.99, 12.99, 14.99, 19.99}
    return round(transaction.amount, 2) in subscription_amounts


def get_additional_features(
    transaction: Transaction, all_transactions: list[Transaction]
) -> dict[str, float | int | bool]:
    """Extract additional temporal and merchant consistency features that are not already included."""
    trans_date = datetime.datetime.strptime(transaction.date, "%Y-%m-%d").date()
    day_of_week: int = trans_date.weekday()
    day_of_month: int = trans_date.day
    is_weekend: bool = day_of_week >= 5
    is_end_of_month: bool = day_of_month >= 28
    same_merchant_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name], key=lambda x: x.date
    )
    if same_merchant_transactions:
        first_date = datetime.datetime.strptime(same_merchant_transactions[0].date, "%Y-%m-%d").date()
        days_since_first: int = (trans_date - first_date).days
    else:
        days_since_first = 0
    intervals = []
    for t1, t2 in itertools.pairwise(same_merchant_transactions):
        d1 = datetime.datetime.strptime(t1.date, "%Y-%m-%d").date()
        d2 = datetime.datetime.strptime(t2.date, "%Y-%m-%d").date()
        intervals.append((d2 - d1).days)
    min_interval: int = min(intervals) if intervals else 0
    max_interval: int = max(intervals) if intervals else 0
    merchant_total_count: int = sum(1 for t in all_transactions if t.name == transaction.name)
    merchant_recent_count: int = sum(
        1
        for t in all_transactions
        if t.name == transaction.name
        and (trans_date - datetime.datetime.strptime(t.date, "%Y-%m-%d").date()).days <= 30
    )
    merchant_amounts = [t.amount for t in all_transactions if t.name == transaction.name]
    if merchant_amounts:
        amount_stddev: float = statistics.stdev(merchant_amounts) if len(merchant_amounts) > 1 else 0.0
        merchant_avg: float = statistics.mean(merchant_amounts)
    else:
        amount_stddev = 0.0
        merchant_avg = 0.0
    relative_amount_difference: float = (
        abs(transaction.amount - merchant_avg) / merchant_avg if merchant_avg != 0 else 0.0
    )
    return {
        "day_of_week": day_of_week,
        "day_of_month": day_of_month,
        "is_weekend": is_weekend,
        "is_end_of_month": is_end_of_month,
        "days_since_first_occurrence": days_since_first,
        "min_days_between": min_interval,
        "max_days_between": max_interval,
        "merchant_total_count": merchant_total_count,
        "merchant_recent_count": merchant_recent_count,
        "merchant_amount_stddev": amount_stddev,
        "relative_amount_difference": relative_amount_difference,
    }


# ------------------------- New Feature Functions for Detecting Amount Variations -------------------------


def get_amount_variation_features(
    transaction: Transaction, all_transactions: list[Transaction], threshold: float = 0.2
) -> dict[str, FeatureValue]:
    """
    Calculate features related to amount variations for a given transaction.
    """
    merchant_transactions = [t for t in all_transactions if t.name == transaction.name]
    merchant_avg = statistics.mean([t.amount for t in merchant_transactions]) if merchant_transactions else 0.0
    relative_diff = abs(transaction.amount - merchant_avg) / merchant_avg if merchant_avg != 0 else 0.0
    amount_anomaly = relative_diff > threshold
    return {
        "merchant_avg": merchant_avg,
        "relative_amount_diff": relative_diff,
        "amount_anomaly": amount_anomaly,
    }


# ------------------------- Combined Feature Extraction -------------------------


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, FeatureValue]:
    """Extract a comprehensive set of features for a given transaction"""
    features: dict[str, FeatureValue] = {
        # Basic transaction features
        "amount": transaction.amount,
        "amount_ends_in_99": amount_ends_in_99(transaction),
        "amount_ends_in_00": amount_ends_in_00(transaction),
        # Merchant recurring flags and frequencies
        "is_recurring_merchant": is_recurring_merchant(transaction),
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "n_transactions_same_merchant_amount": get_n_transactions_same_merchant_amount(transaction, all_transactions),
        "percent_transactions_same_merchant_amount": get_percent_transactions_same_merchant_amount(
            transaction, all_transactions
        ),
        # Temporal interval features for same merchant & amount
        "avg_days_between_same_merchant_amount": get_avg_days_between_same_merchant_amount(
            transaction, all_transactions
        ),
        "stddev_days_between_same_merchant_amount": get_stddev_days_between_same_merchant_amount(
            transaction, all_transactions
        ),
        "days_since_last_same_merchant_amount": get_days_since_last_same_merchant_amount(transaction, all_transactions),
        "recurring_frequency": get_recurring_frequency(transaction, all_transactions),
        # Other flags
        "is_insurance": get_is_insurance(transaction),
        "is_utility": get_is_utility(transaction),
        "is_phone": get_is_phone(transaction),
        "is_subscription_amount": is_subscription_amount(transaction),
    }
    # Merge in additional features and amount variation features
    features.update(get_additional_features(transaction, all_transactions))
    features.update(get_amount_variation_features(transaction, all_transactions))
    return features
