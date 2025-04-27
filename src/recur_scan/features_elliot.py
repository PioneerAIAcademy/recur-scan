import re
import statistics
from collections import defaultdict
from datetime import datetime
from typing import cast

import dateutil.parser as _du_parser  # type: ignore
import numpy as np
import pandas as pd
from scipy.stats import iqr  # type: ignore
from thefuzz import fuzz  # type: ignore

from recur_scan.transactions import Transaction


def parse_date(date_str: str) -> datetime:
    """Parse a string into a datetime object."""
    # Cast so mypy knows it's a datetime, not Any
    return cast(datetime, _du_parser.parse(date_str))


def get_is_near_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if a transaction has a recurring amount within 5% of another transaction."""
    return any(
        t != transaction and abs(transaction.amount - t.amount) / max(t.amount, 0.01) <= 0.05 for t in all_transactions
    )


def is_utility_bill(transaction: Transaction) -> bool:
    """Check if the transaction is a utility bill (water, gas, electricity, etc.)."""
    utility_keywords = (
        r"\b(water|gas|electricity|power|energy|utility|sewage|trash|waste|heating|cable|internet|broadband|tv)\b"
    )
    utility_providers = {
        "duke energy",
        "pg&e",
        "con edison",
        "national grid",
        "xcel energy",
        "southern california edison",
        "dominion energy",
        "centerpoint energy",
        "peoples gas",
        "nrg energy",
        "direct energy",
        "atmos energy",
        "comcast",
        "xfinity",
        "spectrum",
        "verizon fios",
        "centurylink",
        "at&t",
        "cox communications",
    }
    name_lower = transaction.name.lower()
    return bool(re.search(utility_keywords, name_lower, re.IGNORECASE)) or any(
        provider in name_lower for provider in utility_providers
    )


def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring using fuzzy matching."""
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
        "apple music",
        "apple arcade",
        "apple tv+",
        "apple fitness+",
        "apple icloud",
        "apple one",
        "amazon prime",
        "adobe creative cloud",
        "microsoft 365",
        "dropbox",
        "youtube premium",
        "discord nitro",
        "playstation plus",
        "xbox game pass",
        "comcast xfinity",
        "spectrum",
        "verizon fios",
        "centurylink",
        "cox communications",
        "at&t internet",
        "t-mobile home internet",
    }
    return any(fuzz.partial_ratio(transaction.name.lower(), vendor) > 85 for vendor in always_recurring_vendors)


def is_auto_pay(transaction: Transaction) -> bool:
    """Check if the transaction is an automatic recurring payment."""
    return bool(re.search(r"\b(auto\s?pay|autopayment|automatic payment)\b", transaction.name, re.IGNORECASE))


def is_membership(transaction: Transaction) -> bool:
    """Check if the transaction is a membership payment."""
    membership_keywords = r"\b(membership|subscription|club|gym|association|society)\b"
    return bool(re.search(membership_keywords, transaction.name, re.IGNORECASE))


