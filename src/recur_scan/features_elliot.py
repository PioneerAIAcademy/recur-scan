# %%
# configure the script
import re
from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime

from thefuzz import fuzz

from recur_scan.transactions import Transaction

#


def get_is_near_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if a transaction has a recurring amount within 5% of another transaction."""
    return any(
        t != transaction and abs(transaction.amount - t.amount) / max(t.amount, 0.01) <= 0.05 for t in all_transactions
    )


def is_utility_bill(transaction: Transaction) -> bool:
    """
    Check if the transaction is a utility bill (water, gas, electricity, etc.).
    """
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

    # Check for keywords or known US utility providers
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
    """
    Check if the transaction is an automatic recurring payment.
    """
    return bool(re.search(r"\b(auto\s?pay|autopayment|automatic payment)\b", transaction.name, re.IGNORECASE))


def is_membership(transaction: Transaction) -> bool:
    """
    Check if the transaction is a membership payment.
    """
    membership_keywords = r"\b(membership|subscription|club|gym|association|society)\b"
    return bool(re.search(membership_keywords, transaction.name, re.IGNORECASE))


def is_recurring_based_on_99(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if a transaction is recurring based on:
    - Amount ending in .99
    - At least 3 occurrences
    - Same company/vendor
    - Appears at 7, 14, 30, or 60-day intervals

    :param transaction: Transaction to check
    :param all_transactions: List of all transactions
    :return: True if it meets the recurring pattern, False otherwise
    """
    if (transaction.amount * 100) % 100 != 99:
        return False

    vendor = transaction.name.lower()
    date_occurrences = defaultdict(list)

    # Store transactions for the same vendor
    for t in all_transactions:
        if t.name.lower() == vendor and (t.amount * 100) % 100 == 99:
            days_since_epoch = (datetime.strptime(t.date, "%Y-%m-%d") - datetime(1970, 1, 1)).days
            date_occurrences[vendor].append(days_since_epoch)

    # Check for recurring pattern (7, 14, 30, or 60 days apart)
    if len(date_occurrences[vendor]) < 3:
        return False  # Must appear at least 3 times

    date_occurrences[vendor].sort()

    count = 1  # Start with the first transaction counted
    for i in range(1, len(date_occurrences[vendor])):
        day_diff = date_occurrences[vendor][i] - date_occurrences[vendor][i - 1]

        if day_diff in {7, 14, 30, 60}:
            count += 1
            if count >= 3:
                return True  # Recurring pattern found
        else:
            count = 1  # Reset count if the gap doesn't match

    return False


