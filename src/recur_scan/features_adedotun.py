import re
from collections import defaultdict

from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date

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


def get_is_always_recurring_at(transaction: Transaction) -> bool:
    """Standalone version of get_is_always_recurring with _at suffix"""
    normalized_name = normalize_vendor_name_at(transaction.name)
    return normalized_name in ALWAYS_RECURRING_VENDORS_AT


def get_is_utility_at(transaction: Transaction) -> bool:
    """Standalone version of get_is_utility with _at suffix"""
    return bool(re.search(r"\b(utility|utilit|energy)\b", transaction.name, re.IGNORECASE))


def get_is_insurance_at(transaction: Transaction) -> bool:
    """Standalone version of get_is_insurance with _at suffix"""
    return bool(re.search(r"\b(insurance|insur|insuranc)\b", transaction.name, re.IGNORECASE))


def get_is_phone_at(transaction: Transaction) -> bool:
    """Standalone version of get_is_phone with _at suffix"""
    return bool(re.search(r"\b(at&t|t-mobile|verizon|comcast|spectrum)\b", transaction.name, re.IGNORECASE))


def get_is_communication_or_energy_at(transaction: Transaction) -> bool:
    """Standalone version of get_is_communication_or_energy with _at suffix"""
    return get_is_phone_at(transaction) or get_is_utility_at(transaction)


def preprocess_transactions_at(transactions: list[Transaction]) -> dict:
    """Standalone version of preprocess_transactions with _at suffix"""
    by_vendor = defaultdict(list)
    by_user_vendor = defaultdict(list)
    date_objects = {}

    for t in transactions:
        normalized_name = normalize_vendor_name_at(t.name)
        by_vendor[normalized_name].append(t)
        by_user_vendor[(t.user_id, normalized_name)].append(t)
        date_objects[t] = parse_date(t.date)

    return {"by_vendor": by_vendor, "by_user_vendor": by_user_vendor, "date_objects": date_objects}


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

    similar_transactions.sort(key=lambda t: parse_date(t.date))

    if len(similar_transactions) < min_occurrences:
        return False

    recurring_count = 0
    for i in range(1, len(similar_transactions)):
        delta = (parse_date(similar_transactions[i].date) - parse_date(similar_transactions[i - 1].date)).days
        if (expected_interval - allowance) <= delta <= (expected_interval + allowance):
            recurring_count += 1
        else:
            recurring_count = 0

    return recurring_count >= min_occurrences - 1


def compute_recurring_inputs_at(
    transaction: Transaction, all_transactions: list[Transaction]
) -> tuple[list[Transaction], list[Transaction], dict]:
    """Standalone version of compute_recurring_inputs with _at suffix"""
    preprocessed = preprocess_transactions_at(all_transactions)
    normalized_name = normalize_vendor_name_at(transaction.name)
    vendor_txns = preprocessed["by_vendor"].get(normalized_name, [])
    user_vendor_txns = preprocessed["by_user_vendor"].get((transaction.user_id, normalized_name), [])
    return vendor_txns, user_vendor_txns, preprocessed


def get_n_transactions_same_amount_at(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Standalone version of get_n_transactions_same_amount with _at suffix"""
    return len([t for t in all_transactions if abs(t.amount - transaction.amount) < 0.001])


def get_percent_transactions_same_amount_tolerant(transaction: Transaction, vendor_txns: list[Transaction]) -> float:
    return sum(1 for t in vendor_txns if abs(t.amount - transaction.amount) <= 0.05 * transaction.amount) / len(
        vendor_txns
    )
