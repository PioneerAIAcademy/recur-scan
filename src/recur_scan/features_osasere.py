import re

import numpy as np  # type: ignore

from recur_scan.transactions import Transaction
from recur_scan.utils import get_day, parse_date


def has_min_recurrence_period(
    transaction: Transaction,
    all_transactions: list[Transaction],
    min_days: int = 60,
) -> bool:
    """Check if transactions from the same vendor span at least `min_days`."""
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(vendor_txs) < 2:
        return False
    dates = sorted([parse_date(t.date) for t in vendor_txs])
    return (dates[-1] - dates[0]).days >= min_days


def get_day_of_month_consistency(
    transaction: Transaction,
    all_transactions: list[Transaction],
    tolerance_days: int = 7,
) -> float:
    """Calculate the fraction of transactions within `tolerance_days` of the target day."""
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(vendor_txs) < 2:
        return 0.0
    target_day = get_day(transaction.date)
    matches = 0
    for t in vendor_txs:
        day_diff = abs(get_day(t.date) - target_day)
        if day_diff <= tolerance_days or day_diff >= 28 - tolerance_days:  # Handle month-end
            matches += 1
    return matches / len(vendor_txs)


def get_day_of_month_variability(
    transaction: Transaction,
    all_transactions: list[Transaction],
) -> float:
    """Measure consistency of day-of-month (lower = more consistent)."""
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(vendor_txs) < 2:
        return 31.0  # Max possible variability

    days = [get_day(t.date) for t in vendor_txs]
    # Handle month-end transitions (e.g., 28th vs 1st)
    adjusted_days = []
    for day in days:
        if day > 28 and day < 31:  # Treat 28+, 1, 2, 3 as close
            adjusted_days.extend([day, day - 31])
        else:
            adjusted_days.append(day)
    return np.std(adjusted_days)  # type: ignore


def get_recurrence_confidence(
    transaction: Transaction,
    all_transactions: list[Transaction],
    decay_rate: float = 2,  # Higher = recent transactions matter more
) -> float:
    """Calculate a confidence score (0-1) based on weighted historical recurrences."""
    vendor_txs = sorted(
        [t for t in all_transactions if t.name.lower() == transaction.name.lower()],
        key=lambda x: x.date,
    )
    if len(vendor_txs) < 2:
        return 0.0

    confidence = 0.0
    for i in range(1, len(vendor_txs)):
        days_diff = (parse_date(vendor_txs[i].date) - parse_date(vendor_txs[i - 1].date)).days
        # Weight by decay_rate^(time ago) and normalize
        confidence += (decay_rate**i) * (1.0 if days_diff <= 35 else 0.0)

    return confidence / sum(decay_rate**i for i in range(1, len(vendor_txs)))