def get_transaction_similarity(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Computes the average similarity score of a transaction with other transactions."""
    scores: list[int] = [
        fuzz.partial_ratio(transaction.name.lower(), t.name.lower()) for t in all_transactions if t.id != transaction.id
    ]
    return float(sum(scores)) / len(scores) if scores else 0.0


def is_weekday_transaction(transaction: Transaction) -> bool:
    """Returns True if the transaction happened on a weekday (Monday-Friday)."""
    return datetime.strptime(transaction.date, "%Y-%m-%d").weekday() < 5


def is_price_trending(transaction: Transaction, all_transactions: list[Transaction], threshold: int) -> bool:
    """
    Checks if a transaction's amount gradually increases or decreases within a threshold percentage.
    """
    same_vendor_txs = [t.amount for t in all_transactions if t.name == transaction.name]
    if len(same_vendor_txs) < 3:  # Need at least 3 data points to detect trends
        return False

    price_differences = [abs(same_vendor_txs[i] - same_vendor_txs[i - 1]) for i in range(1, len(same_vendor_txs))]
    avg_change = sum(price_differences) / len(price_differences)

    return avg_change <= (transaction.amount * threshold / 100)


def is_split_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Detects if a transaction is part of a split payment series."""
    related_txs = [t for t in all_transactions if t.amount < transaction.amount and t.name == transaction.name]
    return len(related_txs) >= 2  # Consider it a split payment if there are 2+ similar smaller transactions


# %%
# configure the script
# NEW FEATURES


def organize_transactions_by_user_company(
    transactions: list[dict],
) -> dict[str, dict[str, dict[datetime, list[float]]]]:
    user_data: dict[str, dict[str, dict[datetime, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    for txn in transactions:
        user_id = txn["user_id"]
        merchant = txn["merchant"].lower()  # safer to lowercase merchants
        date_str = txn["date"]
        date = datetime.strptime(date_str, "%Y-%m-%d") if isinstance(date_str, str) else date_str
        amount = txn["amount"]
        user_data[user_id][merchant][date].append(amount)
    return {
        user: {merchant: dict(dates) for merchant, dates in merchants.items()} for user, merchants in user_data.items()
    }


# %%
# configure the script
def detect_duplicates(txns: list[dict]) -> list[dict]:
    """
    Detect exact duplicate transactions based on (amount, merchant, date).
    Returns list of duplicate transaction dicts.
    """
    seen = set()
    duplicates = []
    for txn in txns:
        key = (txn["amount"], txn["merchant"], txn["date"])
        if key in seen:
            duplicates.append(txn)
        else:
            seen.add(key)
    return duplicates


# %%
# configure the script
def detect_split_payments(txns: list[dict], tolerance: float = 0.1, window_days: int = 7) -> list[tuple[dict, dict]]:
    """
    Detect split payments for the same merchant within tolerance % and time window.
    Returns list of tuples of transaction dicts considered splits.
    """
    split_payments = []
    txns_sorted = sorted(txns, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
    for i, txn in enumerate(txns_sorted):
        for txn2 in txns_sorted[i + 1 :]:
            if txn["merchant"] == txn2["merchant"]:
                amount_gap = abs(txn["amount"] - txn2["amount"])
                if amount_gap <= max(txn["amount"], txn2["amount"]) * tolerance:
                    time_diff = abs(
                        datetime.strptime(txn["date"], "%Y-%m-%d") - datetime.strptime(txn2["date"], "%Y-%m-%d")
                    ).days
                    if time_diff <= window_days:
                        split_payments.append((txn, txn2))
    return split_payments


# %%
# configure the script
def detect_spending_anomalies(txns: list[dict]) -> set[str]:
    """
    Detect merchants where total spending deviates by >50% from the per-company average.
    Returns set of merchant names flagged as anomalies.
    """
    spending_by_merchant: defaultdict[str, float] = defaultdict(float)
    for txn in txns:
        spending_by_merchant[txn["merchant"]] += txn["amount"]
    avg_spending = sum(spending_by_merchant.values()) / len(spending_by_merchant)
    anomalies = {
        merchant for merchant, total in spending_by_merchant.items() if abs(total - avg_spending) > 0.5 * avg_spending
    }
    return anomalies


# %%
# configure the script
def calculate_weekday_consistency(txns: list[dict]) -> float:
    """
    Fraction of transactions occurring on the same weekday as the first transaction.
    """
    if not txns:
        return 0.0
    weekdays = [datetime.strptime(txn["date"], "%Y-%m-%d").weekday() for txn in txns]
    baseline = weekdays[0]
    return sum(1 for day in weekdays if day == baseline) / len(weekdays)


# %%
# configure the script
def calculate_merchant_diversity(txns: list[dict]) -> float:
    """
    Fraction of unique merchants over total transactions.
    """
    unique_merchants = {txn["merchant"] for txn in txns}
    return len(unique_merchants) / len(txns) if txns else 0.0


# %%
# configure the script
def _to_txn_dict(txn: Transaction | dict) -> dict[str, float | str]:
    if isinstance(txn, Transaction):
        return {
            "merchant": txn.name,
            "amount": txn.amount,
            "date": txn.date,
        }
    elif isinstance(txn, dict):
        return {
            "merchant": txn["name"],
            "amount": txn["amount"],
            "date": txn["date"],
        }
    else:
        raise TypeError(f"Unsupported transaction type: {type(txn)}")


# %%
# configure the script


def get_new_features(txn: Transaction, all_txns: Sequence[Transaction]) -> dict[str, float | bool]:
    """
    Extract six key features for a single transaction, whether txn/all_txns
    are passed in as Transaction objects or dicts.
    """
    # 1) Normalize inputs
    txn_dicts = [_to_txn_dict(t) for t in all_txns]
    this_txn = _to_txn_dict(txn)

    # 2) Compute each feature on the dict list
    return {
        "num_dates_for_user_merchant": len(
            organize_transactions_by_user_company(txn_dicts)
            .get(str(this_txn["user_id"]).lower(), {})
            .get(str(this_txn["merchant"]).lower(), {})
        ),
        "is_duplicate": this_txn in detect_duplicates(txn_dicts),
        "is_split_payment": any(this_txn in pair for pair in detect_split_payments(txn_dicts)),
        "is_spending_anomaly": this_txn["merchant"] in detect_spending_anomalies(txn_dicts),
        "weekday_consistency": calculate_weekday_consistency(txn_dicts),
        "merchant_diversity": calculate_merchant_diversity(txn_dicts),
    }


# %%
