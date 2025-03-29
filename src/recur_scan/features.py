import re
from datetime import datetime

from recur_scan.transactions import Transaction


def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring because of the vendor name - check lowercase match"""
    always_recurring_vendors = {"google storage", "netflix", "hulu", "spotify"}
    return transaction.name.lower() in always_recurring_vendors


def get_is_insurance(transaction: Transaction) -> bool:
    """Check if the transaction is an insurance payment."""
    match = re.search(r"\b(insurance|insur|insuranc)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_utility(transaction: Transaction) -> bool:
    """Check if the transaction is a utility payment."""
    match = re.search(r"\b(utility|utilit|energy)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_phone(transaction: Transaction) -> bool:
    """Check if the transaction is a phone payment."""
    match = re.search(r"\b(at&t|t-mobile|verizon)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def _get_days(date: str) -> int:
    """Get the number of days since the epoch of a transaction date."""
    return (datetime.strptime(date, "%Y-%m-%d") - datetime(1970, 1, 1)).days


def get_n_transactions_days_apart(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> int:
    """Get the number of transactions within n_days_off of being n_days_apart from transaction."""
    n_txs = 0
    transaction_days = _get_days(transaction.date)
    for t in all_transactions:
        t_days = _get_days(t.date)
        days_diff = abs(t_days - transaction_days)
        if days_diff < n_days_apart - n_days_off:
            continue
        remainder = days_diff % n_days_apart
        if remainder <= n_days_off or (n_days_apart - remainder) <= n_days_off:
            n_txs += 1
    return n_txs


def _get_day(date: str) -> int:
    """Get the day of the month from a transaction date."""
    return int(date.split("-")[2])


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    """Get the number of transactions on the same day of the month as transaction."""
    return len([t for t in all_transactions if abs(_get_day(t.date) - _get_day(transaction.date)) <= n_days_off])


def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in 99."""
    return (transaction.amount * 100) % 100 == 99


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions with the same amount as transaction."""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions with the same amount as transaction."""
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions)


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    features: dict[str, float | int] = {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "ends_in_99": int(get_ends_in_99(transaction)),
        "amount": transaction.amount,
        "same_day_exact": get_n_transactions_same_day(transaction, all_transactions, 0),
        "same_day_off_by_1": get_n_transactions_same_day(transaction, all_transactions, 1),
        "same_day_off_by_2": get_n_transactions_same_day(transaction, all_transactions, 2),
        "14_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 14, 0),
        "14_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 14, 1),
        "7_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 7, 0),
        "7_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 7, 1),
        "is_insurance": int(get_is_insurance(transaction)),
        "is_utility": int(get_is_utility(transaction)),
        "is_phone": int(get_is_phone(transaction)),
        "is_always_recurring": int(get_is_always_recurring(transaction)),
    }
    dates = sorted([t.date for t in all_transactions])
    if len(dates) > 1:
        deltas = [
            (datetime.strptime(dates[i + 1], "%Y-%m-%d") - datetime.strptime(dates[i], "%Y-%m-%d")).days
            for i in range(len(dates) - 1)
        ]
        features["avg_days_between"] = sum(deltas) / len(deltas)  # Ensured as float
    else:
        features["avg_days_between"] = 0.0  # Explicit float
    return features


# Optional functions (not used in 30_train.py but kept for completeness)
def call_features(transaction: dict, group: list) -> dict[str, float]:
    features: dict[str, float] = {}
    features["amount"] = transaction["amount"]
    features["frequency"] = len(group)
    dates = sorted([t.date for t in group])
    if len(dates) > 1:
        deltas = [
            (datetime.strptime(dates[i + 1], "%Y-%m-%d") - datetime.strptime(dates[i], "%Y-%m-%d")).days
            for i in range(len(dates) - 1)
        ]
        features["avg_days_between"] = sum(deltas) / len(deltas)
        features["std_days_between"] = (
            sum((d - features["avg_days_between"]) ** 2 for d in deltas) / len(deltas)
        ) ** 0.5
    else:
        features["avg_days_between"] = 0
        features["std_days_between"] = 0
    return features


def get_newfeatures(transaction: Transaction, group: list[Transaction]) -> dict[str, float]:
    features: dict[str, float] = {}
    features["amount"] = transaction.amount
    features["n_transactions_same_amount"] = sum(1 for t in group if t.amount == transaction.amount)
    features["percent_transactions_same_amount"] = features["n_transactions_same_amount"] / len(group)
    dates = sorted([t.date for t in group])
    if len(dates) > 1:
        deltas = [
            (datetime.strptime(dates[i + 1], "%Y-%m-%d") - datetime.strptime(dates[i], "%Y-%m-%d")).days
            for i in range(len(dates) - 1)
        ]
        features["avg_days_between"] = sum(deltas) / len(deltas)
        features["std_days_between"] = (
            sum((d - features["avg_days_between"]) ** 2 for d in deltas) / len(deltas)
        ) ** 0.5
        features["min_days_between"] = min(deltas)
        features["max_days_between"] = max(deltas)
    else:
        features["avg_days_between"] = 0
        features["std_days_between"] = 0
        features["min_days_between"] = 0
        features["max_days_between"] = 0
    return features
