import difflib
from datetime import datetime

import numpy as np

from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date


# ===== ORIGINAL FUNCTIONS (KEPT IN PLACE) =====
def get_n_transactions_same_day(transaction: Transaction, all_transactions: list[Transaction], n_days_off: int) -> int:
    transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    transaction_day = transaction_date.day

    count = 0
    for t in all_transactions:
        if t.name == transaction.name:  # Only consider transactions with same name
            t_date = datetime.strptime(t.date, "%Y-%m-%d")
            # Check if day of month is within tolerance, accounting for month boundaries
            day_diff = abs(t_date.day - transaction_day)
            if day_diff <= n_days_off:
                count += 1
            # Special case for month boundaries (e.g., Jan 31 and Feb 1 with n_days_off=1)
            elif (transaction_day > 28 and t_date.day < 3) or (transaction_day < 3 and t_date.day > 28):
                month_diff = abs((t_date.month - transaction_date.month) % 12)
                if month_diff == 1 and (31 - transaction_day + t_date.day) <= n_days_off:
                    count += 1

    return count


def get_n_transactions_days_apart(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> int:
    """
    Get the number of transactions in all_transactions that are within n_days_off of
    being n_days_apart from transaction.
    """
    transaction_date = parse_date(transaction.date)
    count = 0

    for t in all_transactions:
        days_difference = abs((parse_date(t.date) - transaction_date).days)
        if abs(days_difference - n_days_apart) <= n_days_off:
            count += 1

    return count


def get_pct_transactions_days_apart(
    transaction: Transaction,
    all_transactions: list[Transaction],
    n_days_apart: int,
    n_days_off: int,
) -> float:
    """
    Get the percentage of transactions in all_transactions that are within n_days_off
    of being n_days_apart from transaction.
    """
    if not all_transactions:
        return 0.0

    n_transactions = get_n_transactions_days_apart(transaction, all_transactions, n_days_apart, n_days_off)
    return float(n_transactions) / float(len(all_transactions))


def get_pct_transactions_same_day(
    transaction: Transaction, all_transactions: list[Transaction], n_days_off: int
) -> float:
    """
    Get the percentage of transactions in all_transactions that are on the same day of the month as transaction.
    """
    if not all_transactions:
        return 0.0

    n_same_day = get_n_transactions_same_day(transaction, all_transactions, n_days_off)
    return float(n_same_day) / float(len(all_transactions))


def get_is_common_subscription_amount(transaction: Transaction) -> bool:
    common_amounts = {4.99, 5.99, 9.99, 12.99, 14.99, 15.99, 19.99, 49.99, 99.99}
    return transaction.amount in common_amounts


def get_occurs_same_week(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """Checks if the transaction occurs in the same week of the month across multiple months."""
    transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    transaction_week = transaction_date.day // 7  # Determine which week in the month (0-4)

    same_week_count = sum(
        1
        for t in transactions
        if t.name == transaction.name and datetime.strptime(t.date, "%Y-%m-%d").day // 7 == transaction_week
    )

    return same_week_count >= 2  # True if found at least twice


def get_is_similar_name(
    transaction: Transaction, transactions: list[Transaction], similarity_threshold: float = 0.6
) -> bool:
    """Checks if a transaction has a similar name to other past transactions."""
    for t in transactions:
        similarity = difflib.SequenceMatcher(None, transaction.name.lower(), t.name.lower()).ratio()
        if similarity >= similarity_threshold:
            return True  # If a close match is found, return True
    return False


def get_is_fixed_interval(transaction: Transaction, transactions: list[Transaction], margin: int = 1) -> bool:
    """Returns True if a transaction recurs at fixed intervals (weekly, bi-weekly, monthly)."""
    transaction_dates = sorted([
        datetime.strptime(t.date, "%Y-%m-%d") for t in transactions if t.name == transaction.name
    ])

    if len(transaction_dates) < 2:
        return False  # Not enough transactions to determine intervals

    intervals = [(transaction_dates[i] - transaction_dates[i - 1]).days for i in range(1, len(transaction_dates))]
    return all(abs(interval - 30) <= margin for interval in intervals)  # Allow ±1 day for monthly intervals


def get_has_irregular_spike(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """
    Check if the transaction amount is significantly higher than the average amount
    for the same transaction name in the user's transaction history.
    """
    similar_transactions = [t for t in transactions if t.name == transaction.name]
    if not similar_transactions:
        return False

    average_amount = sum(t.amount for t in similar_transactions) / len(similar_transactions)
    return transaction.amount > average_amount * 1.5  # Spike threshold: 50% higher than average


def get_is_first_of_month(transaction: Transaction) -> bool:
    """
    Checks if a transaction occurs on the first day of the month.
    """
    return transaction.date.split("-")[2] == "01"


# ===== NEW FEATURES ADDED BELOW =====
def get_is_weekday_consistent(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """Check if transaction consistently occurs on the same weekday"""
    same_name_txns = [t for t in transactions if t.name == transaction.name]
    if len(same_name_txns) < 2:
        return False

    transaction_weekday = datetime.strptime(transaction.date, "%Y-%m-%d").weekday()
    return all(
        datetime.strptime(t.date, "%Y-%m-%d").weekday() == transaction_weekday for t in same_name_txns[-3:]
    )  # Check last 3 occurrences


def get_is_seasonal(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """Detect seasonal/annual payments"""
    same_name_txns = [t for t in transactions if t.name == transaction.name]
    if len(same_name_txns) < 2:
        return False

    dates = [datetime.strptime(t.date, "%Y-%m-%d") for t in same_name_txns]
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    return all(360 <= interval <= 370 for interval in intervals)


def get_amount_variation(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Calculate coefficient of variation for amounts."""
    same_name_txns = [t for t in transactions if t.name == transaction.name]
    if len(same_name_txns) < 2:
        return 0.0

    amounts = [t.amount for t in same_name_txns]
    mean = sum(amounts) / len(amounts)
    std_dev = (sum((x - mean) ** 2 for x in amounts) / len(amounts)) ** 0.5
    return float((std_dev / mean) * 100) if mean != 0 else 0.0


def get_has_trial_period(transaction: Transaction, transactions: list[Transaction]) -> bool:
    """Detect potential free trial periods"""
    same_name_txns = sorted([t for t in transactions if t.name == transaction.name], key=lambda x: x.date)
    return len(same_name_txns) >= 2 and same_name_txns[0].amount == 0 and all(t.amount > 0 for t in same_name_txns[1:])


def get_description_pattern(transaction: Transaction) -> str:
    """Extract payment pattern from description"""
    desc = transaction.name.lower()
    patterns = {
        "ach": "ach" in desc,
        "auto": "auto" in desc or "autopay" in desc,
        "recurring": "recur" in desc,
        "invoice": "inv" in desc or "invoice" in desc,
    }
    return next((k for k, v in patterns.items() if v), "other")


def get_is_weekend_transaction(transaction: Transaction) -> bool:
    """Check if transaction occurs on weekend"""
    return datetime.strptime(transaction.date, "%Y-%m-%d").weekday() >= 5


def get_merchant_fingerprint(transaction: Transaction, transactions: list[Transaction]) -> float:
    """Identifies unique merchant patterns using multiple characteristics."""
    same_merchant = [t for t in transactions if t.name == transaction.name]

    # Calculate stability scores (0-1)
    if len(same_merchant) > 1:
        amounts = [t.amount for t in same_merchant]
        days = [datetime.strptime(t.date, "%Y-%m-%d").day for t in same_merchant]
        # Penalize amount variation more strongly
        amount_stability = 1 - min(1, (float(np.std(amounts)) / (float(np.mean(amounts)) + 1e-6)) ** 1.5)
        day_stability = 1 - (float(np.std(days)) / 15)
    else:
        amount_stability = 0
        day_stability = 0

    # Payment method clues
    method_score = 0.5 if any("ach" in t.name.lower() or "autopay" in t.name.lower() for t in same_merchant) else 0

    # Adjusted weights: make perfect patterns score high
    return float(max(0.0, min(1.0, (amount_stability * 0.7) + (day_stability * 0.2) + (method_score * 0.1))))


def get_recurrence_confidence_score(transaction: Transaction, transactions: list[Transaction]) -> float:
    """
    Calculates a 0-1 confidence score combining:
    - Temporal consistency
    - Amount patterns
    - Merchant trust signals
    - Behavioral history
    """
    same_merchant = [t for t in transactions if t.name == transaction.name]

    if len(same_merchant) < 2:
        return 0.0

    amounts = [t.amount for t in same_merchant]
    days = [datetime.strptime(t.date, "%Y-%m-%d").day for t in same_merchant]

    # Stronger penalty for amount variation
    amount_stability = 1 - min(1, (float(np.std(amounts)) / (float(np.mean(amounts)) + 1e-6)) ** 3.0)
    day_stability = 1 - (float(np.std(days)) / 15)

    # Payment method clues
    method_score = 0.5 if any("ach" in t.name.lower() or "autopay" in t.name.lower() for t in same_merchant) else 0

    # Special case: only two transactions and large differences
    if len(same_merchant) == 2 and (abs(amounts[0] - amounts[1]) > 0.5 * max(amounts) or abs(days[0] - days[1]) > 10):
        return 0.0

    # Adjusted weights: penalize amount variation much more
    return float(max(0.0, min(1.0, (amount_stability * 0.85) + (day_stability * 0.05) + (method_score * 0.1))))


def get_transaction_trust_score(transaction: Transaction, transactions: list[Transaction]) -> float:
    """
    Calculates a 0-1 score focusing on precision by verifying:
    1. Merchant reputation
    2. Amount validity
    3. Temporal plausibility
    4. Behavioral patterns
    """
    same_merchant = [t for t in transactions if t.name == transaction.name]

    # Base score components
    trust_signals = {
        "merchant_reputation": 0.0,
        "amount_validation": 0.0,
        "temporal_plausibility": 0.0,
        "behavioral_consistency": 0.0,
    }

    # 1. Merchant Reputation (30% weight)
    trusted_merchants = {"netflix", "spotify", "amazon prime", "mortgage", "rent"}
    if any(m in transaction.name.lower() for m in trusted_merchants):
        trust_signals["merchant_reputation"] = 1.0
    elif "ach" in transaction.name.lower():
        trust_signals["merchant_reputation"] = 0.8

    # 2. Amount Validation (25% weight)
    if transaction.amount > 0:  # Negative amounts often indicate refunds
        if 4.99 <= transaction.amount <= 299.99:  # Common subscription range
            trust_signals["amount_validation"] = 1.0 if transaction.amount % 1 in {0, 0.99, 0.95} else 0.7
        elif 0 < transaction.amount < 1000:  # Plausible subscription range
            trust_signals["amount_validation"] = 0.7

    # 3. Temporal Plausibility (25% weight)
    if len(same_merchant) >= 2:
        dates = sorted([datetime.strptime(t.date, "%Y-%m-%d") for t in same_merchant])
        intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
        if all(15 <= i <= 45 for i in intervals):  # Valid recurring range
            trust_signals["temporal_plausibility"] = 1.0

    # 4. Behavioral Consistency (20% weight)
    desc = transaction.name.lower()
    if any(kw in desc for kw in {"subscription", "membership", "renewal"}):
        trust_signals["behavioral_consistency"] = 1.0
    elif "payment" in desc:
        trust_signals["behavioral_consistency"] = 0.8

    # Calculate weighted score
    weights = {
        "merchant_reputation": 0.3,
        "amount_validation": 0.25,
        "temporal_plausibility": 0.25,
        "behavioral_consistency": 0.2,
    }
    return sum(trust_signals[s] * weights[s] for s in trust_signals)


def get_recurring_confidence(transaction: Transaction, transactions: list[Transaction]) -> float:
    """
    Calculates a 0-1 confidence score for recurring transactions by:
    1. Analyzing payment intervals with natural variance allowance
    2. Checking amount consistency with seasonal fluctuations
    3. Validating merchant patterns
    """
    same_merchant = [t for t in transactions if t.name == transaction.name]
    if len(same_merchant) < 2:
        return 0.0

    # 1. Interval Analysis (Allows ±7 day variance)
    dates = sorted(datetime.strptime(t.date, "%Y-%m-%d") for t in same_merchant)
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    if not intervals:
        return 0.0
    avg_interval = sum(intervals) / len(intervals)
    interval_var = max(abs(i - avg_interval) for i in intervals)
    interval_score = max(0.0, 1 - (interval_var / 30) ** 2)

    # 2. Amount consistency (relative difference)
    amounts = [t.amount for t in same_merchant]
    amount_var = max(amounts) - min(amounts)
    amount_score = max(0.0, 1 - (amount_var / (min(amounts) + 1e-6)) ** 2)

    # 3. Merchant pattern (bonus for keywords)
    name = transaction.name.lower()
    merchant_bonus = (
        0.05 if any(kw in name for kw in ["autopay", "subscription", "prime", "netflix", "spotify"]) else 0.0
    )

    # Special case: only two transactions and large differences
    if len(same_merchant) == 2 and (abs(amounts[0] - amounts[1]) > 0.5 * max(amounts) or abs(intervals[0] - 30) > 20):
        return 0.0

    # Weighted sum
    return min(1.0, max(0.0, 0.5 * interval_score + 0.45 * amount_score + merchant_bonus))


def get_amount_mad(transaction: Transaction, transactions: list[Transaction]) -> float:
    """
    Calculate the Median Absolute Deviation (MAD) relative to median amount.
    This is more robust to outliers than standard deviation.
    """
    same_name_txns = [t for t in transactions if t.name == transaction.name]
    if len(same_name_txns) < 2:
        return 0.0

    amounts = sorted([t.amount for t in same_name_txns])
    median = amounts[len(amounts) // 2]

    # Calculate absolute deviations from median
    abs_deviations = [abs(amount - median) for amount in amounts]
    mad = sorted(abs_deviations)[len(abs_deviations) // 2]  # Median of absolute deviations

    return float((mad / median) * 100) if median != 0 else 0.0


def get_amount_roundness(transaction: Transaction) -> float:
    """
    Returns 1 if amount ends in .00/.99, 0.5 for .95, 0 otherwise.
    Common in subscriptions.
    """
    cents = round(transaction.amount % 1, 2)
    if cents in {0.00, 0.99}:
        return 1.0
    elif cents == 0.95:
        return 0.5
    return 0.0


def get_vendor_risk_keywords(vendor_name: str, risk_keywords: set[str] | None = None) -> bool:
    """
    Args:
        vendor_name (str): Vendor name.
        risk_keywords (set): Keywords indicating high risk.
    Returns:
        bool: True if any keyword is found in vendor_name.
    """
    if risk_keywords is None:
        risk_keywords = {"Lending", "Payday", "Advance"}
    return any(keyword.lower() in vendor_name.lower() for keyword in risk_keywords)


def get_vendor_trust_score(vendor_name: str, trusted_vendors: set[str], high_risk_vendors: set[str]) -> float:
    """
    Args:
        vendor_name: Name of the vendor.
        trusted_vendors: Predefined trusted vendors (e.g., {"Apple", "AT&T"}).
        high_risk_vendors: Predefined high-risk vendors (e.g., {"AfterPay", "CreditNinja"}).
    Returns:
        1.0 (trusted), 0.1 (high risk), 0.5 (neutral).
    """
    if vendor_name in trusted_vendors:
        return 1.0
    if vendor_name in high_risk_vendors:
        return 0.1
    return 0.5


def get_is_recurring_charge(
    vendor_name: str, user_id: str, transaction_history: dict[str, list[dict[str, int | str]]]
) -> bool:
    """
    Args:
        vendor_name: Vendor name.
        user_id: User ID.
        transaction_history: {user_id: [{"vendor": str, "days_ago": int}, ...]}.
    Returns:
        True if same vendor appears >=2 times in last 30 days.
    """
    user_txns = transaction_history.get(user_id, [])
    recent_txns = [t for t in user_txns if int(t["days_ago"]) <= 30 and t["vendor"] == vendor_name]
    return len(recent_txns) >= 2


def is_apple_subscription_service(transaction_name: str) -> bool:
    """
    Args:
        transaction_name: Vendor name or transaction description
    Returns:
        True if this is a known Apple subscription service
    """
    apple_services = {
        "Apple Music",
        "Apple TV+",
        "Apple Arcade",
        "iCloud",
        "Apple Fitness+",
        "Apple News+",
        "Apple One",
    }
    return any(service.lower() in transaction_name.lower() for service in apple_services)


def apple_transaction_amount_profile(amount: float) -> float:
    """
    Args:
        amount: Transaction amount
    Returns:
        1.0 if amount matches common Apple pattern, 0.0 if suspicious
    """
    common_amounts = {0.99, 1.99, 2.99, 4.99, 9.99, 14.99, 19.99, 29.99}
    return 1.0 if amount in common_amounts else 0.0


def get_new_features(
    transaction: Transaction, all_transactions: list[Transaction]
) -> dict[str, float | int | bool | str]:
    """
    Return a dictionary containing only the new features for the given transaction.
    """
    return {
        "is_weekday_consistent": get_is_weekday_consistent(transaction, all_transactions),
        "is_seasonal": get_is_seasonal(transaction, all_transactions),
        "amount_variation_pct": get_amount_variation(transaction, all_transactions),
        "had_trial_period": get_has_trial_period(transaction, all_transactions),
        "description_pattern": get_description_pattern(transaction),
        "is_weekend_transaction": get_is_weekend_transaction(transaction),
        "n_days_apart_30": get_n_transactions_days_apart(transaction, all_transactions, 30, 2),
        "pct_days_apart_30": get_pct_transactions_days_apart(transaction, all_transactions, 30, 2),
        "merchant_fingerprint": get_merchant_fingerprint(transaction, all_transactions),
        "recurrence_confidence": get_recurrence_confidence_score(transaction, all_transactions),
        "transaction_trust": get_transaction_trust_score(transaction, all_transactions),
        "recurring_confidence": get_recurring_confidence(transaction, all_transactions),
        "amount_mad_pct": get_amount_mad(transaction, all_transactions),
        "amount_roundness": get_amount_roundness(transaction),
        "vendor_risk_keywords": get_vendor_risk_keywords(transaction.name),
        "vendor_trust_score": get_vendor_trust_score(transaction.name, {"Apple", "AT&T"}, {"AfterPay", "CreditNinja"}),
        "is_recurring_charge": get_is_recurring_charge(transaction.name, transaction.user_id, {}),
        "is_apple_subscription_service": is_apple_subscription_service(transaction.name),
        "apple_transaction_amount_profile": apple_transaction_amount_profile(transaction.amount),
    }
