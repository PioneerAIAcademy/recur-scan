import re
import statistics
from collections import defaultdict
from datetime import datetime

from fuzzywuzzy import fuzz

from recur_scan.transactions import Transaction

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


def parse_date(date_str: str) -> datetime:
    """
    Parse a date string in multiple formats.

    Args:
        date_str: Date string to parse

    Returns:
        Parsed datetime object

    Raises:
        ValueError: If date string is invalid
    """
    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date: {date_str}")


def normalize_amount(amount: float) -> float:
    """
    Normalize transaction amount by rounding and adjusting for common patterns.

    Args:
        amount: Transaction amount

    Returns:
        Normalized amount
    """
    if amount <= 0:
        return 0.0
    rounded = round(amount, 2)
    if abs((amount * 100) % 100 - 99) < 5 or abs((amount * 100) % 100) < 5:
        return rounded
    return rounded


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


# nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnneeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeewwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww


# Additional patterns for non-recurring transaction detection
PERSON_NAME_PATTERN = re.compile(r"\b(mr|mrs|ms|dr)\.?\s+\w+|\b\w+\s+\w+\b", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_PATTERN = re.compile(r"\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4}")


def get_is_one_time_vendor_at(transaction: Transaction) -> bool:
    """Check if vendor appears to be a one-time service provider."""
    name = transaction.name.lower()
    return (
        bool(PERSON_NAME_PATTERN.search(name)) or bool(EMAIL_PATTERN.search(name)) or bool(PHONE_PATTERN.search(name))
    )


def get_vendor_name_entropy_at(transaction: Transaction) -> float:
    """Calculate the entropy of the vendor name (higher = more random)."""
    import math
    from collections import Counter

    text = transaction.name.lower().replace(" ", "")
    if not text:
        return 0.0
    counts = Counter(text)
    probs = [c / len(text) for c in counts.values()]
    return -sum(p * math.log(p) for p in probs)


def get_vendor_occurrence_count_at(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Count how many times this vendor appears in all transactions."""
    normalized_name = normalize_vendor_name_at(transaction.name)
    return len([t for t in all_transactions if normalize_vendor_name_at(t.name) == normalized_name])


def get_user_vendor_occurrence_count_at(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Count how many times this user transacted with this vendor."""
    normalized_name = normalize_vendor_name_at(transaction.name)
    return len([
        t
        for t in all_transactions
        if t.user_id == transaction.user_id and normalize_vendor_name_at(t.name) == normalized_name
    ])


def get_same_amount_count_at(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Count transactions with same amount (±$0.01)."""
    return len([
        t
        for t in all_transactions
        if normalize_vendor_name_at(t.name) == normalize_vendor_name_at(transaction.name)
        and abs(t.amount - transaction.amount) < 0.01
    ])


def get_similar_amount_count_at(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Count transactions with similar amount (±5%)."""
    return len([
        t
        for t in all_transactions
        if normalize_vendor_name_at(t.name) == normalize_vendor_name_at(transaction.name)
        and abs(t.amount - transaction.amount) <= 0.05 * transaction.amount
    ])


def get_amount_uniqueness_score_at(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate how unique this transaction amount is for the vendor (0-1 scale)."""
    similar_count = get_similar_amount_count_at(transaction, all_transactions)
    total_count = get_vendor_occurrence_count_at(transaction, all_transactions)
    return 1 - (similar_count / total_count) if total_count > 0 else 1.0


def get_days_since_last_occurrence_at(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Days since last transaction with same vendor."""
    vendor_txns = [
        t
        for t in all_transactions
        if normalize_vendor_name_at(t.name) == normalize_vendor_name_at(transaction.name)
        and parse_date(t.date) < parse_date(transaction.date)
    ]
    if not vendor_txns:
        return 365 * 5  # Large value if no previous occurrence
    return (parse_date(transaction.date) - parse_date(max(t.date for t in vendor_txns))).days


def get_is_weekend_at(transaction: Transaction) -> bool:
    """Check if transaction occurred on a weekend."""
    return parse_date(transaction.date).weekday() >= 5


def get_is_month_end_at(transaction: Transaction) -> bool:
    """Check if transaction occurred in the last week of the month."""
    return parse_date(transaction.date).day >= 25


# Additional patterns for non-recurring transactions
ENTERTAINMENT_PATTERN = re.compile(r"\b(cinema|movie|theater|concert|festival|show|ticket)\b", re.IGNORECASE)
FOOD_PATTERN = re.compile(r"\b(coffee|pizza|burger|restaurant|cafe|diner|bakery|eat|food)\b", re.IGNORECASE)
GAMBLING_PATTERN = re.compile(r"\b(bet|casino|poker|gamble|lottery|wager|sportsbook)\b", re.IGNORECASE)
GAMING_PATTERN = re.compile(r"\b(game|arcade|steam|playstation|xbox|nintendo|fortnite|roblox)\b", re.IGNORECASE)
RETAIL_PATTERN = re.compile(r"\b(shop|store|mall|outlet|boutique|merch|buy|purchase)\b", re.IGNORECASE)
TRAVEL_PATTERN = re.compile(
    r"\b(hotel|airbnb|flight|airline|train|bus|taxi|uber|lyft|vacation|travel)\b", re.IGNORECASE
)


def get_is_entertainment_at(transaction: Transaction) -> bool:
    """Check if vendor is entertainment-related (cinema, concert, etc.)"""
    return bool(ENTERTAINMENT_PATTERN.search(transaction.name))


def get_is_food_dining_at(transaction: Transaction) -> bool:
    """Check if vendor is food/dining-related"""
    return bool(FOOD_PATTERN.search(transaction.name))


def get_is_gambling_at(transaction: Transaction) -> bool:
    """Check if vendor is gambling-related"""
    return bool(GAMBLING_PATTERN.search(transaction.name))


def get_is_gaming_at(transaction: Transaction) -> bool:
    """Check if vendor is gaming-related"""
    return bool(GAMING_PATTERN.search(transaction.name))


def get_is_retail_at(transaction: Transaction) -> bool:
    """Check if vendor is retail shopping-related"""
    return bool(RETAIL_PATTERN.search(transaction.name))


def get_is_travel_at(transaction: Transaction) -> bool:
    """Check if vendor is travel-related"""
    return bool(TRAVEL_PATTERN.search(transaction.name))


def get_contains_common_nonrecurring_keywords_at(transaction: Transaction) -> bool:
    """Check for any non-recurring spending keywords"""
    patterns = [ENTERTAINMENT_PATTERN, FOOD_PATTERN, GAMBLING_PATTERN, GAMING_PATTERN, RETAIL_PATTERN, TRAVEL_PATTERN]
    return any(pattern.search(transaction.name) for pattern in patterns)


def is_recurring_based_on_99(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if a .99-ending transaction is recurring based on vendor, amount, and timing.

    Args:
        transaction: Transaction to check
        all_transactions: List of all transactions

    Returns:
        True if likely recurring, False otherwise
    """
    # Check .99 ending
    if abs((transaction.amount * 100) % 100 - 99) > 0.01:
        return False

    # Normalize vendor name
    base_vendor = re.sub(r"[^\w\s]", "", transaction.name.lower()).strip()

    # Find similar .99 transactions
    similar: list[Transaction] = []
    for t in all_transactions:
        t_vendor = re.sub(r"[^\w\s]", "", t.name.lower()).strip()
        if fuzz.token_sort_ratio(base_vendor, t_vendor) > 90 and abs((t.amount * 100) % 100 - 99) < 0.01:
            similar.append(t)

    # Need 2+ occurrences
    if len(similar) < 2:
        return False

    # Parse and sort dates
    try:
        similar.sort(key=lambda t: parse_date(t.date))  # Use top-level parse_date
        intervals = [
            (parse_date(similar[i].date) - parse_date(similar[i - 1].date)).days for i in range(1, len(similar))
        ]
    except ValueError:
        return False  # Invalid dates

    # Check for 2 occurrences with strong evidence
    if len(similar) == 2:
        interval = intervals[0]
        return any(abs(interval - ci) <= 3 for ci in [7, 14, 30, 60])

    # Flexible intervals
    interval_counts: defaultdict[str, int] = defaultdict(int)
    for interval in intervals:
        if 5 <= interval <= 9:
            interval_counts["weekly"] += 1
        elif 12 <= interval <= 17:
            interval_counts["biweekly"] += 1
        elif 25 <= interval <= 36:
            interval_counts["monthly"] += 1
        elif 55 <= interval <= 66:
            interval_counts["bimonthly"] += 1

    # Recurring if 2+ intervals in same period or 70%+ match
    total = len(intervals)
    matches = sum(interval_counts.values())
    return max(interval_counts.values(), default=0) >= 2 or (matches / total >= 0.7)


def get_interval_variance_coefficient(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    base_vendor = re.sub(r"[^\w\s]", "", transaction.name.lower()).strip()

    def parse_date(date_str: str) -> datetime:
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Invalid date: {date_str}")

    same_transactions = sorted(
        [
            t
            for t in all_transactions
            if fuzz.token_sort_ratio(base_vendor, re.sub(r"[^\w\s]", "", t.name.lower()).strip()) > 90
            and abs(t.amount - transaction.amount) < 0.01
        ],
        key=lambda x: parse_date(x.date),
    )

    if len(same_transactions) < 2:
        return 1.0

    intervals = [
        (parse_date(same_transactions[i + 1].date) - parse_date(same_transactions[i].date)).days
        for i in range(len(same_transactions) - 1)
    ]
    if not intervals:
        return 1.0

    # Normalize intervals
    common_intervals = {7: range(5, 10), 14: range(12, 17), 30: range(25, 36), 60: range(55, 66)}
    normalized = [next((k for k, v in common_intervals.items() if i in v), i) for i in intervals]

    # Handle 2 transactions
    if len(same_transactions) == 2 and any(abs(normalized[0] - ci) <= 3 for ci in [7, 14, 30, 60]):
        return 0.1

    # Use MAD for robustness
    try:
        mean = statistics.mean(normalized)
        if mean == 0:
            return 1.0
        mad = statistics.median([abs(i - mean) for i in normalized])
        return mad / mean if mean > 0 else 1.0
    except statistics.StatisticsError:
        return 1.0


def amount_variability_score(transactions: list[Transaction], base_vendor: str | None = None) -> float:
    """
    Scores transaction amount variability (1-10, lower = more consistent) for recurring transaction detection.
    Supports all recurring patterns (fixed, variable, tiered, sparse) with vendor-specific analysis.
    :param transactions: List of transactions to score
    :param base_vendor: Optional vendor name to filter transactions (normalized)
    :return: Variability score (1-10)
    """
    if not transactions:
        return 1.0  # Empty list is non-recurring

    # Normalize vendor name and filter transactions
    if base_vendor:
        base_vendor = re.sub(r"[^\w\s]", "", base_vendor.lower()).strip()
        transactions = [
            t
            for t in transactions
            if fuzz.token_sort_ratio(base_vendor, re.sub(r"[^\w\s]", "", t.name.lower()).strip()) > 85
        ]

    if len(transactions) < 2:
        return 1.0  # Single transactions are non-recurring

    # Parse dates and filter valid transactions in one pass
    def parse_date(date_str: str) -> datetime | None:
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    # Store transactions with valid dates and amounts
    valid_transactions: list[tuple[Transaction, datetime]] = [
        (t, datetime.combine(parsed_date, datetime.min.time()))
        for t in transactions
        if (parsed_date := parse_date(t.date)) is not None and t.amount > 0
    ]
    if len(valid_transactions) < 2:
        return 1.0

    # Extract amounts and dates
    amounts = [t.amount for t, _ in valid_transactions]
    dates = [parsed_date for _, parsed_date in valid_transactions]

    # Normalize amounts to handle variations
    def normalize_amount(amount: float) -> float:
        if amount <= 0:
            return 0.0  # Invalid amounts
        # Cluster amounts within ±0.05, prioritize .99-ending or round numbers
        rounded = round(amount, 2)
        if abs((amount * 100) % 100 - 99) < 5 or abs((amount * 100) % 100) < 5:
            return rounded
        return rounded

    normalized_amounts = [normalize_amount(amount) for amount in amounts]

    # Calculate variability using MAD
    try:
        mean_amount = statistics.mean(normalized_amounts)
        if mean_amount == 0:
            return 1.0
        mad = statistics.median([abs(a - mean_amount) for a in normalized_amounts])
        variability = mad / mean_amount if mean_amount > 0 else 1.0
    except statistics.StatisticsError:
        return 1.0

    # Non-linear scoring
    score = 1.0 + 9.0 * (1 - 1 / (1 + variability * 12))  # Logistic curve
    score = min(10.0, max(1.0, score))

    # Adjust for recurring patterns
    unique_amounts = len(set(normalized_amounts))
    amount_ratio = unique_amounts / len(normalized_amounts)

    # Small dataset: 2 transactions with similar amounts
    if len(valid_transactions) == 2 and amount_ratio <= 0.5:
        interval = (dates[1] - dates[0]).days if dates[1] > dates[0] else 0
        if interval and any(abs(interval - ci) <= 3 for ci in [7, 14, 30, 60]):
            return 1.0  # Likely recurring
        return 2.0  # Neutral, pending more data

    # Subscription-like patterns
    is_subscription_like = (
        amount_ratio <= 0.5
        or all(abs((a * 100) % 100 - 99) < 5 or abs((a * 100) % 100) < 5 for a in normalized_amounts)
        or variability < 0.1
    )

    # Interval consistency check
    dates.sort()  # Ensure chronological order
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1) if dates[i + 1] > dates[i]]
    if intervals:
        common_intervals = [range(5, 10), range(12, 17), range(25, 36), range(55, 66)]
        matches = sum(1 for i in intervals if any(i in r for r in common_intervals))
        consistency_ratio = matches / len(intervals)
        if is_subscription_like and consistency_ratio >= 0.6:
            score = min(score, 2.5)  # Cap for recurring patterns
        elif consistency_ratio < 0.4 and amount_ratio > 0.6:
            score = max(score, 6.0)  # Penalize irregular non-recurring patterns

    # Handle tiered subscriptions
    if unique_amounts <= 3 and amount_ratio <= 0.5:
        score = min(score, 3.5)  # Moderate score for tiered patterns

    # Cap score for outliers
    if unique_amounts == 2 and amount_ratio > 0.7:
        score = min(score, 4.0)  # Likely one outlier

    return round(score, 2)


def is_known_recurring_company(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Flags transactions as recurring if the vendor is likely a recurring service and shows
    consistent transaction patterns. Combines keyword hints with interval checks.
    :param transaction: Transaction to check
    :param all_transactions: List of all transactions
    :return: True if likely recurring, False otherwise
    """
    # Curated keyword list (avoid generic terms)
    known_recurring_keywords = [
        "amazon prime",
        "ancestry",
        "at&t",
        "canva",
        "comcast",
        "cox",
        "cricket wireless",
        "disney+",
        "geico",
        "google storage",
        "hulu",
        "hbo max",
        "national grid",
        "netflix",
        "peacock",
        "spotify",
        "sezzle",
        "spectrum",
        "verizon",
        "walmart+",
        "wix",
        "youtube",
    ]

    # Normalize vendor name
    base_vendor = re.sub(r"[^\w\s]", "", transaction.name.lower()).strip()

    # Check if vendor matches a known recurring keyword (fuzzy match)
    is_keyword_match = any(fuzz.token_sort_ratio(base_vendor, keyword) > 85 for keyword in known_recurring_keywords)

    # Parse date with multiple formats
    def parse_date(date_str: str) -> datetime:
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Invalid date format: {date_str}")

    # Find similar transactions (fuzzy vendor match, similar amount)
    similar_transactions = []
    for t in all_transactions:
        try:
            t_vendor = re.sub(r"[^\w\s]", "", t.name.lower()).strip()
            if fuzz.token_sort_ratio(base_vendor, t_vendor) > 85 and abs(t.amount - transaction.amount) < 0.05:
                similar_transactions.append(t)
        except ValueError:
            continue

    # Sort by date
    similar_transactions.sort(key=lambda x: parse_date(x.date))

    # If no keyword match and insufficient transactions, return False
    if not is_keyword_match and len(similar_transactions) < 2:
        return False

    # Check for consistent intervals (basic pattern validation)
    if len(similar_transactions) >= 2:
        intervals = [
            (parse_date(t2.date) - parse_date(t1.date)).days
            for i, t1 in enumerate(similar_transactions[:-1])
            for t2 in similar_transactions[i + 1 :]
            if (parse_date(t2.date) - parse_date(t1.date)).days > 0
        ]
        if not intervals:
            return is_keyword_match

        # Common billing cycles
        common_intervals = [range(5, 10), range(12, 17), range(25, 36), range(55, 66)]
        matches = sum(1 for i in intervals if any(i in r for r in common_intervals))
        consistency_ratio = matches / len(intervals) if intervals else 0

        # Recurring if keyword match OR sufficient transactions with consistent intervals
        return (
            is_keyword_match
            or (len(similar_transactions) >= 3 and consistency_ratio >= 0.7)
            or (len(similar_transactions) == 2 and any(abs(i - ci) <= 3 for i in intervals for ci in [7, 14, 30, 60]))
        )

    return is_keyword_match


def is_price_trending(transaction: Transaction, all_transactions: list[Transaction], threshold: float = 0.1) -> bool:
    """
    Checks if a transaction is part of a recurring pattern with stable, trending, or bounded amounts.
    Supports all recurring scenarios (fixed, variable, tiered, sparse) with fuzzy vendor matching,
    interval checks, and robust variability analysis. Handles type safety for date operations.
    :param transaction: Transaction to check
    :param all_transactions: List of all transactions
    :param threshold: Maximum variability ratio (default 0.1, i.e., 10%)
    :return: True if part of a recurring pattern, False otherwise
    """
    # Normalize vendor name
    base_vendor = re.sub(r"[^\w\s]", "", transaction.name.lower()).strip()

    # Parse dates
    def parse_date(date_str: str) -> datetime | None:
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    # Filter same-vendor transactions with valid dates and amounts
    same_vendor_txs: list[tuple[Transaction, datetime]] = []
    for t in all_transactions:
        parsed_date = parse_date(t.date)
        if parsed_date is None or t.amount <= 0:
            continue
        t_vendor = re.sub(r"[^\w\s]", "", t.name.lower()).strip()
        if fuzz.token_sort_ratio(base_vendor, t_vendor) > 85:
            same_vendor_txs.append((t, parsed_date))

    if len(same_vendor_txs) < 2:
        return False

    # Sort by date
    same_vendor_txs.sort(key=lambda x: x[1])
    amounts = [t.amount for t, _ in same_vendor_txs]
    dates = [t_date for _, t_date in same_vendor_txs]

    # Normalize amounts
    def normalize_amount(amount: float) -> float:
        rounded = round(amount, 2)
        if abs((amount * 100) % 100 - 99) < 5 or abs((amount * 100) % 100) < 5:
            return rounded
        return rounded

    normalized_amounts = [normalize_amount(a) for a in amounts]

    # Calculate variability
    try:
        mean_amount = statistics.mean(normalized_amounts)
        if mean_amount == 0:
            return False
        mad = statistics.median([abs(a - mean_amount) for a in normalized_amounts])
        variability = mad / mean_amount
    except statistics.StatisticsError:
        return False

    # Check intervals
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1) if dates[i + 1] > dates[i]]
    is_interval_consistent = False
    if intervals:
        common_intervals = [range(5, 10), range(12, 17), range(25, 36), range(55, 66)]
        matches = sum(1 for i in intervals if any(i in r for r in common_intervals))
        consistency_ratio = matches / len(intervals)
        is_interval_consistent = consistency_ratio >= 0.6

    # Recurring patterns
    unique_amounts = len(set(normalized_amounts))
    amount_ratio = unique_amounts / len(normalized_amounts)

    # 2-transaction case
    if len(same_vendor_txs) == 2:
        interval = intervals[0] if intervals else 0
        return (
            (amount_ratio <= 0.5 or variability < 0.1)
            and interval != 0
            and any(abs(interval - ci) <= 3 for ci in [7, 14, 30, 60])
        )

    # Subscription-like patterns
    is_subscription_like = (
        amount_ratio <= 0.5
        or all(abs((a * 100) % 100 - 99) < 5 or abs((a * 100) % 100) < 5 for a in normalized_amounts)
        or variability < 0.1
    )

    # Stable, trending, or bounded amounts
    if is_subscription_like and is_interval_consistent:
        return True

    # Check for trending or bounded variability
    price_differences = [
        abs(normalized_amounts[i] - normalized_amounts[i - 1]) for i in range(1, len(normalized_amounts))
    ]
    avg_change = sum(price_differences) / len(price_differences) if price_differences else 0
    adaptive_threshold = mean_amount * threshold

    # Bounded or trending within threshold
    if avg_change <= adaptive_threshold and is_interval_consistent:
        return True

    # Tiered subscriptions
    return unique_amounts <= 3 and amount_ratio <= 0.5 and is_interval_consistent


def get_n_transactions_same_amount_chris(
    transaction: Transaction, all_transactions: list[Transaction], base_vendor: str | None = None
) -> int:
    """
    Counts transactions with nearly the same amount as the input transaction, optionally for a specific vendor.
    :param transaction: Transaction to compare
    :param all_transactions: List of all transactions
    :param base_vendor: Optional vendor name to filter transactions (normalized)
    :return: Number of transactions with similar amounts
    """
    # Normalize vendor name
    base_vendor_normalized = re.sub(r"[^\w\s]", "", base_vendor.lower()).strip() if base_vendor else None

    def normalize_amount(amount: float) -> float:
        if amount <= 0:
            return 0.0
        rounded = round(amount, 2)
        if abs((amount * 100) % 100 - 99) < 5 or abs((amount * 100) % 100) < 5:
            return rounded
        return rounded

    target_amount = normalize_amount(transaction.amount)
    count = 0
    for t in all_transactions:
        if t.amount <= 0:
            continue
        t_vendor = re.sub(r"[^\w\s]", "", t.name.lower()).strip()
        if base_vendor_normalized and fuzz.token_sort_ratio(base_vendor_normalized, t_vendor) <= 85:
            continue
        if abs(normalize_amount(t.amount) - target_amount) <= 0.05:
            count += 1
    return count


def get_percent_transactions_same_amount_chris(
    transaction: Transaction, all_transactions: list[Transaction], base_vendor: str | None = None
) -> float:
    """
    Calculates the percentage of transactions with nearly the same amount, optionally for a specific vendor.
    Supports recurring scenarios (fixed, variable, tiered, sparse) with fuzzy vendor matching and amount normalization.
    :param transaction: Transaction to compare
    :param all_transactions: List of all transactions
    :param base_vendor: Optional vendor name to filter transactions (normalized)
    :return: Percentage of transactions with similar amounts (0.0-100.0)
    """
    if not all_transactions:
        return 0.0

    # Normalize vendor name
    base_vendor_normalized = re.sub(r"[^\w\s]", "", base_vendor.lower()).strip() if base_vendor else None

    # Filter vendor-specific transactions
    if base_vendor_normalized:
        vendor_transactions = [
            t
            for t in all_transactions
            if fuzz.token_sort_ratio(base_vendor_normalized, re.sub(r"[^\w\s]", "", t.name.lower()).strip()) > 85
            and t.amount > 0
        ]
    else:
        vendor_transactions = [t for t in all_transactions if t.amount > 0]

    if not vendor_transactions:
        return 0.0

    count = get_n_transactions_same_amount_chris(transaction, all_transactions, base_vendor)
    percentage = (count / len(vendor_transactions)) * 100.0 if vendor_transactions else 0.0
    return round(min(100.0, max(0.0, percentage)), 2)


def get_interval_histogram(
    transaction: Transaction, all_transactions: list[Transaction], amount_tolerance: float = 0.05
) -> float:
    """
    Calculate a periodicity score based on the distribution of time intervals between similar transactions.
    Returns a single score in [0, 1] representing the likelihood of a recurring pattern.
    """
    try:
        # Filter transactions by similar amount and same merchant to focus on relevant patterns
        similar_transactions = [
            t
            for t in all_transactions
            if abs(t.amount - transaction.amount) <= transaction.amount * amount_tolerance
            and t.name.upper() == transaction.name.upper()
            and t.date != transaction.date  # Exclude the transaction itself
        ]

        # Need at least 2 transactions to compute intervals
        if len(similar_transactions) < 2:
            return 0.0

        # Sort dates and calculate intervals
        sorted_dates = sorted(parse_date(t.date) for t in similar_transactions if parse_date(t.date) is not None)
        intervals = [
            (sorted_dates[i + 1] - sorted_dates[i]).days
            for i in range(len(sorted_dates) - 1)
            if (sorted_dates[i + 1] - sorted_dates[i]).days > 0
        ]  # Exclude 0-day intervals

        if not intervals:
            return 0.0

        # Define periodicity ranges (with tolerance for real-world variations)
        periodicity_ranges = {
            "weekly": (5, 9),  # 7 ± 2 days
            "biweekly": (12, 16),  # 14 ± 2 days
            "monthly": (26, 34),  # 30 ± 4 days
            "quarterly": (85, 95),  # 90 ± 5 days
            "annual": (350, 380),  # 365 ± 15 days
        }

        # Calculate proportion of intervals in each range
        histogram = {}
        for period, (low, high) in periodicity_ranges.items():
            histogram[period] = sum(1 for i in intervals if low <= i <= high) / len(intervals) if intervals else 0.0

        # Compute periodicity score as the maximum proportion, adjusted for confidence
        max_proportion = max(histogram.values())
        # Normalize by number of intervals to reduce sensitivity to small datasets
        confidence = min(len(intervals) / 12.0, 1.0)  # Expect up to 12 intervals for monthly recurrence
        periodicity_score = max_proportion * confidence

        return max(0.0, min(periodicity_score, 1.0))

    except Exception as e:
        print(f"Error in get_interval_histogram: {e}")
        return 0.0


RECURRING_VENDORS = frozenset([
    # Streaming services
    "netflix",
    "hulu",
    "disney+",
    "spotify",
    "apple music",
    "youtube premium",
    "hbo max",
    "amazon prime",
    "peacock",
    "paramount+",
    "discovery+",
    "crunchyroll",
    "tidal",
    "deezer",
    "apple tv+",
    "pandora",
    "sling",
    "fubo",
    "youtube tv",
    # Utilities and telecom
    "t-mobile",
    "at&t",
    "verizon",
    "sprint",
    "comcast",
    "spectrum",
    "cox",
    "xfinity",
    "centurylink",
    "frontier",
    "dish",
    "directv",
    "optimum",
    "windstream",
    "earthlink",
    "cpsenergy",
    "pg&e",
    "duke energy",
    "conedison",
    "southern california edison",
    "water bill",
    "gas bill",
    "electric bill",
    "waste management",
    "republic services",
    # Software and cloud services
    "microsoft",
    "office365",
    "adobe",
    "aws",
    "amazon web",
    "googlestorage",
    "dropbox",
    "zoom",
    "slack",
    "github",
    "gitlab",
    "atlassian",
    "salesforce",
    "mailchimp",
    "squarespace",
    "wix",
    "godaddy",
    "namecheap",
    "google workspace",
    "shopify",
    "quickbooks",
    "xero",
    # Financial services
    "insurance",
    "progressive",
    "geico",
    "state farm",
    "allstate",
    "farmers",
    "nationwide",
    "usaa",
    "liberty mutual",
    "american family",
    "travelers",
    "loan payment",
    "mortgage",
    "rent",
    "hoa",
    "leasing",
    "credit card annual fee",
    # Memberships
    "gym",
    "fitness",
    "planet fitness",
    "la fitness",
    "gold's gym",
    "24 hour fitness",
    "equinox",
    "lifetime fitness",
    "anytime fitness",
    "ymca",
    "costco",
    "sam's club",
    "aaa",
    "amazon prime membership",
    "bj's",
    "walmart+",
    "instacart",
    # Payment processors (that often handle subscriptions)
    "paypal",
    "stripe",
    "square",
    "adyen",
    "zip.co",
    "afterpay",
    "klarna",
])

# Map common variations to normalized vendor names
VENDOR_ALIASES = {
    # Netflix variations
    "netflix.com": "netflix",
    "netflix monthly": "netflix",
    "netflix subscription": "netflix",
    # Spotify variations
    "spotify.com": "spotify",
    "spotify premium": "spotify",
    "spotify family plan": "spotify",
    # Phone carrier variations
    "t mobile": "t-mobile",
    "tmobile": "t-mobile",
    "at and t": "at&t",
    "att": "at&t",
    "verizon wireless": "verizon",
    "vzw": "verizon",
    # Cable/internet variations
    "xfinity": "comcast",
    "comcast cable": "comcast",
    "spectrum internet": "spectrum",
    "time warner": "spectrum",
    "charter communications": "spectrum",
    # Utilities variations
    "cps energy": "cpsenergy",
    "duke power": "duke energy",
    "con edison": "conedison",
    "so cal edison": "southern california edison",
    # Software variations
    "microsoft365": "microsoft",
    "ms office": "microsoft",
    "adobe creative cloud": "adobe",
    "adobe cc": "adobe",
    "amazon aws": "aws",
    "amazon web services": "aws",
    "google cloud": "googlestorage",
    "gcs": "googlestorage",
    # Streaming service variations
    "disney plus": "disney+",
    "hulu premium": "hulu",
    "youtube music": "youtube premium",
    "hbo": "hbo max",
    "max": "hbo max",
}

# Words commonly found in recurring transaction descriptions
RECURRING_KEYWORDS = frozenset([
    "subscription",
    "monthly",
    "recurring",
    "membership",
    "bill",
    "payment",
    "service",
    "plan",
    "auto-pay",
    "autopay",
    "premium",
    "plus",
    "pro",
    "annual",
    "renewal",
    "utility",
    "internet",
    "phone",
    "mobile",
    "cable",
    "streaming",
])


def has_recurring_keywords(transaction: Transaction) -> bool:
    """
    Check if the transaction description contains keywords typically
    associated with recurring payments.
    """
    name_lower = transaction.name.lower()
    return any(keyword in name_lower for keyword in RECURRING_KEYWORDS)


def is_subscription_amount(amount: float) -> bool:
    """
    Check if an amount matches common subscription price patterns.
    """
    # Common subscription price points (rounded to nearest dollar)
    common_prices = {5, 10, 15, 20, 25, 30, 50, 100}

    # Common price points with cents
    common_prices_cents = {9.99, 4.99, 14.99, 19.99, 29.99, 49.99, 99.99, 7.99, 8.99, 13.99}

    # Check for exact matches to common price points
    rounded = round(amount)
    if rounded in common_prices:
        return True

    # Check for common price points with cents
    return any(abs(amount - price) < 0.01 for price in common_prices_cents)


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int | bool | float]:
    """Get all features for identifying non-recurring transactions."""

    return {
        # Vendor type indicators
        "is_known_recurring": get_is_always_recurring_at(transaction),
        "is_one_time_vendor": get_is_one_time_vendor_at(transaction),
        "is_utility": get_is_utility_at(transaction),
        "is_insurance": get_is_insurance_at(transaction),
        "is_phone": get_is_phone_at(transaction),
        # Vendor characteristics
        "vendor_name_length": len(transaction.name),
        "vendor_name_entropy": get_vendor_name_entropy_at(transaction),
        # Transaction frequency
        "vendor_occurrence_count": get_vendor_occurrence_count_at(transaction, all_transactions),
        "user_vendor_occurrence_count": get_user_vendor_occurrence_count_at(transaction, all_transactions),
        "days_since_last_occurrence": get_days_since_last_occurrence_at(transaction, all_transactions),
        # Amount patterns
        "same_amount_count": get_same_amount_count_at(transaction, all_transactions),
        "similar_amount_count": get_similar_amount_count_at(transaction, all_transactions),
        "amount_uniqueness_score": get_amount_uniqueness_score_at(transaction, all_transactions),
        # Transaction context
        "is_weekend": get_is_weekend_at(transaction),
        "is_month_end": get_is_month_end_at(transaction),
        # Recurring check (for reference)
        "is_recurring_allowance": is_recurring_allowance_at(transaction, all_transactions),
        "is_entertainment": get_is_entertainment_at(transaction),
        "is_food_dining": get_is_food_dining_at(transaction),
        "is_gambling": get_is_gambling_at(transaction),
        "is_gaming": get_is_gaming_at(transaction),
        "is_retail": get_is_retail_at(transaction),
        "is_travel": get_is_travel_at(transaction),
        "has_nonrecurring_keywords": get_contains_common_nonrecurring_keywords_at(transaction),
        "is_recurring_based_on_99_at": is_recurring_based_on_99(transaction, all_transactions),
        "get_interval_variance_coefficient_refine": get_interval_variance_coefficient(transaction, all_transactions),
        "amount_variability_score_refine": amount_variability_score(all_transactions, transaction.name),
        "is_known_recurring_company_refine": is_known_recurring_company(transaction, all_transactions),
        "is_price_trendin_refine": is_price_trending(transaction, all_transactions),
        "get_percent_transactions_same_amount_chris_refine": get_percent_transactions_same_amount_chris(
            transaction, all_transactions, transaction.name
        ),
        "get_n_transactions_same_amount_chris_refine": get_n_transactions_same_amount_chris(
            transaction, all_transactions, transaction.name
        ),
        "get_interval_histogram_refine": get_interval_histogram(transaction, all_transactions),
    }
