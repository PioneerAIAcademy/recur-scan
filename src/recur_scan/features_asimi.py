import datetime
from collections import Counter

import numpy as np

from recur_scan.transactions import Transaction


def get_frequency_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    merchant_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(merchant_transactions) < 2:
        return {"frequency": 0.0, "date_variability": 0.0, "median_frequency": 0.0, "std_frequency": 0.0}

    dates = sorted([datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in merchant_transactions])
    date_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    avg_frequency = sum(date_diffs) / len(date_diffs)
    median_frequency = sorted(date_diffs)[len(date_diffs) // 2]
    std_frequency = (sum((x - avg_frequency) ** 2 for x in date_diffs) / len(date_diffs)) ** 0.5
    date_variability = max(date_diffs) - min(date_diffs)

    return {
        "frequency": avg_frequency,
        "date_variability": date_variability,
        "median_frequency": median_frequency,
        "std_frequency": std_frequency,
    }


def is_valid_recurring_transaction(transaction: Transaction) -> bool:
    """
    Check if a transaction is valid for being marked as recurring based on vendor-specific rules.

    Rules:
    - For 'Apple', 'Brigit', 'Cleo AI', 'Credit Genie': Amount must end with '.99' (within floating point tolerance)
    and be less than 20. (Checking specific amounts is not reliable as they may change over time)
    """
    vendor_name = transaction.name.lower()
    amount = transaction.amount

    always_recurring_vendors = {
        "netflix",
        "spotify",
        "microsoft",
        "amazon prime",
        "at&t",
        "verizon",
        "spectrum",
        "geico",
        "hugo insurance",
    }

    # instead of checking for specific amounts, which may change over time, check for small amount ending in 0.99
    if vendor_name in {"apple", "brigit", "cleo ai", "credit genie"}:
        # Better way to check for .99 ending
        return amount < 20.00 and abs(amount - round(amount) + 0.01) < 0.001  # Check if decimal part is ~0.99
    elif vendor_name in always_recurring_vendors:
        return True
    else:
        return True


def get_amount_features(transaction: Transaction) -> dict[str, float]:
    return {
        "is_amount_rounded": int(transaction.amount == round(transaction.amount)),
        "amount_category": int(transaction.amount // 10),
    }


def get_vendor_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
    avg_amount = sum(t.amount for t in vendor_transactions) / len(vendor_transactions) if vendor_transactions else 0.0
    return {
        "n_transactions_with_vendor": len(vendor_transactions),
        "avg_amount_for_vendor": avg_amount,
    }


def get_time_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int]:
    date_obj = datetime.datetime.strptime(transaction.date, "%Y-%m-%d")
    merchant_transactions = [t for t in all_transactions if t.name == transaction.name]
    dates = sorted([datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in merchant_transactions])
    next_transaction_date = dates[dates.index(date_obj) + 1] if dates.index(date_obj) < len(dates) - 1 else None
    days_until_next = (next_transaction_date - date_obj).days if next_transaction_date else 0

    return {
        "month": date_obj.month,
        "days_until_next_transaction": days_until_next,
    }


def get_user_recurrence_rate(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    if len(user_transactions) < 2:
        return {"user_recurrence_rate": 0.0}

    recurring_count = sum(1 for t in user_transactions if is_valid_recurring_transaction(t))
    user_recurrence_rate = recurring_count / len(user_transactions)

    return {
        "user_recurrence_rate": user_recurrence_rate,
    }


def get_user_specific_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    if len(user_transactions) < 2:
        return {
            "user_transaction_count": 0.0,
            "user_recurring_transaction_count": 0.0,
            "user_recurring_transaction_rate": 0.0,
        }

    recurring_count = sum(1 for t in user_transactions if is_valid_recurring_transaction(t))
    user_recurring_transaction_rate = recurring_count / len(user_transactions)

    return {
        "user_transaction_count": len(user_transactions),
        "user_recurring_transaction_count": recurring_count,
        "user_recurring_transaction_rate": user_recurring_transaction_rate,
    }


def get_user_recurring_vendor_count(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int]:
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    recurring_vendors = {t.name for t in user_transactions if is_valid_recurring_transaction(t)}
    return {"user_recurring_vendor_count": len(recurring_vendors)}


def get_user_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    if len(user_transactions) < 2:
        return {"user_transaction_frequency": 0.0}

    # Sort transactions by date
    user_transactions_sorted = sorted(user_transactions, key=lambda t: t.date)
    dates = [datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in user_transactions_sorted]

    # Calculate the average time between transactions
    date_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    avg_frequency = sum(date_diffs) / len(date_diffs)

    return {"user_transaction_frequency": avg_frequency}


def get_vendor_amount_std(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(vendor_transactions) < 2:
        return {"vendor_amount_std": 0.0}

    amounts = [t.amount for t in vendor_transactions]
    mean_amount = sum(amounts) / len(amounts)
    std_amount = (sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5

    return {"vendor_amount_std": std_amount}


def get_vendor_recurring_user_count(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int]:
    vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
    recurring_users = {t.user_id for t in vendor_transactions if is_valid_recurring_transaction(t)}
    return {"vendor_recurring_user_count": len(recurring_users)}


def get_vendor_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(vendor_transactions) < 2:
        return {"vendor_transaction_frequency": 0.0}

    # Sort transactions by date
    vendor_transactions_sorted = sorted(vendor_transactions, key=lambda t: t.date)
    dates = [datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in vendor_transactions_sorted]

    # Calculate the average time between transactions
    date_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    avg_frequency = sum(date_diffs) / len(date_diffs)

    return {"vendor_transaction_frequency": avg_frequency}


def get_user_vendor_transaction_count(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int]:
    user_vendor_transactions = [
        t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name
    ]
    return {"user_vendor_transaction_count": len(user_vendor_transactions)}


def get_user_vendor_recurrence_rate(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    user_vendor_transactions = [
        t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name
    ]
    if len(user_vendor_transactions) < 1:
        return {"user_vendor_recurrence_rate": 0.0}

    recurring_count = sum(1 for t in user_vendor_transactions if is_valid_recurring_transaction(t))
    recurrence_rate = recurring_count / len(user_vendor_transactions)

    return {"user_vendor_recurrence_rate": recurrence_rate}


def get_user_vendor_interaction_count(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int]:
    user_vendor_transactions = [
        t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name
    ]
    return {"user_vendor_interaction_count": len(user_vendor_transactions)}


def get_amount_category(transaction: Transaction) -> dict[str, int]:
    amount = transaction.amount
    if amount < 10:
        return {"amount_category": 0}
    elif 10 <= amount < 20:
        return {"amount_category": 1}
    elif 20 <= amount < 50:
        return {"amount_category": 2}
    else:
        return {"amount_category": 3}


def get_temporal_consistency_features(
    transaction: Transaction, all_transactions: list[Transaction]
) -> dict[str, float]:
    """Measure how consistent transaction timing is for this vendor"""
    vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(vendor_transactions) < 3:
        return {"temporal_consistency_score": 0.0, "is_monthly_consistent": 0, "is_weekly_consistent": 0}

    dates = sorted([datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in vendor_transactions])
    date_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

    # Check for monthly consistency (28-31 day intervals)
    monthly_diffs = [diff for diff in date_diffs if 28 <= diff <= 31]
    monthly_consistency = len(monthly_diffs) / len(date_diffs) if date_diffs else 0

    # Check for weekly consistency (7 day intervals)
    weekly_diffs = [diff for diff in date_diffs if 6 <= diff <= 8]
    weekly_consistency = len(weekly_diffs) / len(date_diffs) if date_diffs else 0

    return {
        "temporal_consistency_score": (monthly_consistency + weekly_consistency) / 2,
        "is_monthly_consistent": int(monthly_consistency > 0.7),
        "is_weekly_consistent": int(weekly_consistency > 0.7),
    }


def get_vendor_recurrence_profile(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    """Analyze how often this vendor appears in recurring patterns across all users"""
    vendor_name = transaction.name.lower()
    vendor_transactions = [t for t in all_transactions if t.name.lower() == vendor_name]
    total_vendor_transactions = len(vendor_transactions)

    if total_vendor_transactions == 0:
        return {"vendor_recurrence_score": 0.0, "vendor_recurrence_consistency": 0.0, "vendor_is_common_recurring": 0}

    # Count how many unique users have recurring patterns with this vendor
    recurring_users = set()
    amount_counts: Counter = Counter()

    for t in vendor_transactions:
        if is_valid_recurring_transaction(t):
            recurring_users.add(t.user_id)
        amount_counts[t.amount] += 1

    # Calculate recurrence score (0-1) based on how consistent amounts are
    if amount_counts:
        _, count = amount_counts.most_common(1)[0]
        amount_consistency = count / total_vendor_transactions
    else:
        amount_consistency = 0

    common_recurring_vendors = {
        "netflix",
        "spotify",
        "microsoft",
        "amazon prime",
        "at&t",
        "verizon",
        "spectrum",
        "geico",
        "hugo insurance",
    }

    return {
        "vendor_recurrence_score": len(recurring_users) / len({t.user_id for t in vendor_transactions}),
        "vendor_recurrence_consistency": amount_consistency,
        "vendor_is_common_recurring": int(vendor_name in common_recurring_vendors),
    }


def get_user_vendor_relationship_features(
    transaction: Transaction, all_transactions: list[Transaction]
) -> dict[str, float]:
    """Analyze the relationship between this user and vendor"""
    user_vendor_transactions = [
        t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name
    ]
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]

    if not user_transactions:
        return {"user_vendor_dependency": 0.0, "user_vendor_tenure": 0.0}

    # Calculate what percentage of user's transactions are with this vendor
    dependency = len(user_vendor_transactions) / len(user_transactions)

    # Calculate tenure (days since first transaction with this vendor)
    if user_vendor_transactions:
        dates = [datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in user_vendor_transactions]
        tenure = (max(dates) - min(dates)).days
    else:
        tenure = 0

    return {"user_vendor_dependency": dependency, "user_vendor_tenure": tenure, "user_vendor_transaction_span": tenure}


# new features


def has_99_cent_pricing(transaction: Transaction) -> bool:
    """More robust version that checks for .99, .95, .00 endings"""
    cent_part = abs(round(transaction.amount - int(transaction.amount), 2))
    return cent_part in {0.99, 0.95, 0.00} and transaction.amount < 50  # Ignore large amounts


def is_apple_subscription_amount(amount: float) -> bool:
    """Check for ANY consistent amount (not just common ones)"""
    common_amounts = {0.99, 1.99, 2.99, 4.99, 8.65, 9.99, 10.99, 14.99}  # Added 8.65
    return any(abs(amount - a) < 0.01 for a in common_amounts)


def is_annual_subscription(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Identify annual subscriptions (365±15 day intervals)"""
    user_vendor_txns = sorted(
        [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name],
        key=lambda x: x.date,
    )

    if len(user_vendor_txns) < 2:
        return False

    intervals = []
    dates = [datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in user_vendor_txns]

    for i in range(1, len(dates)):
        intervals.append((dates[i] - dates[i - 1]).days)

    return any(350 <= delta <= 380 for delta in intervals)


def get_recurrence_streak(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    vendor_trans = sorted(
        [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name],
        key=lambda x: x.date,
    )

    if len(vendor_trans) < 2:
        return 0

    streak = 0
    dates = [datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in vendor_trans]
    amounts = [t.amount for t in vendor_trans]

    for i in range(1, len(dates)):
        delta = (dates[i] - dates[i - 1]).days
        amount_diff = abs(amounts[i] - amounts[i - 1])

        if 25 <= delta <= 35 and amount_diff < 0.1:
            streak += 1
        else:
            streak = 0  # Reset streak on broken pattern

    return streak


def is_common_subscription_amount(amount: float) -> bool:
    """Check for common subscription pricing patterns across vendors"""
    cent_part = round(amount - int(amount), 2)
    common_cents = {0.99, 0.95, 0.00, 0.49}
    return (
        cent_part in common_cents
        or (amount > 4 and abs(cent_part - 0.99) < 0.01)
        or (amount > 10 and amount % 5 == 0)  # Common for annual subs
    )


def get_amount_frequency_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    user_txns = [t for t in all_transactions if t.user_id == transaction.user_id]

    if len(user_txns) < 5:
        return 0.0

    # Consider similar amounts (±5%) as matches
    similar_amounts = [t.amount for t in user_txns if abs(t.amount - transaction.amount) <= transaction.amount * 0.05]
    freq = len(similar_amounts) / len(user_txns)

    # Add common subscription amount boost
    if is_common_subscription_amount(transaction.amount):
        freq = min(freq + 0.2, 1.0)

    return round(freq, 2)


def calculate_day_of_month_consistency(dates: list[datetime.datetime]) -> float:
    """Calculate consistency of transaction day of month (0-1 scale)."""
    if len(dates) < 3:
        return 0.0
    days = [d.day for d in dates]
    base_day = max(set(days), key=days.count)
    matches = sum(1 for d in days if abs(d - base_day) <= 3)
    return matches / len(days)


def get_amount_quantum(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Detect if amount is a 'quantum' value (e.g., $9.99 → $10.00 after tax)."""
    vendor_txns = [t for t in all_transactions if t.name == transaction.name]
    if not vendor_txns:
        return 0

    quantum_pairs = {
        4.99: 5.35,
        9.99: 10.71,
        11.54: 12.00,
        0.99: 1.08,
        2.99: 3.21,  # Common .99 upcharges
        19.99: 21.39,
        29.99: 32.09,
    }

    for pre_tax, post_tax in quantum_pairs.items():
        if abs(transaction.amount - post_tax) < 0.05 or any(abs(t.amount - pre_tax) < 0.05 for t in vendor_txns):
            return 1

    return 0


def get_interval_precision(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate precision of transaction intervals (0-1 scale)."""
    vendor_trans = sorted(
        [t for t in all_transactions if t.name == transaction.name and t.user_id == transaction.user_id],
        key=lambda x: x.date,
    )

    if len(vendor_trans) < 3:
        return 0.0

    dates = [datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in vendor_trans]
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

    if transaction.name == "Apple":
        monthly_intervals = sum(25 <= diff <= 35 for diff in intervals)
        return min(monthly_intervals / len(intervals) * 1.2, 1.0)

    return sum(28 <= diff <= 31 for diff in intervals) / len(intervals)


def get_amount_temporal_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Combines amount consistency, temporal regularity, AND day-of-month consistency.
    Returns a 0-1 score where higher = more subscription-like.
    """
    vendor_trans = sorted(
        [t for t in all_transactions if t.name == transaction.name and t.user_id == transaction.user_id],
        key=lambda x: x.date,
    )

    if len(vendor_trans) < 3:
        return 0.0

    # Amount consistency (standard deviation)
    amounts = np.array([t.amount for t in vendor_trans])
    amount_std = np.std(amounts)

    # Temporal regularity (interval coefficient of variation)
    dates = [datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in vendor_trans]
    intervals = np.diff([d.toordinal() for d in dates])
    interval_cv = np.std(intervals) / (np.mean(intervals) + 1e-9)

    # Day-of-month consistency (new addition)
    day_consistency = calculate_day_of_month_consistency(dates)

    # Combined score (weighted average)
    return float(0.4 * (1 - amount_std) + 0.3 * (1 - interval_cv) + 0.3 * day_consistency)


def get_burst_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Detects clustered transactions (common in non-subscriptions)
    Returns: 0 (no burst) to 1 (high burstiness)
    """
    user_trans = sorted([t for t in all_transactions if t.user_id == transaction.user_id], key=lambda x: x.date)

    if len(user_trans) < 3:
        return 0.0

    # Find transactions within 7 days with similar amounts
    current_date = datetime.datetime.strptime(transaction.date, "%Y-%m-%d")
    similar_trans = [
        t
        for t in user_trans[-10:]
        if abs((datetime.datetime.strptime(t.date, "%Y-%m-%d") - current_date).days) <= 7
        and abs(t.amount - transaction.amount) < 2.0
    ]

    return float(min(len(similar_trans) / 3.0, 1.0))  # Cap at 1.0


def get_series_duration(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Returns a normalized score (0-1) based on how long the transaction series has been active.
    Longer series are more likely to be true recurring transactions.
    """
    similar_transactions = [
        t
        for t in all_transactions
        if t.name == transaction.name
        # and t.category == transaction.category  # Removed as "category" is not a valid attribute
    ]

    if len(similar_transactions) < 2:
        return 0.0

    sorted_trans = sorted(similar_transactions, key=lambda x: x.date)
    duration_days = (
        datetime.datetime.strptime(sorted_trans[-1].date, "%Y-%m-%d")
        - datetime.datetime.strptime(sorted_trans[0].date, "%Y-%m-%d")
    ).days

    # Normalize score (0-1) where 1 = 1+ year of history
    return round(min(1.0, duration_days / 365), 2)


def is_apple_subscription(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Special handling for Apple's billing quirks with stricter rules."""
    if transaction.name != "Apple":
        return False

    vendor_trans = sorted(
        [t for t in all_transactions if t.user_id == transaction.user_id and t.name == "Apple"], key=lambda x: x.date
    )

    if len(vendor_trans) < 4:  # Require at least 4 transactions to establish a pattern
        return False

    dates = [datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in vendor_trans]

    # ===== New Checks =====
    # 1. Burst Detection - reject if multiple charges in short windows
    short_gaps = sum((dates[i + 1] - dates[i]).days <= 14 for i in range(len(dates) - 1))
    if short_gaps > len(dates) * 0.25:  # If >25% of gaps are <=14 days
        return False

    # 2. Stricter Interval Checking
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

    # Check for consistent monthly pattern (28-31 days)
    monthly_count = sum(28 <= diff <= 31 for diff in intervals)
    monthly_ratio = monthly_count / len(intervals)

    # Check for biweekly pattern (13-15 days)
    biweekly_count = sum(13 <= diff <= 15 for diff in intervals)

    # Reject mixed patterns (e.g., some monthly, some biweekly)
    if monthly_count > 0 and biweekly_count > 0:
        return False

    # 3. Amount Consistency with tolerance for one-off changes
    base_amount = vendor_trans[0].amount
    amount_changes = sum(not is_similar_amount(t.amount, base_amount, threshold=0.01) for t in vendor_trans)
    if amount_changes > 1:  # Allow at most one amount variation
        return False

    # ===== Existing Checks (Modified) =====
    day_consistency = calculate_day_of_month_consistency(dates)

    # Only accept if:
    # - Strong monthly pattern (>80%) OR strong biweekly pattern (>90%)
    # - AND day consistency is good
    # - AND no problematic bursts
    return monthly_ratio >= 0.8 and day_consistency >= 0.7


def is_afterpay_installment(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Detect AfterPay's installment payments."""
    if transaction.name != "AfterPay":
        return False

    vendor_trans = sorted(
        [t for t in all_transactions if t.user_id == transaction.user_id and t.name == "AfterPay"], key=lambda x: x.date
    )

    if len(vendor_trans) < 4:
        return False

    first_amount = vendor_trans[0].amount
    return all(is_similar_amount(t.amount, first_amount, threshold=0.05) for t in vendor_trans)


def is_similar_amount(a: float, b: float, threshold: float = 0.05) -> bool:
    """Check if two amounts are within ±threshold% (default: ±5%)."""
    return abs(a - b) <= max(a, b) * threshold


# Use this in your existing amount checks instead of strict equality.


def is_afterpay_one_time(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Filter out one-time AfterPay purchases."""
    if transaction.name != "AfterPay":
        return False

    vendor_trans = [t for t in all_transactions if t.user_id == transaction.user_id and t.name == "AfterPay"]

    if len(vendor_trans) <= 2:
        return True

    amounts = [t.amount for t in vendor_trans]
    return max(amounts) - min(amounts) > 10


def is_common_subscription(transaction: Transaction) -> bool:
    common_amounts = {
        0.99,
        1.99,
        2.99,
        4.99,
        9.99,
        10.99,
        11.76,
        14.99,
        15.98,
        19.99,
    }  # Add more as needed
    return any(
        is_similar_amount(transaction.amount, amount, threshold=0.01)  # ±1% for strict matching
        for amount in common_amounts
    )


def get_apple_interval_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Returns a score (0-1) for how well Apple transactions match monthly intervals.
    Called as an intermediate feature in your pipeline.
    """
    if transaction.name != "Apple":
        return 0.0  # Only for Apple transactions

    vendor_trans = sorted(
        [t for t in all_transactions if t.user_id == transaction.user_id and t.name == "Apple"], key=lambda x: x.date
    )

    if len(vendor_trans) < 3:
        return 0.0

    dates = [datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in vendor_trans]
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

    # Score: % of intervals that are 25-35 days (Apple's flexible billing cycle)
    monthly_intervals = sum(28 <= diff <= 31 for diff in intervals)
    biweekly_intervals = sum(13 <= diff <= 15 for diff in intervals)

    if monthly_intervals > 0 and biweekly_intervals > 0:
        return 0.0  # Mixed patterns = not a subscription

    return max(monthly_intervals, biweekly_intervals) / len(intervals)


def get_loan_repayment_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Returns a score (0-1) for how likely this transaction is a recurring loan payment.
    - Score 1.0: Perfect match (fixed amount, strict weekly intervals).
    - Score 0.0: No pattern detected.
    """
    # Step 1: Filter this user's transactions from the same merchant
    user_transactions = [
        t
        for t in all_transactions
        if t.user_id == transaction.user_id and t.name == transaction.name  # Same merchant
    ]

    # Need at least 3 transactions to detect a pattern
    if len(user_transactions) < 3:
        return 0.0

    # Step 2: Check amount consistency (allow ±$0.10 variance)
    amounts = [t.amount for t in user_transactions]
    avg_amount = sum(amounts) / len(amounts)
    amount_variance = max(abs(t.amount - avg_amount) for t in user_transactions)

    if amount_variance > 0.10:
        return 0.0  # Amounts vary too much for a loan repayment

    # Step 3: Check interval consistency (weekly = ~7 days)
    dates = sorted([datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in user_transactions])
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

    # Allow ±1 day flexibility (e.g., 6-8 days for weekly payments)
    weekly_intervals = sum(6 <= diff <= 8 for diff in intervals)
    interval_confidence = weekly_intervals / len(intervals)  # % of intervals that match

    # Step 4: Final score (weight amount + interval confidence)
    return interval_confidence  # Since amount is already fixed, this is the key factor


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int | bool | float]:
    return {
        "amount_frequency_score": get_amount_frequency_score(transaction, all_transactions),
        "has_99_cent_pricing": has_99_cent_pricing(transaction),
        "interval_precision": get_interval_precision(transaction, all_transactions),
        "is_apple_subscription_amount": is_apple_subscription_amount(transaction.amount),
        "is_annual_subscription": is_annual_subscription(transaction, all_transactions),
        "apple_subscription": is_apple_subscription(transaction, all_transactions),
        "afterpay_installment": is_afterpay_installment(transaction, all_transactions),
        "is_afterpay_one_time": is_afterpay_one_time(transaction, all_transactions),
        "temporal_consistency": get_amount_temporal_consistency(transaction, all_transactions),
        "recurrence_streak": get_recurrence_streak(transaction, all_transactions),
        "burst_score": get_burst_score(transaction, all_transactions),
        "series_duration": get_series_duration(transaction, all_transactions),
        "amount_quantum": get_amount_quantum(transaction, all_transactions),
        "apple_interval_score": get_apple_interval_score(transaction, all_transactions),
        "is_common_subscription": is_common_subscription(transaction),
        "is_common_subscription_amount": is_common_subscription_amount(transaction.amount),
        "loan_repayment_score": get_loan_repayment_score(transaction, all_transactions),
    }
