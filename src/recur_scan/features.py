import re
from collections import defaultdict
from datetime import date, datetime
from functools import lru_cache

from recur_scan.transactions import Transaction

# Precompiled regex patterns for better performance
INSURANCE_PATTERN = re.compile(r"\b(insurance|insur|insuranc)\b", re.IGNORECASE)
UTILITY_PATTERN = re.compile(r"\b(utility|utilit|energy)\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"\b(at&t|t-mobile|verizon|comcast|spectrum)\b", re.IGNORECASE)
VARIABLE_BILL_PATTERN = re.compile(r"\b(insurance|insur|bill|premium|policy|utility|energy|phone)\b", re.IGNORECASE)

ALWAYS_RECURRING_VENDORS = frozenset([
    "googlestorage",
    "netflix",
    "hulu",
    "spotify",
    "t-mobile",
    "at&t",
    "zip.co",
    "comcast",
    "spectrum",
    "cpsenergy",
    "disney+",
])

ALWAYS_RECURRING_VENDORS_AT = frozenset([
    "googlestorage",
    "netflix",
    "hulu",
    "spotify",
    "t-mobile",
    "at&t",
    "zip.co",
    "comcast",
    "spectrum",
    "cpsenergy",
    "disney+",
])


def normalize_vendor_name(vendor: str) -> str:
    """Extract the core company name from a vendor string."""
    vendor = vendor.lower().replace(" ", "")
    patterns = {
        "t-mobile": r"t-mobile",
        "at&t": r"at&t",
        "zip.co": r"zip\.co",
        "comcast": r"comcast",
        "netflix": r"netflix",
        "spectrum": r"spectrum",
        "cpsenergy": r"cpsenergy",
        "disney+": r"disney\+",
    }
    for normalized_name, pattern in patterns.items():
        if re.search(pattern, vendor, re.IGNORECASE):
            return normalized_name
    return vendor.replace(" ", "")


def normalize_vendor_name_at(vendor: str) -> str:
    """Standalone version of normalize_vendor_name with _at suffix"""
    vendor = vendor.lower().replace(" ", "")
    patterns = {
        "t-mobile": r"t-mobile",
        "at&t": r"at&t",
        "zip.co": r"zip\.co",
        "comcast": r"comcast",
        "netflix": r"netflix",
        "spectrum": r"spectrum",
        "cpsenergy": r"cpsenergy",
        "disney+": r"disney\+",
    }
    for normalized_name, pattern in patterns.items():
        if re.search(pattern, vendor, re.IGNORECASE):
            return normalized_name
    return vendor.replace(" ", "")


def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring because of the vendor name"""
    normalized_name = normalize_vendor_name(transaction.name)
    return normalized_name in ALWAYS_RECURRING_VENDORS


def get_is_always_recurring_at(transaction: Transaction) -> bool:
    """Standalone version of get_is_always_recurring with _at suffix"""
    normalized_name = normalize_vendor_name_at(transaction.name)
    return normalized_name in ALWAYS_RECURRING_VENDORS_AT


def get_is_insurance(transaction: Transaction) -> bool:
    """Check if the transaction is an insurance payment."""
    return bool(INSURANCE_PATTERN.search(transaction.name))


def get_is_insurance_at(transaction: Transaction) -> bool:
    """Standalone version of get_is_insurance with _at suffix"""
    return bool(re.search(r"\b(insurance|insur|insuranc)\b", transaction.name, re.IGNORECASE))


def get_is_utility(transaction: Transaction) -> bool:
    """Check if the transaction is a utility payment."""
    return bool(UTILITY_PATTERN.search(transaction.name))


def get_is_utility_at(transaction: Transaction) -> bool:
    """Standalone version of get_is_utility with _at suffix"""
    return bool(re.search(r"\b(utility|utilit|energy)\b", transaction.name, re.IGNORECASE))


def get_is_phone(transaction: Transaction) -> bool:
    """Check if the transaction is a phone payment."""
    return bool(PHONE_PATTERN.search(transaction.name))


def get_is_phone_at(transaction: Transaction) -> bool:
    """Standalone version of get_is_phone with _at suffix"""
    return bool(re.search(r"\b(at&t|t-mobile|verizon|comcast|spectrum)\b", transaction.name, re.IGNORECASE))


def get_is_communication_or_energy(transaction: Transaction) -> bool:
    """Check if the transaction is from a communication or energy company"""
    return get_is_phone(transaction) or get_is_utility(transaction)


def get_is_communication_or_energy_at(transaction: Transaction) -> bool:
    """Standalone version of get_is_communication_or_energy with _at suffix"""
    return get_is_phone_at(transaction) or get_is_utility_at(transaction)


@lru_cache(maxsize=1024)
def _parse_date(date_str: str) -> date:
    """Parse a date string into a datetime.date object."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


@lru_cache(maxsize=1024)
def _parse_date_at(date_str: str) -> date:
    """Standalone version of _parse_date with _at suffix"""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def get_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in 99"""
    return abs((transaction.amount * 100) % 100 - 99) < 0.001


def get_ends_in_99_at(transaction: Transaction) -> bool:
    """Standalone version of get_ends_in_99 with _at suffix"""
    return abs((transaction.amount * 100) % 100 - 99) < 0.001


def preprocess_transactions(transactions: list[Transaction]) -> dict:
    """Preprocess transactions once to avoid repeated computations"""
    by_vendor = defaultdict(list)
    by_user_vendor = defaultdict(list)
    date_objects = {}

    for t in transactions:
        normalized_name = normalize_vendor_name(t.name)
        by_vendor[normalized_name].append(t)
        by_user_vendor[(t.user_id, normalized_name)].append(t)
        date_objects[t] = _parse_date(t.date)

    return {"by_vendor": by_vendor, "by_user_vendor": by_user_vendor, "date_objects": date_objects}


def preprocess_transactions_at(transactions: list[Transaction]) -> dict:
    """Standalone version of preprocess_transactions with _at suffix"""
    by_vendor = defaultdict(list)
    by_user_vendor = defaultdict(list)
    date_objects = {}

    for t in transactions:
        normalized_name = normalize_vendor_name_at(t.name)
        by_vendor[normalized_name].append(t)
        by_user_vendor[(t.user_id, normalized_name)].append(t)
        date_objects[t] = _parse_date_at(t.date)

    return {"by_vendor": by_vendor, "by_user_vendor": by_user_vendor, "date_objects": date_objects}


def is_recurring_core(
    transaction: Transaction,
    relevant_txns: list[Transaction],
    preprocessed: dict,
    interval: int = 30,
    variance: int = 4,
    min_occurrences: int = 2,
) -> bool:
    """Core recurring detection with preprocessed data"""
    is_always = get_is_always_recurring(transaction)
    is_comm_energy = get_is_communication_or_energy(transaction)
    if is_always or is_comm_energy:
        return True

    relevant_txns = list(relevant_txns)
    if transaction not in relevant_txns:
        relevant_txns.append(transaction)

    if len(relevant_txns) < min_occurrences:
        return False

    dates = sorted(preprocessed["date_objects"][t] for t in relevant_txns)
    recurring_count = 0

    for i in range(1, len(dates)):
        delta = (dates[i] - dates[i - 1]).days
        if abs(delta - interval) <= variance:
            recurring_count += 1
        elif delta > interval + variance:
            recurring_count = 0

    return recurring_count >= min_occurrences - 1


def is_recurring_core_at(
    transaction: Transaction,
    relevant_txns: list[Transaction],
    preprocessed: dict,
    interval: int = 30,
    variance: int = 4,
    min_occurrences: int = 2,
) -> bool:
    """Standalone version of is_recurring_core with _at suffix"""
    is_always = get_is_always_recurring_at(transaction)
    is_comm_energy = get_is_communication_or_energy_at(transaction)
    if is_always or is_comm_energy:
        return True

    relevant_txns = list(relevant_txns)
    if transaction not in relevant_txns:
        relevant_txns.append(transaction)

    if len(relevant_txns) < min_occurrences:
        return False

    dates = sorted(preprocessed["date_objects"][t] for t in relevant_txns)
    recurring_count = 0

    for i in range(1, len(dates)):
        delta = (dates[i] - dates[i - 1]).days
        if abs(delta - interval) <= variance:
            recurring_count += 1
        elif delta > interval + variance:
            recurring_count = 0

    return recurring_count >= min_occurrences - 1


def is_recurring_allowance(
    transaction: Transaction,
    transaction_history: list[Transaction],
    expected_interval: int = 30,
    allowance: int = 2,
    min_occurrences: int = 2,
) -> bool:
    """Check if a transaction appears to be recurring based on historical data"""
    is_always = get_is_always_recurring(transaction)
    is_comm_energy = get_is_communication_or_energy(transaction)
    if is_always or is_comm_energy:
        return True

    similar_transactions = [
        t
        for t in transaction_history
        if normalize_vendor_name(t.name) == normalize_vendor_name(transaction.name)
        and abs(t.amount - transaction.amount) < 0.01
    ]

    if transaction not in similar_transactions:
        similar_transactions.append(transaction)

    similar_transactions.sort(key=lambda t: _parse_date(t.date))

    if len(similar_transactions) < min_occurrences:
        return False

    recurring_count = 0
    for i in range(1, len(similar_transactions)):
        delta = (_parse_date(similar_transactions[i].date) - _parse_date(similar_transactions[i - 1].date)).days
        if (expected_interval - allowance) <= delta <= (expected_interval + allowance):
            recurring_count += 1
        else:
            recurring_count = 0

    return recurring_count >= min_occurrences - 1


def is_recurring_allowance_at(
    transaction: Transaction,
    transaction_history: list[Transaction],
    expected_interval: int = 30,
    allowance: int = 2,
    min_occurrences: int = 2,
) -> bool:
    """Standalone version of is_recurring_allowance with _at suffix"""
    is_always = get_is_always_recurring_at(transaction)
    is_comm_energy = get_is_communication_or_energy_at(transaction)
    if is_always or is_comm_energy:
        return True

    similar_transactions = [
        t
        for t in transaction_history
        if normalize_vendor_name_at(t.name) == normalize_vendor_name_at(transaction.name)
        and abs(t.amount - transaction.amount) < 0.01
    ]

    if transaction not in similar_transactions:
        similar_transactions.append(transaction)

    similar_transactions.sort(key=lambda t: _parse_date_at(t.date))

    if len(similar_transactions) < min_occurrences:
        return False

    recurring_count = 0
    for i in range(1, len(similar_transactions)):
        delta = (_parse_date_at(similar_transactions[i].date) - _parse_date_at(similar_transactions[i - 1].date)).days
        if (expected_interval - allowance) <= delta <= (expected_interval + allowance):
            recurring_count += 1
        else:
            recurring_count = 0

    return recurring_count >= min_occurrences - 1


def compute_recurring_inputs(
    transaction: Transaction, all_transactions: list[Transaction]
) -> tuple[list[Transaction], list[Transaction], dict]:
    """Compute vendor_txns, user_vendor_txns, and preprocessed data for recurring checks"""
    preprocessed = preprocess_transactions(all_transactions)
    normalized_name = normalize_vendor_name(transaction.name)
    vendor_txns = preprocessed["by_vendor"].get(normalized_name, [])
    user_vendor_txns = preprocessed["by_user_vendor"].get((transaction.user_id, normalized_name), [])
    return vendor_txns, user_vendor_txns, preprocessed


def compute_recurring_inputs_at(
    transaction: Transaction, all_transactions: list[Transaction]
) -> tuple[list[Transaction], list[Transaction], dict]:
    """Standalone version of compute_recurring_inputs with _at suffix"""
    preprocessed = preprocess_transactions_at(all_transactions)
    normalized_name = normalize_vendor_name_at(transaction.name)
    vendor_txns = preprocessed["by_vendor"].get(normalized_name, [])
    user_vendor_txns = preprocessed["by_user_vendor"].get((transaction.user_id, normalized_name), [])
    return vendor_txns, user_vendor_txns, preprocessed


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

    for t in all_transactions:
        t_date = _parse_date(t.date)
        days_diff = abs((t_date - transaction_date).days)

        if days_diff == 0:
            continue

        remainder = days_diff % n_days_apart
        if remainder <= n_days_off or remainder >= (n_days_apart - n_days_off):
            n_txs += 1

    return n_txs


def get_n_transactions_days_apart_at(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> int:
    """
    Standalone version of get_n_transactions_days_apart with _at suffix
    """
    n_txs = 0
    transaction_date = _parse_date_at(transaction.date)

    for t in all_transactions:
        t_date = _parse_date_at(t.date)
        days_diff = abs((t_date - transaction_date).days)

        if days_diff == 0:
            continue

        remainder = days_diff % n_days_apart
        if remainder <= n_days_off or remainder >= (n_days_apart - n_days_off):
            n_txs += 1

    return n_txs


def get_pct_transactions_days_apart(
    transaction: Transaction, all_transactions: list[Transaction], n_days_apart: int, n_days_off: int
) -> float:
    """
    Get the percentage of transactions in all_transactions that are within
    n_days_off of being n_days_apart from transaction
    """
    if not all_transactions:
        return 0.0
    return get_n_transactions_days_apart(transaction, all_transactions, n_days_apart, n_days_off) / len(
        all_transactions
    )


def get_pct_transactions_days_apart_at(
    transaction: Transaction, all_transactions: list[Transaction], n_days_apart: int, n_days_off: int
) -> float:
    """
    Standalone version of get_pct_transactions_days_apart with _at suffix
    """
    if not all_transactions:
        return 0.0
    return get_n_transactions_days_apart_at(transaction, all_transactions, n_days_apart, n_days_off) / len(
        all_transactions
    )


def _get_day(date: str) -> int:
    """Get the day of the month from a transaction date."""
    return int(date.split("-")[2])


def _get_day_at(date: str) -> int:
    """Standalone version of _get_day with _at suffix"""
    return int(date.split("-")[2])


def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    """Get the number of transactions in all_transactions that are on the same day of the month as transaction"""
    transaction_day = _get_day(transaction.date)
    return len([t for t in all_transactions if abs(_get_day(t.date) - transaction_day) <= n_days_off])


def get_n_transactions_same_day_at(
    transaction: Transaction, all_transactions: list[Transaction], n_days_off: int
) -> int:
    """Standalone version of get_n_transactions_same_day with _at suffix"""
    transaction_day = _get_day_at(transaction.date)
    return len([t for t in all_transactions if abs(_get_day_at(t.date) - transaction_day) <= n_days_off])


def get_pct_transactions_same_day(
    transaction: Transaction, all_transactions: list[Transaction], n_days_off: int
) -> float:
    """Get the percentage of transactions in all_transactions that are on the same day of the month as transaction"""
    if not all_transactions:
        return 0.0
    return get_n_transactions_same_day(transaction, all_transactions, n_days_off) / len(all_transactions)


def get_pct_transactions_same_day_at(
    transaction: Transaction, all_transactions: list[Transaction], n_days_off: int
) -> float:
    """Standalone version of get_pct_transactions_same_day with _at suffix"""
    if not all_transactions:
        return 0.0
    return get_n_transactions_same_day_at(transaction, all_transactions, n_days_off) / len(all_transactions)


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if abs(t.amount - transaction.amount) < 0.001])


def get_n_transactions_same_amount_at(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Standalone version of get_n_transactions_same_amount with _at suffix"""
    return len([t for t in all_transactions if abs(t.amount - transaction.amount) < 0.001])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    return get_n_transactions_same_amount(transaction, all_transactions) / len(all_transactions)


def get_percent_transactions_same_amount_at(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Standalone version of get_percent_transactions_same_amount with _at suffix"""
    if not all_transactions:
        return 0.0
    return get_n_transactions_same_amount_at(transaction, all_transactions) / len(all_transactions)


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    """Get all features for a transaction."""
    vendor_txns, user_vendor_txns, preprocessed = compute_recurring_inputs(transaction, all_transactions)
    date_obj = preprocessed["date_objects"][transaction]

    same_amount = get_n_transactions_same_amount(transaction, vendor_txns)
    same_amount_tolerant = sum(
        1 for t in vendor_txns if abs(t.amount - transaction.amount) <= 0.05 * transaction.amount
    )
    total_txns = len(vendor_txns)

    return {
        "n_transactions_same_amount": same_amount,
        "percent_transactions_same_amount": same_amount / total_txns if total_txns else 0.0,
        "percent_transactions_same_amount_tolerant": same_amount_tolerant / total_txns if total_txns else 0.0,
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
        "is_communication_or_energy": get_is_communication_or_energy(transaction),
        "is_recurring_monthly": is_recurring_core(transaction, vendor_txns, preprocessed, 30, 4, 2),
        "is_recurring_weekly": is_recurring_core(transaction, vendor_txns, preprocessed, 7, 2, 2),
        "is_recurring_user_vendor": is_recurring_core(transaction, user_vendor_txns, preprocessed, 30, 4, 2),
        "day_consistency": sum(1 for t in vendor_txns if abs(date_obj.day - preprocessed["date_objects"][t].day) <= 2)
        / total_txns
        if total_txns
        else 0.0,
        "amount_stability": (sum((t.amount - transaction.amount) ** 2 for t in vendor_txns) / total_txns) ** 0.5
        / transaction.amount
        if total_txns and transaction.amount
        else 0.0,
        "is_recurring_allowance": is_recurring_allowance(transaction, all_transactions, 30, 2, 2),
    }


def get_features_at(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    """Standalone version of get_features with _at suffix"""
    vendor_txns, user_vendor_txns, preprocessed = compute_recurring_inputs_at(transaction, all_transactions)
    date_obj = preprocessed["date_objects"][transaction]

    same_amount = get_n_transactions_same_amount_at(transaction, vendor_txns)
    same_amount_tolerant = sum(
        1 for t in vendor_txns if abs(t.amount - transaction.amount) <= 0.05 * transaction.amount
    )
    total_txns = len(vendor_txns)

    return {
        "n_transactions_same_amount": same_amount,
        "percent_transactions_same_amount": same_amount / total_txns if total_txns else 0.0,
        "percent_transactions_same_amount_tolerant": same_amount_tolerant / total_txns if total_txns else 0.0,
        "ends_in_99": get_ends_in_99_at(transaction),
        "amount": transaction.amount,
        "same_day_exact": get_n_transactions_same_day_at(transaction, all_transactions, 0),
        "pct_transactions_same_day": get_pct_transactions_same_day_at(transaction, all_transactions, 0),
        "same_day_off_by_1": get_n_transactions_same_day_at(transaction, all_transactions, 1),
        "same_day_off_by_2": get_n_transactions_same_day_at(transaction, all_transactions, 2),
        "14_days_apart_exact": get_n_transactions_days_apart_at(transaction, all_transactions, 14, 0),
        "pct_14_days_apart_exact": get_pct_transactions_days_apart_at(transaction, all_transactions, 14, 0),
        "14_days_apart_off_by_1": get_n_transactions_days_apart_at(transaction, all_transactions, 14, 1),
        "pct_14_days_apart_off_by_1": get_pct_transactions_days_apart_at(transaction, all_transactions, 14, 1),
        "7_days_apart_exact": get_n_transactions_days_apart_at(transaction, all_transactions, 7, 0),
        "pct_7_days_apart_exact": get_pct_transactions_days_apart_at(transaction, all_transactions, 7, 0),
        "7_days_apart_off_by_1": get_n_transactions_days_apart_at(transaction, all_transactions, 7, 1),
        "pct_7_days_apart_off_by_1": get_pct_transactions_days_apart_at(transaction, all_transactions, 7, 1),
        "is_insurance": get_is_insurance_at(transaction),
        "is_utility": get_is_utility_at(transaction),
        "is_phone": get_is_phone_at(transaction),
        "is_always_recurring": get_is_always_recurring_at(transaction),
        "is_communication_or_energy": get_is_communication_or_energy_at(transaction),
        "is_recurring_monthly": is_recurring_core_at(transaction, vendor_txns, preprocessed, 30, 4, 2),
        "is_recurring_weekly": is_recurring_core_at(transaction, vendor_txns, preprocessed, 7, 2, 2),
        "is_recurring_user_vendor": is_recurring_core_at(transaction, user_vendor_txns, preprocessed, 30, 4, 2),
        "day_consistency": sum(1 for t in vendor_txns if abs(date_obj.day - preprocessed["date_objects"][t].day) <= 2)
        / total_txns
        if total_txns
        else 0.0,
        "amount_stability": (sum((t.amount - transaction.amount) ** 2 for t in vendor_txns) / total_txns) ** 0.5
        / transaction.amount
        if total_txns and transaction.amount
        else 0.0,
        "is_recurring_allowance": is_recurring_allowance_at(transaction, all_transactions, 30, 2, 2),
    }