def is_weekday_consistent(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    weekdays = [parse_date(t.date).weekday() for t in vendor_txs]  # Monday=0, Sunday=6
    return len(set(weekdays)) <= 2  # Allow minor drift (e.g., weekend vs. Monday)


def get_median_period(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    dates = sorted([parse_date(t.date) for t in vendor_txs])
    if len(dates) < 2:
        return 0.0
    day_diffs = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    return float(np.median(day_diffs))  # Median is robust to outliers


# New Features


def get_fixed_recurring(name: str, transaction: Transaction) -> bool:
    """Check if the transaction is a fixed recurring payment."""
    # Check if the transaction name contains the specified name (case-insensitive)
    return name.lower() in transaction.name.lower()


# def is_att_recurring_pattern(
#     transaction: Transaction,
#     all_transactions: list[Transaction],
# ) -> bool:
#     """
#     Identifies AT&T transactions as recurring by examining the pattern of all AT&T transactions.

#     This function first identifies if the current transaction is from AT&T, then checks if there
#     are multiple AT&T transactions to confirm a recurring pattern.

#     Args:
#         transaction: The transaction to check
#         all_transactions: List of all transactions to analyze for patterns

#     Returns:
#         True if the transaction is from AT&T and shows recurring patterns, False otherwise
#     """
#     # AT&T identification patterns (case insensitive)
#     att_patterns = ["at&t", "att ", "at and t", "at & t", "at-t"]

#     # Check if this transaction is from AT&T
#     transaction_name = transaction.name.lower()
#     is_att = any(pattern in transaction_name for pattern in att_patterns)

#     if not is_att:
#         return False

#     # Find all AT&T transactions
#     att_transactions = []
#     for t in all_transactions:
#         t_name = t.name.lower()
#         if any(pattern in t_name for pattern in att_patterns):
#             att_transactions.append(t)

#     # Always mark as recurring if we have at least 2 AT&T transactions
#     # This ensures all AT&T transactions are marked as recurring if multiple exist
#     return len(att_transactions) >= 2


def detect_installment_payments(
    transaction: Transaction,
    all_transactions: list[Transaction],
) -> bool:
    """
    Detects installment payment services like AfterPay and similar services.

    Args:
        transaction: The transaction to check
        all_transactions: List of all transactions to analyze for patterns

    Returns:
        True if the transaction appears to be an installment payment, False otherwise
    """
    # List of common installment payment services
    installment_services = [
        "afterpay",
        "klarna",
        "affirm",
        "splitit",
        "sezzle",
        "quadpay",
        "zip",
    ]
    # Get all transactions from the same vendor
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    # Installment payments typically have at least 2 payments
    if len(vendor_txs) < 2:
        return False

    # Check if transaction is from an installment service
    if not any(service in transaction.name.lower() for service in installment_services):
        return False

    # Analyze date patterns - installments often happen every 2-4 weeks
    dates = sorted([parse_date(t.date) for t in vendor_txs])
    if len(dates) < 2:
        return False

    day_diffs = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

    # Check if any consecutive transactions are 10-20 days apart (typical for biweekly payments)
    has_biweekly = any(10 <= diff <= 20 for diff in day_diffs)

    # If we have any reasonably close payments and it's an installment service, mark as recurring
    return has_biweekly


def detect_financial_service_fees(
    transaction: Transaction,
    all_transactions: list[Transaction],
) -> bool:
    """
    Detects recurring financial service fees from apps like Albert, FloatMe, etc.

    Args:
        transaction: The transaction to check
        all_transactions: List of all transactions to analyze for patterns

    Returns:
        True if the transaction appears to be a financial service fee, False otherwise
    """
    # Common financial service apps
    financial_services = [
        "albert",
        "floatme",
        "earnin",
        "dave",
        "brigit",
        "empower",
        "moneyLion",
        "vola",
        "chime",
    ]

    # Check if transaction is from a financial service
    if not any(service in transaction.name.lower() for service in financial_services):
        return False

    # Get all transactions from the same vendor
    vendor_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]

    # If we have 3+ transactions from the same financial service with the same amount,
    # it's likely a recurring service fee
    if len(vendor_txs) >= 3:
        # Check if at least 3 transactions have the same amount
        amounts: dict[float, int] = {}
        for t in vendor_txs:
            amount = t.amount
            amounts[amount] = amounts.get(amount, 0) + 1

        return any(count >= 3 for count in amounts.values())

    return False


# def detect_variable_amount_recurring(
#     transaction: Transaction,
#     all_transactions: list[Transaction],
#     min_transactions: int = 3,
#     max_amount_variation: float = 0.5,
# ) -> bool:
#     """
#     Detects recurring payments that have varying amounts (like utilities).

#     Args:
#         transaction: The transaction to check
#         all_transactions: List of all transactions to analyze for patterns
#         min_transactions: Minimum number of transactions to establish a pattern
#         max_amount_variation: Maximum allowed variation in amount (as a ratio)

#     Returns:
#         True if the transaction appears to be recurring with variable amounts, False otherwise
#     """
#     # Get all transactions from the same vendor
#     vendor_txs = [
#         t for t in all_transactions if t.name.lower() == transaction.name.lower()
#     ]

#     if len(vendor_txs) < min_transactions:
#         return False

#     # Sort by date
#     vendor_txs.sort(key=lambda x: x.date)

#     # Check if there's a pattern in transaction dates
#     dates = [parse_date(t.date) for t in vendor_txs]

#     # Calculate intervals between transactions
#     intervals = []
#     for i in range(1, len(dates)):
#         interval = (dates[i] - dates[i - 1]).days
#         intervals.append(interval)

#     # Check if intervals are consistent (within 7 days variation)
#     if len(intervals) >= 2:
#         median_interval = np.median(intervals)
#         is_regular_timing = all(abs(i - median_interval) <= 7 for i in intervals)

#         if is_regular_timing:
#             # Check amount variation
#             amounts = [float(t.amount) for t in vendor_txs]
#             mean_amount = np.mean(amounts)

#             # Calculate coefficient of variation to measure amount consistency
#             if mean_amount > 0:
#                 cv = np.std(amounts) / mean_amount

#                 # If amount variation is within acceptable range, consider it recurring
#                 if cv <= max_amount_variation:
#                     return True

#     return False


def normalize_vendor_name(name: str) -> str:
    """
    Normalize vendor names by removing common suffixes and extra spaces.

    Args:
        name: The vendor name to normalize

    Returns:
        Normalized vendor name
    """
    # Convert to lowercase
    name = name.lower()

    # Remove common suffixes

    suffixes = [" apa", " llc", " inc", " corp", " co", " ltd"]
    for suffix in suffixes:
        index = name.find(suffix)
        if index != -1:
            name = name[:index]

    # Remove phone numbers and location details in common formats
    name = re.sub(r"\s+\d{3}-\d{3}-\d{4}\s+.*", "", name)
    name = re.sub(r"\s+\d{3}-\d{7}\s+.*", "", name)
    name = re.sub(r"\s+\d{10}\s+.*", "", name)
    name = re.sub(r"\s+\d{3}\-\d{4}\s+.*", "", name)

    # Remove URLs and common transaction details
    name = re.sub(r"\s+[a-z0-9]+\.[a-z]{2,3}(/[a-z]+)?\s+.*", "", name)

    # Remove city and state patterns
    name = re.sub(r"\s+[A-Za-z]+\s+[A-Z]{2}.*", "", name)

    # Remove special characters and all text after them
    name = re.split(r"[^\w\s]", name)[0]
    name = re.sub(r"\s+", " ", name)  # Replace multiple spaces with a single space

    # Remove extra spaces
    name = " ".join(name.split())

    return name


def detect_housing_payments(
    transaction: Transaction,
    all_transactions: list[Transaction],
) -> bool:
    """
    Detects housing/rent payments which may vary in amount but occur monthly.

    Args:
        transaction: The transaction to check
        all_transactions: List of all transactions to analyze for patterns

    Returns:
        True if the transaction appears to be housing/rent related, False otherwise
    """
    # Housing-related keywords
    housing_keywords = [
        "rent",
        "lease",
        "apartment",
        "apt",
        "condo",
        "townhome",
        "housing",
        "mortgage",
        "property",
        "realty",
        "real estate",
        "waterford",
        "grove",
        "residence",
        "home",
    ]

    # Check if transaction name contains housing keywords
    if not any(keyword in transaction.name.lower() for keyword in housing_keywords):
        return False

    # Normalize the vendor name
    norm_name = normalize_vendor_name(transaction.name)

    # Find all transactions from similar vendors
    similar_txs = []
    for t in all_transactions:
        if norm_name in normalize_vendor_name(t.name):
            similar_txs.append(t)

    # Need at least 2 transactions to establish a pattern
    if len(similar_txs) < 2:
        return False

    # Sort by date
    similar_txs.sort(key=lambda x: x.date)
    dates = [parse_date(t.date) for t in similar_txs]

    # Check if transactions occur roughly monthly (15-45 days apart)
    if len(dates) >= 2:
        intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
        monthly_intervals = [i for i in intervals if 15 <= i <= 45]

        # If at least half of the intervals are monthly, consider it a housing payment
        return len(monthly_intervals) >= len(intervals) // 2

    return False


# newer features


# def get_amount_consistency(
#     transaction: Transaction,
#     all_transactions: list[Transaction],
#     tolerance_percent: float = 0.05,
# ) -> float:
#     """
#     Calculate the fraction of transactions from the same vendor with similar amounts.

#     Args:
#         transaction: The transaction to check
#         all_transactions: List of all transactions to analyze
#         tolerance_percent: The percentage difference allowed for amount matching

#     Returns:
#         Fraction of transactions with consistent amounts (0.0-1.0)
#     """
#     vendor_txs = [
#         t for t in all_transactions if t.name.lower() == transaction.name.lower()
#     ]
#     if len(vendor_txs) < 2:
#         return 0.0

#     target_amount = transaction.amount
#     matches = 0

#     for t in vendor_txs:
#         # Calculate percentage difference
#         if target_amount == 0:
#             continue
#         percent_diff = abs(t.amount - target_amount) / target_amount
#         if percent_diff <= tolerance_percent:
#             matches += 1

#     return matches / len(vendor_txs)


def detect_streaming_services(transaction: Transaction) -> bool:
    """
    Detects if the transaction is from a common streaming service.

    Args:
        transaction: The transaction to check

    Returns:
        True if it's a streaming service, False otherwise
    """
    streaming_services = [
        "netflix",
        "hulu",
        "disney+",
        "disney plus",
        "hbo max",
        "paramount+",
        "peacock",
        "apple tv",
        "amazon prime video",
        "youtube premium",
        "spotify",
        "pandora",
        "tidal",
        "apple music",
        "amazon music",
        "deezer",
        "youtube music",
        "amazon kids+",
    ]

    return any(service in transaction.name.lower() for service in streaming_services)


def detect_insurance_payments(transaction: Transaction) -> bool:
    """
    Detects if the transaction is an insurance payment.

    Args:
        transaction: The transaction to check

    Returns:
        True if it's an insurance payment, False otherwise
    """
    insurance_keywords = [
        "insurance",
        "geico",
        "progressive",
        "allstate",
        "state farm",
        "farmers",
        "liberty mutual",
        "nationwide",
        "root insurance",
        "national general",
        "usaa",
    ]

    return any(keyword in transaction.name.lower() for keyword in insurance_keywords)


# def detect_subscription_box(transaction: Transaction) -> bool:
#     """
#     Detects if the transaction is a subscription box service.

#     Args:
#         transaction: The transaction to check

#     Returns:
#         True if it's a subscription box, False otherwise
#     """
#     subscription_keywords = [
#         "box",
#         "crate",
#         "club",
#         "walmart+",
#         "amazon prime",
#         "membership",
#         "subscription",
#     ]

#     return any(keyword in transaction.name.lower() for keyword in subscription_keywords)


# def get_date_pattern_consistency(
#     transaction: Transaction, all_transactions: list[Transaction]
# ) -> float:
#     """
#     Analyze if the transaction follows common subscription patterns (monthly, quarterly, etc).

#     Args:
#         transaction: The transaction to check
#         all_transactions: List of all transactions to analyze

#     Returns:
#         Score representing how well transaction fits subscription patterns (0.0-1.0)
#     """
#     vendor_txs = [
#         t for t in all_transactions if t.name.lower() == transaction.name.lower()
#     ]
#     if len(vendor_txs) < 3:
#         return 0.0

#     dates = sorted([parse_date(t.date) for t in vendor_txs])
#     day_diffs = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

#     # Common subscription intervals (days)
#     patterns = {
#         "monthly": (25, 35),  # ~30 days
#         "bi-monthly": (55, 65),  # ~60 days
#         "quarterly": (85, 95),  # ~90 days
#         "biweekly": (12, 16),  # ~14 days
#         "weekly": (5, 9),  # ~7 days
#         "annual": (350, 380),  # ~365 days
#     }

#     # Check if day differences match any pattern
#     matches = 0
#     for diff in day_diffs:
#         for interval_range in patterns.values():
#             if interval_range[0] <= diff <= interval_range[1]:
#                 matches += 1
#                 break

#     return matches / len(day_diffs) if day_diffs else 0.0


# def detect_utility_payments(transaction: Transaction) -> bool:
#     """
#     Detects if the transaction is a utility payment.

#     Args:
#         transaction: The transaction to check

#     Returns:
#         True if it's a utility payment, False otherwise
#     """
#     utility_keywords = [
#         "electric",
#         "water",
#         "gas",
#         "power",
#         "utility",
#         "utilities",
#         "energy",
#         "sewage",
#         "waste",
#         "ngrid",
#         "national grid",
#         "pg&e",
#         "duke energy",
#         "con edison",
#         "xcel",
#     ]

#     return any(keyword in transaction.name.lower() for keyword in utility_keywords)


# def detect_lending_services(transaction: Transaction) -> bool:
#     """
#     Detects if the transaction is from a lending service.

#     Args:
#         transaction: The transaction to check

#     Returns:
#         True if it's a lending service payment, False otherwise
#     """
#     lending_keywords = [
#         "loan",
#         "lending",
#         "kikoff",
#         "credit",
#         "borrowing",
#         "payment",
#         "finance",
#         "leasing",
#         "cleo",
#     ]

#     return any(keyword in transaction.name.lower() for keyword in lending_keywords)


# def get_future_transactions_count(
#     transaction: Transaction, all_transactions: list[Transaction]
# ) -> int:
#     """
#     Count how many transactions from the same vendor occur after this one.

#     Args:
#         transaction: The transaction to check
#         all_transactions: List of all transactions to analyze

#     Returns:
#         Number of future transactions from same vendor
#     """
#     tx_date = parse_date(transaction.date)

#     future_count = 0
#     for t in all_transactions:
#         if t.name.lower() == transaction.name.lower() and parse_date(t.date) > tx_date:
#             future_count += 1

#     return future_count


# def is_common_misclassified_merchant(transaction: Transaction) -> bool:
#     """
#     Identifies merchants that are commonly misclassified in the dataset.

#     Args:
#         transaction: The transaction to check

#     Returns:
#         True if this is a merchant that's commonly misclassified
#     """
#     problem_merchants = [
#         "planet fitness",
#         "hulu",
#         "earnin",
#         "walmart+",
#         "music & arts",
#         "ngrid",
#         "root insurance",
#     ]

#     return any(
#         merchant.lower() in transaction.name.lower() for merchant in problem_merchants
#     )


def is_likely_recurring_by_merchant(transaction: Transaction) -> bool:
    """
    Identifies merchants that are almost always recurring subscriptions.

    Args:
        transaction: The transaction to check

    Returns:
        True if this merchant is likely to be a recurring subscription
    """
    recurring_merchants = [
        "kikoff",
        "albert",
        "amazon kids+",
        "amazon music",
        "microsoft xbox",
        "apple",
        "floatme",
        "sezzle",
    ]

    return any(merchant.lower() in transaction.name.lower() for merchant in recurring_merchants)


def has_consistent_amount(
    transaction: Transaction,
    all_transactions: list[Transaction],
    exact_match: bool = True,
) -> bool:
    """
    Checks if this transaction has the same amount as other transactions from the same merchant.

    Args:
        transaction: The transaction to check
        all_transactions: List of all transactions to analyze
        exact_match: Whether to require exact match or allow small variance

    Returns:
        True if the amount is consistent with other transactions from this merchant
    """
    merchant_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(merchant_txs) <= 1:
        return False

    target_amount = transaction.amount
    matches = 0
    total = 0

    for t in merchant_txs:
        if t.id != transaction.id:  # Skip comparing to self
            total += 1
            if (exact_match and t.amount == target_amount) or (
                not exact_match and abs(t.amount - target_amount) / max(t.amount, target_amount) < 0.05
            ):
                matches += 1

    return matches >= total * 0.75  # 75% or more match


# def is_round_number_amount(transaction: Transaction) -> bool:
#     """
#     Checks if the transaction amount is a round number (often indicates recurring).

#     Args:
#         transaction: The transaction to check

#     Returns:
#         True if the amount is a round number
#     """
#     amount = transaction.amount
#     return amount == int(amount) or amount * 100 == int(amount * 100)


# def is_likely_one_time_by_amount(transaction: Transaction) -> bool:
#     """
#     Checks if the transaction amount suggests a one-time payment rather than recurring.

#     Args:
#         transaction: The transaction to check

#     Returns:
#         True if the amount suggests a one-time payment
#     """
#     # Large, uneven amounts are often one-time payments
#     return transaction.amount > 100 and not is_round_number_amount(transaction)


def has_regular_interval(
    transaction: Transaction,
    all_transactions: list[Transaction],
    max_variance_days: int = 5,
) -> bool:
    """
    Checks if transactions from this merchant occur at regular intervals.

    Args:
        transaction: The transaction to check
        all_transactions: List of all transactions to analyze
        max_variance_days: Maximum allowed variance in days between intervals

    Returns:
        True if transactions occur at regular intervals
    """
    merchant_txs = [t for t in all_transactions if t.name.lower() == transaction.name.lower()]
    if len(merchant_txs) < 3:
        return False

    dates = sorted([parse_date(t.date) for t in merchant_txs])
    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]

    if not intervals:
        return False

    avg_interval = sum(intervals) / len(intervals)
    # Check if all intervals are within max_variance_days of the average
    return all(abs(interval - avg_interval) <= max_variance_days for interval in intervals)


