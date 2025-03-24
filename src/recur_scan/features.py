import datetime
import re
from datetime import date
from functools import lru_cache
from statistics import mean, stdev

import numpy as np
from fuzzywuzzy import process
from sklearn.cluster import KMeans

from recur_scan.transactions import Transaction

RECURRING_VENDORS = {
    # Streaming & Entertainment
    "netflix",
    "spotify",
    "disney+",
    "hulu",
    "amazon prime",
    "hbo max",
    "apple music",
    "youtube premium",
    "paramount+",
    "peacock",
    # Cloud & Software Subscriptions
    "microsoft",
    "adobe",
    "google workspace",
    "dropbox",
    "zoom",
    "notion",
    "evernote",
    "github",
    "figma",
    "canva",
    "grammarly",
    # Telecom & Internet
    "at&t",
    "verizon",
    "t-mobile",
    "spectrum",
    "xfinity",
    "comcast",
    "google fi",
    "mint mobile",
    "cricket wireless",
    # Insurance & Financial Services
    "geico",
    "state farm",
    "progressive",
    "allstate",
    "hugo insurance",
    "metlife",
    "blue cross blue shield",
    "aetna",
    "cigna",
    # Utilities & Home Services
    "duke energy",
    "pg&e",
    "con edison",
    "national grid",
    "directv",
    "dish network",
    "ring",
    "adt security",
    "vivint",
    # Fitness & Health
    "planet fitness",
    "24 hour fitness",
    "la fitness",
    "peloton",
    "fitbit premium",
    "calm",
    "headspace",
    "myfitnesspal",
    # Food & Delivery
    "hello fresh",
    "blue apron",
    "doordash pass",
    "uber eats pass",
    "instacart+",
    "starbucks rewards",
    # Miscellaneous Subscriptions
    "amazon aws",
    "patreon",
    "onlyfans",
    "substack",
    "new york times",
    "washington post",
    "the economist",
    "linkedin premium",
    "audible",
}


def count_transactions_by_amount(transaction: Transaction, transactions: list[Transaction]) -> tuple[int, float]:
    """Returns count and percentage of transactions with the same amount."""
    if not transactions:
        return 0, 0.0
    same_amount_count = sum(1 for t in transactions if t.amount == transaction.amount)
    return same_amount_count, same_amount_count / len(transactions)


