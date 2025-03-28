import re
from datetime import date, datetime
from functools import lru_cache

import numpy as np

from recur_scan.transactions import Transaction


def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring because of the vendor name - check lowercase match"""
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
        "amazon prime",
        "apple music",
        "microsoft 365",
        "dropbox",
        "adobe creative cloud",
        "discord nitro",
        "zoom subscription",
        "patreon",
        "new york times",
        "wall street journal",
        "github copilot",
        "notion",
        "evernote",
        "expressvpn",
        "nordvpn",
        "youtube premium",
        "linkedin premium",
        "at&t",
        "afterpay",
        "amazon+",
        "walmart+",
        "amazonprime",
        "t-mobile",
        "duke energy",
        "adobe",
        "charter comm",
        "boostmobile",
        "verizon",
        "disney+",
    }
    return transaction.name.lower() in always_recurring_vendors


def get_is_insurance(transaction: Transaction) -> bool:
    match = re.search(r"\b(insurance|insur|insuranc)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_utility(transaction: Transaction) -> bool:
    match = re.search(r"\b(utility|utilit|energy)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_phone(transaction: Transaction) -> bool:
    match = re.search(r"\b(at&t|t-mobile|verizon)\b", transaction.name, re.IGNORECASE)
    return bool(match)


@lru_cache(maxsize=1024)
def _parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def get_n_transactions_days_apart(
    transaction: Transaction, all_transactions: list[Transaction], n_days_apart: int, n_days_off: int
) -> int:
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


def _get_day(date: str) -> int:
    return int(date.split("-")[2])


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    return len([t for t in all_transactions if abs(_get_day(t.date) - _get_day(transaction.date)) <= n_days_off])


def get_pct_transactions_same_day(
    transaction: Transaction, all_transactions: list[Transaction], n_days_off: int
) -> float:
    return get_n_transactions_same_day(transaction, all_transactions, n_days_off) / len(all_transactions)


def get_ends_in_99(transaction: Transaction) -> bool:
    return (transaction.amount * 100) % 100 == 99


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions)


def get_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    return sum(1 for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip())


def get_amount_std_dev(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    amounts = [t.amount for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()]
    return float(np.std(amounts, ddof=0)) if amounts else 0.0


def get_median_transaction_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    amounts = [t.amount for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()]
    return float(np.median(amounts)) if amounts else 0.0


def get_is_weekend_transaction(transaction: Transaction) -> bool:
    return _parse_date(transaction.date).weekday() >= 5


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
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
        "is_always_recurring": get_is_always_recurring(transaction),
        "transaction_frequency": get_transaction_frequency(transaction, all_transactions),
        "amount_std_dev": get_amount_std_dev(transaction, all_transactions),
        "median_transaction_amount": get_median_transaction_amount(transaction, all_transactions),
        "is_weekend_transaction": get_is_weekend_transaction(transaction),
    }