# def simple_classifier(
#     transaction: Transaction, all_transactions: list[Transaction]
# ) -> int:
#     """
#     A simple rule-based classifier to determine if a transaction is recurring.

#     Args:
#         transaction: The transaction to check
#         all_transactions: List of all transactions to analyze

#     Returns:
#         1 if transaction is recurring, 0 if not recurring
#     """
#     # First, check if it's a merchant we know is typically recurring
#     if is_likely_recurring_by_merchant(transaction):
#         return 1

#     # Next, check if it's a merchant that's often misclassified
#     if is_common_misclassified_merchant(transaction):
#         # For common misclassified merchants, use stricter criteria
#         if has_consistent_amount(
#             transaction, all_transactions
#         ) and has_regular_interval(transaction, all_transactions):
#             return 1
#         else:
#             return 0

#     # For other transactions, use a combination of features
#     recurring_signals = 0

#     if has_consistent_amount(transaction, all_transactions, exact_match=True):
#         recurring_signals += 2

#     if has_regular_interval(transaction, all_transactions):
#         recurring_signals += 2

#     if is_round_number_amount(transaction):
#         recurring_signals += 1

#     if is_likely_one_time_by_amount(transaction):
#         recurring_signals -= 2

#     # Return 1 (recurring) if we have enough signals, otherwise 0 (not recurring)
#     return 1 if recurring_signals >= 2 else 0