def is_recurring_based_on_99(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if a transaction is recurring based on:
    - Amount ending in .99
    - >= 3 occurrences
    - 7, 14, 30, or 60-day intervals
    """
    if (transaction.amount * 100) % 100 != 99:
        return False

    vendor = transaction.name.lower()
    date_occurrences = defaultdict(list)
    for t in all_transactions:
        if t.name.lower() == vendor and (t.amount * 100) % 100 == 99:
            days = (parse_date(t.date) - datetime(1970, 1, 1)).days
            date_occurrences[vendor].append(days)

    dates = sorted(date_occurrences[vendor])
    if len(dates) < 3:
        return False

    count = 1
    for i in range(1, len(dates)):
        diff = dates[i] - dates[i - 1]
        if diff in {7, 14, 30, 60}:
            count += 1
            if count >= 3:
                return True
        else:
            count = 1
    return False


def get_transaction_similarity(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Compute the average fuzzy similarity of this transaction's name to others."""
    scores = [
        fuzz.partial_ratio(transaction.name.lower(), t.name.lower()) for t in all_transactions if t.id != transaction.id
    ]
    return float(sum(scores)) / float(len(scores)) if scores else 0.0


def is_weekday_transaction(transaction: Transaction) -> bool:
    """Return True if the transaction happened on a weekday (Mon-Fri)."""
    return datetime.strptime(transaction.date, "%Y-%m-%d").weekday() < 5


def is_price_trending(transaction: Transaction, all_transactions: list[Transaction], threshold: int) -> bool:
    """Check if a transaction's amount trends within a threshold percentage."""
    amounts = [t.amount for t in all_transactions if t.name == transaction.name]
    if len(amounts) < 3:
        return False
    diffs = [abs(amounts[i] - amounts[i - 1]) for i in range(1, len(amounts))]
    avg_change = sum(diffs) / len(diffs)
    return avg_change <= (transaction.amount * threshold / 100)


def is_split_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Detect if a transaction is part of a split payment (2+ smaller pieces)."""
    related = [t for t in all_transactions if t.name == transaction.name and t.amount < transaction.amount]
    return len(related) >= 2


# —————————————————————————————————————
#        ADVANCED, VECTORISED FEATURES
# —————————————————————————————————————


def get_time_regularity_score(txn: dict, txns: list[dict]) -> float:
    """Regularity of time intervals for a vendor's transactions."""
    same = [t for t in txns if t["name"] == txn["name"]]
    if len(same) <= 2:
        return 0.0
    try:
        dates = sorted(parse_date(t["date"]) for t in same)
        intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
        if len(intervals) <= 1:
            return 0.0
        stddev = statistics.stdev(intervals)
        return 1.0 / (1.0 + stddev / 5.0)
    except Exception:
        return 0.0


def get_transaction_amount_variance(txn: dict, txns: list[dict]) -> float:
    """Std deviation of amounts for a vendor."""
    vals = [t["amount"] for t in txns if t["name"] == txn["name"]]
    if len(vals) <= 1:
        return 0.0
    return float(statistics.stdev(vals))


def most_common_interval(df: pd.DataFrame) -> int:
    """Mode of day-diffs between sorted dates."""
    df2 = df.copy()
    df2["date"] = pd.to_datetime(df2["date"])
    df2 = df2.sort_values("date")
    diffs = df2["date"].diff().dt.days.dropna()
    return int(diffs.mode()[0]) if not diffs.empty else 0


def amount_variability_ratio(df: pd.DataFrame) -> float:
    """IQR / median of 'amount' column."""
    med = float(np.median(df["amount"]))
    return float(iqr(df["amount"])) / med if med != 0 else 0.0


def amount_similarity(df: pd.DataFrame, tolerance: float = 0.1) -> float:
    """Fraction of amounts within +/-tolerance of the mean."""
    mean_amt = float(np.mean(df["amount"]))
    mask = np.abs(df["amount"] - mean_amt) < tolerance * mean_amt
    return float(mask.mean()) if len(df) else 0.0


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int | bool]:
    """Aggregate selected engineered features for model training."""

    txns_dicts = [{"amount": t.amount, "date": t.date, "merchant": t.name} for t in all_transactions]
    df = pd.DataFrame(txns_dicts)

    return {
        "time_regularity_score": get_time_regularity_score(
            {"name": transaction.name, "date": transaction.date, "amount": transaction.amount},
            [{"name": t.name, "date": t.date, "amount": t.amount} for t in all_transactions],
        ),
        "transaction_amount_variance": get_transaction_amount_variance(
            {"name": transaction.name, "date": transaction.date, "amount": transaction.amount},
            [{"name": t.name, "date": t.date, "amount": t.amount} for t in all_transactions],
        ),
        "amount_variability_ratio": amount_variability_ratio(df),
        "most_common_interval": most_common_interval(df),
        "amount_similarity": amount_similarity(df),
    }
