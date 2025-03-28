import itertools
import re
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from functools import lru_cache
from itertools import pairwise

from recur_scan.transactions import Transaction


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
    # use a regular expression with boundaries to match case-insensitive insurance
    # and insurance-related terms
    match = re.search(r"\b(insurance|insur|insuranc)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_utility(transaction: Transaction) -> bool:
    """Check if the transaction is a utility payment."""
    # use a regular expression with boundaries to match case-insensitive utility
    # and utility-related terms
    match = re.search(r"\b(utility|utilit|energy)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_phone(transaction: Transaction) -> bool:
    """Check if the transaction is a phone payment."""
    # use a regular expression with boundaries to match case-insensitive phone
    # and phone-related terms
    match = re.search(r"\b(at&t|t-mobile|verizon)\b", transaction.name, re.IGNORECASE)
    return bool(match)


@lru_cache(maxsize=1024)
def _parse_date(date_str: str) -> date:
    """Parse a date string into a datetime.date object."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


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

    # Pre-calculate bounds for faster checking
    lower_remainder = n_days_apart - n_days_off
    upper_remainder = n_days_off

    for t in all_transactions:
        t_date = _parse_date(t.date)
        days_diff = abs((t_date - transaction_date).days)

        # Skip if the difference is less than minimum required
        if days_diff < n_days_apart - n_days_off:
            continue

        # Check if the difference is close to any multiple of n_days_apart
        remainder = days_diff % n_days_apart

        if remainder <= upper_remainder or remainder >= lower_remainder:
            n_txs += 1

    return n_txs


def get_pct_transactions_days_apart(
    transaction: Transaction, all_transactions: list[Transaction], n_days_apart: int, n_days_off: int
) -> float:
    """
    Get the percentage of transactions in all_transactions that are within
    n_days_off of being n_days_apart from transaction
    """
    return get_n_transactions_days_apart(transaction, all_transactions, n_days_apart, n_days_off) / len(
        all_transactions
    )


def _get_day(date: str) -> int:
    """Get the day of the month from a transaction date."""
    return int(date.split("-")[2])


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    """Get the number of transactions in all_transactions that are on the same day of the month as transaction"""
    return len([t for t in all_transactions if abs(_get_day(t.date) - _get_day(transaction.date)) <= n_days_off])


def get_pct_transactions_same_day(
    transaction: Transaction, all_transactions: list[Transaction], n_days_off: int
) -> float:
    """Get the percentage of transactions in all_transactions that are on the same day of the month as transaction"""
    return get_n_transactions_same_day(transaction, all_transactions, n_days_off) / len(all_transactions)


def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in 99"""
    return (transaction.amount * 100) % 100 == 99


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    return sum(1 for t in all_transactions if t.amount == transaction.amount)


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    return get_n_transactions_same_amount(transaction, all_transactions) / len(all_transactions)


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
        matches = re.findall(r"(?:ref|id|no)[-:]\s*([a-zA-Z0-9]+)", t.name.lower())
        if matches:
            ref_codes.extend(matches)

    # Check if the same reference code appears multiple times
    if ref_codes:
        counter = Counter(ref_codes)
        # If any reference code appears multiple times, it's likely not a unique transaction
        return any(count > 1 for count in counter.values())

    return False


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int | bool]:
    return {
        "amount": transaction.amount,
        "is_recurring_merchant": is_recurring_merchant(transaction),
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "avg_days_between_same_merchant_amount": get_avg_days_between_same_merchant_amount(
            transaction, all_transactions
        ),
        "average_transaction_amount": get_average_transaction_amount(all_transactions),
        "max_transaction_amount": get_max_transaction_amount(all_transactions),
        "min_transaction_amount": get_min_transaction_amount(all_transactions),
        "most_frequent_names": len(get_most_frequent_names(all_transactions)),
        "is_recurring": is_recurring(transaction, all_transactions),
        "amount_ends_in_99": amount_ends_in_99(transaction),
        "amount_ends_in_00": amount_ends_in_00(transaction),
        "n_transactions_same_merchant_amount": get_n_transactions_same_merchant_amount(transaction, all_transactions),
        "percent_transactions_same_merchant_amount": get_percent_transactions_same_merchant_amount(
            transaction, all_transactions
        ),
        "interval_variance_coefficient": get_interval_variance_coefficient(transaction, all_transactions),
        "stddev_days_between_same_merchant_amount": get_stddev_days_between_same_merchant_amount(
            transaction, all_transactions
        ),
        "days_since_last_same_merchant_amount": get_days_since_last_same_merchant_amount(transaction, all_transactions),
        "is_expected_transaction_date": is_expected_transaction_date(transaction, all_transactions),
        "has_incrementing_numbers": has_incrementing_numbers(transaction, all_transactions),
        "has_consistent_reference_codes": has_consistent_reference_codes(transaction, all_transactions),
        "is_always_recurring": get_is_always_recurring(transaction),
        "ends_in_99": get_ends_in_99(transaction),
        "amount": transaction.amount,
        "same_day_exact": get_n_transactions_same_day(transaction, all_transactions, 0),
        "pct_transactions_same_day": get_pct_transactions_same_day(transaction, all_transactions, 0),
        "same_day_off_by_1": get_n_transactions_same_day(transaction, all_transactions, 1),
        "same_day_off_by_2": get_n_transactions_same_day(transaction, all_transactions, 2),
        "14_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 14, 0),
        "pct_14_days_apart_exact": get_pct_transactions_days_apart(transaction, all_transactions, 14, 0),
        "14_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 14, 1),
        "pct_14_days_apart_off_by_1": get_pct_transactions_days_apart(transaction, all_transactions, 14, 1),
        "7_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 7, 0),
        "pct_7_days_apart_exact": get_pct_transactions_days_apart(transaction, all_transactions, 7, 0),
        "7_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 7, 1),
        "pct_7_days_apart_off_by_1": get_pct_transactions_days_apart(transaction, all_transactions, 7, 1),
        "is_insurance": get_is_insurance(transaction),
        "is_utility": get_is_utility(transaction),
        "is_phone": get_is_phone(transaction),
        "ends_in_99": get_ends_in_99(transaction),
    }