def get_new_features(
    transaction: Transaction,
    all_transactions: list[Transaction],
) -> dict[str, float]:
    """Generate new features for the transaction."""
    return {
        "is_AT&T_": get_fixed_recurring("AT&T", transaction),
        "is_water_utility": get_fixed_recurring("Water", transaction),
        "is_installment_payment": detect_installment_payments(transaction, all_transactions),
        "is_financial_service_fee": detect_financial_service_fees(transaction, all_transactions),
        # "is_variable_recurring": detect_variable_amount_recurring(
        #     transaction, all_transactions
        # ),
        "is_housing_payment": detect_housing_payments(transaction, all_transactions),
        # "is_insurance_payment_O": detect_insurance_payments(
        #     transaction, all_transactions
        # ),
        # "amount_consistency": get_amount_consistency(transaction, all_transactions),
        "is_streaming_service": detect_streaming_services(transaction),
        "is_insurance_payment": detect_insurance_payments(transaction),
        # "is_subscription_box": detect_subscription_box(transaction),
        # "date_pattern_consistency": get_date_pattern_consistency(
        #     transaction, all_transactions
        # ),
        # "is_utility_payment": detect_utility_payments(transaction),
        # "is_lending_service": detect_lending_services(transaction),
        # "future_transactions_count": get_future_transactions_count(
        #     transaction, all_transactions
        # ),
        "is_recurring_merchant": is_likely_recurring_by_merchant(transaction),
        # "is_problem_merchant": is_common_misclassified_merchant(transaction),
        "has_consistent_amount": has_consistent_amount(transaction, all_transactions),
        # "is_round_number": is_round_number_amount(transaction),
        "has_regular_interval": has_regular_interval(transaction, all_transactions),
        # "prediction": simple_classifier(transaction, all_transactions),
    }