def get_recurrence_patterns(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Determines time-based recurrence patterns from past transactions."""
    merchant_txns = [t for t in transactions if t.name == transaction.name]

    if len(merchant_txns) < 2:
        return {
            key: 0
            for key in [
                "is_biweekly",
                "is_semimonthly",
                "is_monthly",
                "is_bimonthly",
                "is_quarterly",
                "is_annual",
                "avg_days_between",
                "std_days_between",
                "recurrence_score",
            ]
        }

    dates = sorted(datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in merchant_txns)
    date_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

    avg_days_between = mean(date_diffs)
    std_days_between = stdev(date_diffs) if len(date_diffs) > 1 else 0.0

    # Weighted recurrence score
    recurrence_score = sum(1 / (1 + abs(diff - avg_days_between)) for diff in date_diffs) / len(date_diffs)

    recurrence_flags = {
        "is_biweekly": int(14 in date_diffs),
        "is_semimonthly": int(any(d in {14, 15, 16, 17} for d in date_diffs)),
        "is_monthly": int(any(27 <= d <= 31 for d in date_diffs)),
        "is_bimonthly": int(any(55 <= d <= 65 for d in date_diffs)),
        "is_quarterly": int(any(85 <= d <= 95 for d in date_diffs)),
        "is_annual": int(any(360 <= d <= 370 for d in date_diffs)),
    }

    return {
        **recurrence_flags,
        "avg_days_between": avg_days_between,
        "std_days_between": std_days_between,
        "recurrence_score": recurrence_score,
    }


def get_recurring_consistency_score(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Computes a consistency score to minimize bias errors in recurring transaction detection."""

    merchant_txns = [t for t in transactions if t.name == transaction.name]

    if len(merchant_txns) < 2:
        return {"recurring_consistency_score": 0.0}  # Not enough data to determine recurrence

    dates = sorted(datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in merchant_txns)
    date_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

    avg_days_between = mean(date_diffs)
    std_days_between = stdev(date_diffs) if len(date_diffs) > 1 else 0.0

    amount_variations = [t.amount for t in merchant_txns]
    amount_stability = 1 - (stdev(amount_variations) / (mean(amount_variations) + 1e-6))  # Normalize stability score

    # Frequency-based confidence (e.g., monthly = strong, yearly = weaker)
    recurrence_flags = {
        "biweekly": int(14 in date_diffs),
        "monthly": int(any(27 <= d <= 31 for d in date_diffs)),
        "bimonthly": int(any(55 <= d <= 65 for d in date_diffs)),
        "quarterly": int(any(85 <= d <= 95 for d in date_diffs)),
        "annual": int(any(360 <= d <= 370 for d in date_diffs)),
    }

    # Weight factors based on common recurrence patterns
    recurrence_weight = (
        0.4 * recurrence_flags["monthly"]
        + 0.2 * recurrence_flags["biweekly"]
        + 0.15 * recurrence_flags["bimonthly"]
        + 0.1 * recurrence_flags["quarterly"]
        + 0.05 * recurrence_flags["annual"]
    )

    # Final consistency score (scales from 0 to 1)
    consistency_score = (
        0.5 * amount_stability  # Amount consistency
        + 0.3 * (1 - (std_days_between / (avg_days_between + 1e-6)))  # Time interval consistency
        + 0.2 * recurrence_weight  # Frequency confidence
    )

    return {"recurring_consistency_score": round(max(0, min(consistency_score, 1)), 2)}


def validate_recurring_transaction(transaction: Transaction, threshold: int = 80) -> bool:
    """Determines if a transaction should be classified as recurring based on vendor trends."""
    vendor_name = transaction.name.lower()

    # Fuzzy Matching for Vendor Detection
    match_result: tuple[str, int] | None = process.extractOne(vendor_name, RECURRING_VENDORS)

    # If no match is found, return False
    if match_result is None:
        return False

    # Extract the best match and its score
    best_match, score = match_result

    # Return True if the score is above the threshold
    return score > threshold


def classify_subscription_tier(transaction: Transaction) -> str:
    """Dynamically classifies a transaction's subscription tier."""
    subscription_tiers = {
        "netflix": [(8.99, "Basic"), (15.49, "Standard"), (19.99, "Premium")],
        "spotify": [(9.99, "Individual"), (12.99, "Duo"), (15.99, "Family")],
        "disney+": [(7.99, "Basic"), (13.99, "Premium")],
    }

    vendor_name = transaction.name.lower()
    amount = transaction.amount

    return next((tier for price, tier in subscription_tiers.get(vendor_name, []) if price == amount), "Unknown")


def get_amount_features(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Extracts features related to amount stability using clustering."""
    vendor_txns = [t.amount for t in transactions if t.name == transaction.name]

    if not vendor_txns:
        return {"is_fixed_amount_recurring": 0, "amount_fluctuation": 0.0, "price_cluster": -1}

    price_fluctuation = max(vendor_txns) - min(vendor_txns)

    # Handle edge cases for KMeans clustering
    if len(vendor_txns) < 3 or len(set(vendor_txns)) == 1:
        return {
            "is_fixed_amount_recurring": int(max(vendor_txns) <= min(vendor_txns) * 1.02),
            "amount_fluctuation": price_fluctuation,
            "price_cluster": -1,  # Indicates clustering was not performed
        }

    # Perform KMeans clustering
    amounts = np.array(vendor_txns).reshape(-1, 1)
    kmeans = KMeans(n_clusters=min(3, len(set(vendor_txns))), random_state=42).fit(amounts)
    price_cluster = kmeans.predict([[transaction.amount]])[0]

    return {
        "is_fixed_amount_recurring": int(max(vendor_txns) <= min(vendor_txns) * 1.02),
        "amount_fluctuation": price_fluctuation,
        "price_cluster": price_cluster,
    }


def get_user_behavior_features(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Extracts user-level spending behavior."""
    user_txns = [t.amount for t in transactions if t.user_id == transaction.user_id]

    if not user_txns:
        return {"user_avg_spent": 0.0, "user_total_spent": 0.0, "user_subscription_count": 0}

    user_subscription_count = sum(t.name in RECURRING_VENDORS for t in transactions)

    return {
        "user_avg_spent": mean(user_txns),
        "user_total_spent": sum(user_txns),
        "user_subscription_count": user_subscription_count,
    }


def get_refund_features(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Extracts refund-related features."""
    refunds = [t for t in transactions if t.amount == -transaction.amount]

    if not refunds:
        return {"refund_rate": 0.0, "avg_refund_time_lag": 0.0}

    refund_time_lags = [
        (datetime.datetime.strptime(t.date, "%Y-%m-%d") - datetime.datetime.strptime(transaction.date, "%Y-%m-%d")).days
        for t in refunds
    ]

    return {
        "refund_rate": len(refunds) / len(transactions),
        "avg_refund_time_lag": mean(refund_time_lags) if refund_time_lags else 0.0,
    }


def get_monthly_spending_trend(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Calculates the total spending for the transaction's month."""
    month_year = transaction.date[:7]  # Extracts YYYY-MM
    monthly_spending = sum(t.amount for t in transactions if t.date.startswith(month_year))

    return {"monthly_spending_trend": monthly_spending}


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


def _get_day(date: str) -> int:
    """Get the day of the month from a transaction date."""
    return int(date.split("-")[2])


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    """Get the number of transactions in all_transactions that are on the same day of the month as transaction"""
    return len([t for t in all_transactions if abs(_get_day(t.date) - _get_day(transaction.date)) <= n_days_off])


def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in 99"""
    return (transaction.amount * 100) % 100 == 99


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions)


def get_features(transaction: Transaction, transactions: list[Transaction]) -> dict:
    """Extracts all relevant features for a transaction."""
    same_amount_count, same_amount_pct = count_transactions_by_amount(transaction, transactions)

    return {
        "n_transactions_same_amount": same_amount_count,
        "percent_transactions_same_amount": same_amount_pct,
        **get_recurrence_patterns(transaction, transactions),
        "subscription_tier": classify_subscription_tier(transaction),
        **get_amount_features(transaction, transactions),
        **get_user_behavior_features(transaction, transactions),
        **get_refund_features(transaction, transactions),
        **get_monthly_spending_trend(transaction, transactions),
        "is_valid_recurring_transaction": int(validate_recurring_transaction(transaction)),
    }


# def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
#     return {
#         "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
#         "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
#         "ends_in_99": get_ends_in_99(transaction),
#         "amount": transaction.amount,
#         "same_day_exact": get_n_transactions_same_day(transaction, all_transactions, 0),
#         "same_day_off_by_1": get_n_transactions_same_day(transaction, all_transactions, 1),
#         "same_day_off_by_2": get_n_transactions_same_day(transaction, all_transactions, 2),
#         "14_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 14, 0),
#         "14_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 14, 1),
#         "7_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 7, 0),
#         "7_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 7, 1),
#         "is_insurance": get_is_insurance(transaction),
#         "is_utility": get_is_utility(transaction),
#         "is_phone": get_is_phone(transaction),
#         "is_always_recurring": get_is_always_recurring(transaction),
#     }
