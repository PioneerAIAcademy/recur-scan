import difflib
from datetime import datetime

from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date


# ===== ORIGINAL FUNCTIONS (KEPT IN PLACE) =====
def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    transaction_day = transaction_date.day

    count = 0
    for t in all_transactions:
        if t.name == transaction.name:  # Only consider transactions with same name
            t_date = datetime.strptime(t.date, "%Y-%m-%d")
            # Check if day of month is within tolerance, accounting for month boundaries
            day_diff = abs(t_date.day - transaction_day)
            if day_diff <= n_days_off:
                count += 1
            # Special case for month boundaries (e.g., Jan 31 and Feb 1 with n_days_off=1)
            elif (transaction_day > 28 and t_date.day < 3) or (transaction_day < 3 and t_date.day > 28):
                month_diff = abs((t_date.month - transaction_date.month) % 12)
                if month_diff == 1 and (31 - transaction_day + t_date.day) <= n_days_off:
                    count += 1

    return count


def get_n_transactions_days_apart(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> int:
    """
    Get the number of transactions in all_transactions that are within n_days_off of
    being n_days_apart from transaction.
    """
    transaction_date = parse_date(transaction.date)
    count = 0

    for t in all_transactions:
        days_difference = abs((parse_date(t.date) - transaction_date).days)
        if abs(days_difference - n_days_apart) <= n_days_off:
            count += 1

    return count


def get_pct_transactions_days_apart(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> float:
    """
    Get the percentage of transactions in all_transactions that are within n_days_off
    of being n_days_apart from transaction.
    """
    if not all_transactions:
        return 0.0

    n_transactions = get_n_transactions_days_apart(transaction, all_transactions, n_days_apart, n_days_off)
    return float(n_transactions) / float(len(all_transactions))


def get_pct_transactions_same_day(
    transaction: Transaction, all_transactions: list[Transaction], n_days_off: int
) -> float:
    """
    Get the percentage of transactions in all_transactions that are on the same day of the month as transaction.
    """
    if not all_transactions:
        return 0.0

    n_same_day = get_n_transactions_same_day(transaction, all_transactions, n_days_off)
    return float(n_same_day) / float(len(all_transactions))


def get_is_common_subscription_amount(transaction: Transaction) -> bool:
    common_amounts = {4.99, 5.99, 9.99, 12.99, 14.99, 15.99, 19.99, 49.99, 99.99}
    return transaction.amount in common_amounts


def get_occurs_same_week(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """Checks if the transaction occurs in the same week of the month across multiple months."""
    transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    transaction_week = transaction_date.day // 7  # Determine which week in the month (0-4)

    same_week_count = sum(
        1
        for t in transactions
        if t.name == transaction.name and datetime.strptime(t.date, "%Y-%m-%d").day // 7 == transaction_week
    )

    return same_week_count >= 2  # True if found at least twice


def get_is_similar_name(
    transaction: Transaction, transactions: list[Transaction], similarity_threshold: float = 0.6
) -> bool:
    """Checks if a transaction has a similar name to other past transactions."""
    for t in transactions:
        similarity = difflib.SequenceMatcher(None, transaction.name.lower(), t.name.lower()).ratio()
        if similarity >= similarity_threshold:
            return True  # If a close match is found, return True
    return False


def get_is_fixed_interval(transaction: Transaction, transactions: list[Transaction], margin: int = 1) -> bool:
    """Returns True if a transaction recurs at fixed intervals (weekly, bi-weekly, monthly)."""
    transaction_dates = sorted([
        datetime.strptime(t.date, "%Y-%m-%d") for t in transactions if t.name == transaction.name
    ])

    if len(transaction_dates) < 2:
        return False  # Not enough transactions to determine intervals

    intervals = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    return all(abs(interval - 30) <= margin for interval in intervals)  # Allow ±1 day for monthly intervals


def get_has_irregular_spike(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """
    Check if the transaction amount is significantly higher than the average amount
    for the same transaction name in the user's transaction history.
    """
    similar_transactions = [t for t in transactions if t.name == transaction.name]
    if not similar_transactions:
        return False

    average_amount = sum(t.amount for t in similar_transactions) / len(similar_transactions)
    return transaction.amount > average_amount * 1.5  # Spike threshold: 50% higher than average


def get_is_first_of_month(transaction: Transaction) -> bool:
    """
    Checks if a transaction occurs on the first day of the month.
    """
    return transaction.date.split("-")[2] == "01"


# ===== NEW FEATURES ADDED BELOW =====
def get_is_weekday_consistent(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """Check if transaction consistently occurs on the same weekday"""
    same_name_txns = [t for t in transactions if t.name == transaction.name]
    if len(same_name_txns) < 2:
        return False

    transaction_weekday = datetime.strptime(transaction.date, "%Y-%m-%d").weekday()
    return all(
        datetime.strptime(t.date, "%Y-%m-%d").weekday() == transaction_weekday for t in same_name_txns[-3:]
    )  # Check last 3 occurrences


def get_is_seasonal(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """Detect seasonal/annual payments"""
    same_name_txns = [t for t in transactions if t.name == transaction.name]
    if len(same_name_txns) < 2:
        return False

    dates = [datetime.strptime(t.date, "%Y-%m-%d") for t in same_name_txns]
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    return all(360 <= interval <= 370 for interval in intervals)


def get_amount_variation(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Calculate coefficient of variation for amounts."""
    same_name_txns = [t for t in transactions if t.name == transaction.name]
    if len(same_name_txns) < 2:
        return 0.0

    amounts = [t.amount for t in same_name_txns]
    mean = sum(amounts) / len(amounts)
    std_dev = (sum((x - mean) ** 2 for x in amounts) / len(amounts)) ** 0.5
    return float((std_dev / mean) * 100) if mean != 0 else 0.0


def get_has_trial_period(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """Detect potential free trial periods"""
    same_name_txns = sorted([t for t in transactions if t.name == transaction.name], key=lambda x: x.date)
    return len(same_name_txns) >= 2 and same_name_txns[0].amount == 0 and all(t.amount > 0 for t in same_name_txns[1:])


def get_description_pattern(transaction: Transaction) -> str:
    """Extract payment pattern from description"""
    desc = transaction.name.lower()
    patterns = {
        "ach": "ach" in desc,
        "auto": "auto" in desc or "autopay" in desc,
        "recurring": "recur" in desc,
        "invoice": "inv" in desc or "invoice" in desc,
    }
    return next((k for k, v in patterns.items() if v), "other")


def get_is_weekend_transaction(transaction: Transaction) -> bool:
    """Check if transaction occurs on weekend"""
    return datetime.strptime(transaction.date, "%Y-%m-%d").weekday() >= 5


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict:
    """
    Return a dictionary containing only the new features for the given transaction.
    """
    return {
        # New features
        "is_weekday_consistent": get_is_weekday_consistent(transaction, all_transactions),
        "is_seasonal": get_is_seasonal(transaction, all_transactions),
        "amount_variation_pct": get_amount_variation(transaction, all_transactions),
        "had_trial_period": get_has_trial_period(transaction, all_transactions),
        "description_pattern": get_description_pattern(transaction),
        "is_weekend_transaction": get_is_weekend_transaction(transaction),
        "n_days_apart_30": get_n_transactions_days_apart(transaction, all_transactions, 30, 2),
        "pct_days_apart_30": get_pct_transactions_days_apart(transaction, all_transactions, 30, 2),
    }
