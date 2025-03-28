import re
from datetime import date, datetime
from functools import lru_cache

import numpy as np
import pandas as pd

from recur_scan.transactions import Transaction


def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring because of the vendor name."""
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
        "amazon prime",
        "disney+",
        "apple music",
        "xbox live",
        "playstation plus",
        "adobe",
        "microsoft 365",
        "audible",
        "dropbox",
        "zoom",
        "grammarly",
        "nordvpn",
        "expressvpn",
        "patreon",
        "onlyfans",
        "youtube premium",
        "apple tv",
        "hbo max",
        "paramount+",
        "peacock",
        "crunchyroll",
        "masterclass",
    }
    return transaction.name.lower() in always_recurring_vendors


def get_is_insurance(transaction: Transaction) -> bool:
    """Check if the transaction is an insurance payment."""
    match = re.search(
        r"\b(insurance|insur|insuranc|geico|allstate|progressive|state farm|liberty mutual)\b",
        transaction.name,
        re.IGNORECASE,
    )
    return bool(match)


def get_is_utility(transaction: Transaction) -> bool:
    """Check if the transaction is a utility payment."""
    match = re.search(
        r"\b(utility|utilit|energy|water|gas|electric|comcast|xfinity|verizon fios|at&t u-verse|spectrum)\b",
        transaction.name,
        re.IGNORECASE,
    )
    return bool(match)


def get_is_phone(transaction: Transaction) -> bool:
    """Check if the transaction is a phone payment."""
    match = re.search(
        r"\b(at&t|t-mobile|verizon|sprint|boost|cricket|metro pcs|straight talk)\b", transaction.name, re.IGNORECASE
    )
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
    """Get the number of transactions within n_days_off of being n_days_apart from transaction."""
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


def _get_day(date: str) -> int:
    """Get the day of the month from a transaction date."""
    return int(date.split("-")[2])


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    """Get the number of transactions on the same day of the month as transaction."""
    return len([t for t in all_transactions if abs(_get_day(t.date) - _get_day(transaction.date)) <= n_days_off])


def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in 99 (common for subscriptions)."""
    return (transaction.amount * 100) % 100 == 99


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions with the same amount as transaction."""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions with the same amount as transaction."""
    if not all_transactions:
        return 0.0
    n_same_amount = get_n_transactions_same_amount(transaction, all_transactions)
    return n_same_amount / len(all_transactions)


def get_days_between_std(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the standard deviation of days between transactions for this user_id and name."""
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name]
    if len(user_transactions) < 2:
        return 100.0
    dates = sorted([_parse_date(t.date) for t in user_transactions])
    diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    std = float(np.std(diffs) if diffs else 100.0)
    return min(std, 100.0)


def get_amount_cv(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the coefficient of variation of amounts for this user_id and name."""
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name]
    if not user_transactions:
        return 1.0
    amounts = [t.amount for t in user_transactions]
    mean = np.mean(amounts)
    cv = float(np.std(amounts) / mean if mean > 0 else 1.0)
    return min(cv, 10.0)


# Duplicate function removed to resolve the conflict.


def get_has_recurring_keyword(transaction: Transaction) -> int:
    """Check if the transaction name contains recurring-related keywords using regex."""
    recurring_keywords = (
        r"\b(sub|membership|renewal|monthly|annual|premium|bill|plan|fee|auto|pay|service|"
        r"recurring|subscription|auto-renew|recurr|autopay|rec|month|year|quarterly|weekly|due)\b"
    )
    return int(bool(re.search(recurring_keywords, transaction.name, re.IGNORECASE)))


def get_is_convenience_store(transaction: Transaction) -> int:
    """Check if the transaction is at a convenience store using regex."""
    return int(
        bool(
            re.search(
                r"\b(7-eleven|cvs|walgreens|rite aid|circle k|quiktrip|speedway|ampm|"
                r"7 eleven|seven eleven|sheetz)\b",
                transaction.name,
                re.IGNORECASE,
            )
        )
    )


def get_pct_transactions_days_apart(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> float:
    """Get the percentage of transactions within n_days_off of being n_days_apart from transaction."""
    if not all_transactions:
        return 0.0
    n_txs = get_n_transactions_days_apart(transaction, all_transactions, n_days_apart, n_days_off)
    return n_txs / len(all_transactions)


def get_pct_transactions_same_day(
    transaction: Transaction, all_transactions: list[Transaction], n_days_off: int
) -> float:
    """Get the percentage of transactions on the same day of the month as transaction."""
    if not all_transactions:
        return 0.0
    n_txs = get_n_transactions_same_day(transaction, all_transactions, n_days_off)
    return n_txs / len(all_transactions)


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    """Return a feature dictionary for the transaction."""
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "days_between_std": get_days_between_std(transaction, all_transactions),
        "amount_cv": get_amount_cv(transaction, all_transactions),
        "day_of_month_consistency": get_day_of_month_consistency(transaction, all_transactions),
        "exact_amount_count": get_exact_amount_count(transaction, all_transactions),
        "has_recurring_keyword": get_has_recurring_keyword(transaction),
        "is_always_recurring": int(get_is_always_recurring(transaction)),
        "n_transactions_30_days_apart": get_n_transactions_days_apart(transaction, all_transactions, 30, 2),
        "is_convenience_store": get_is_convenience_store(transaction),
        "ends_in_99": int(get_ends_in_99(transaction)),
        "is_insurance": int(get_is_insurance(transaction)),
        "is_utility": int(get_is_utility(transaction)),
        "is_phone": int(get_is_phone(transaction)),
    }


def get_day_of_month_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate entropy of day-of-month distribution for this user_id and name (low = consistent)."""
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name]
    if not user_transactions:
        return 1.0
    days = [int(t.date.split("-")[2]) for t in user_transactions]
    value_counts = pd.Series(days).value_counts(normalize=True)
    entropy = -sum(p * np.log2(p + 1e-10) for p in value_counts)
    return float(entropy / np.log2(31))


def get_exact_amount_count(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Count transactions with the exact same amount for this user_id and name."""
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name]
    return sum(1 for t in user_transactions if t.amount == transaction.amount)
