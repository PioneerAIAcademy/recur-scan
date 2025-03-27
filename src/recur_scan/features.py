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


# Refined Features
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


def get_has_recurring_keyword(transaction: Transaction) -> int:
    """Check if the transaction name contains recurring-related keywords using regex."""
    recurring_keywords = (
        r"\b(sub|membership|renewal|monthly|annual|premium|bill|plan|fee|auto|pay|service|recurring|"
        r"subscription|auto-renew|recurr|autopay|rec|month|year|quarterly|weekly)\b"
    )
    return int(bool(re.search(recurring_keywords, transaction.name, re.IGNORECASE)))


def get_is_convenience_store(transaction: Transaction) -> int:
    """Check if the transaction is at a convenience store using regex."""
    convenience_stores = (
        r"\b(7-eleven|cvs|walgreens|rite aid|circle k|quiktrip|speedway|ampm|7 eleven|seven eleven|sheetz|wawa)\b"
    )
    return int(bool(re.search(convenience_stores, transaction.name, re.IGNORECASE)))


def get_amount_date_cluster_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Score how tightly amounts and dates cluster (high = recurring)."""
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name]
    if len(user_transactions) < 3:
        return 0.0
    amounts = [t.amount for t in user_transactions]
    dates = [(_parse_date(t.date) - _parse_date(user_transactions[0].date)).days for t in user_transactions]
    amount_std = float(np.std(amounts))
    date_std = float(np.std([dates[i + 1] - dates[i] for i in range(len(dates) - 1)] if len(dates) > 1 else 100.0))
    score = 1.0 / (1.0 + 0.1 * amount_std + 3.0 * date_std)  # Reduce date_std weight slightly
    return float(min(score, 1.0))


def get_transaction_frequency_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Score the frequency of transactions for this user_id and name."""
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name]
    if len(user_transactions) < 2:
        return 0.0
    dates = sorted([_parse_date(t.date) for t in user_transactions])
    total_days = (dates[-1] - dates[0]).days
    if total_days == 0:
        return 0.0
    frequency = len(user_transactions) / total_days
    return float(min(frequency * 100, 1.0))


def get_is_transactional_merchant(transaction: Transaction) -> int:
    """Check if the merchant is typically transactional using regex."""
    transactional_merchants = (
        r"\b(7-eleven|cvs|walgreens|rite aid|circle k|quiktrip|speedway|ampm|7 eleven|seven eleven|walmart|"
        r"target|costco|safeway|kroger|starbucks|mcdonalds|chipotle|whole foods|trader joe's|albertsons|"
        r"publix|dunkin|taco bell|wendys|sheetz|wawa|ralphs|vons)\b"
    )
    return int(bool(re.search(transactional_merchants, transaction.name, re.IGNORECASE)))


def get_is_subscription_merchant(transaction: Transaction) -> int:
    """Check if the merchant is typically subscription-based using regex."""
    subscription_merchants = (
        r"\b(netflix|hulu|spotify|amazon prime|disney\+|apple music|xbox live|playstation plus|adobe|"
        r"microsoft 365|audible|dropbox|zoom|grammarly|nordvpn|expressvpn|patreon|onlyfans|youtube premium|"
        r"apple tv|hbo max|paramount\+|peacock|crunchyroll|masterclass)\b"
    )
    return int(bool(re.search(subscription_merchants, transaction.name, re.IGNORECASE)))


def get_amount_roundness_score(transaction: Transaction) -> float:
    """Score how 'round' the amount is (e.g., $10.00 vs. $10.53). Recurring often have round amounts."""
    cents = (transaction.amount * 100) % 100
    if cents == 0 or cents == 99:  # $10.00 or $9.99
        return 1.0
    return 1.0 - (cents / 100.0)  # Closer to 0 or 99 → higher score


def get_timing_consistency_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Score the consistency of transaction timing intervals (high = recurring)."""
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name]
    if len(user_transactions) < 3:
        return 0.0
    dates = sorted([_parse_date(t.date) for t in user_transactions])
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    if not intervals:
        return 0.0
    mean_interval = np.mean(intervals)
    consistency = 1.0 / (1.0 + np.std(intervals) / (mean_interval + 1e-10))  # High if intervals are consistent
    return float(min(float(consistency), 1.0))


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
        "amount_date_cluster_score": get_amount_date_cluster_score(transaction, all_transactions),
        "transaction_frequency_score": get_transaction_frequency_score(transaction, all_transactions),
        "ends_in_99": int(get_ends_in_99(transaction)),
        "is_transactional_merchant": get_is_transactional_merchant(transaction),
        "is_subscription_merchant": get_is_subscription_merchant(transaction),
        "amount_roundness_score": get_amount_roundness_score(transaction),
        "timing_consistency_score": get_timing_consistency_score(transaction, all_transactions),
    }
