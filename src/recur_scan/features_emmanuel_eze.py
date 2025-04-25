import statistics

from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date


def detect_sequence_patterns(
    transaction: Transaction, all_transactions: list[Transaction], min_occurrences: int = 3
) -> dict[str, float]:
    """
    Detects recurring sequences with confidence scores.
    """
    # Skip transactions with zero amount to avoid division by zero
    if transaction.amount == 0:
        return {"sequence_confidence": 0.0, "sequence_pattern": -1, "sequence_length": 0}

    vendor_txs = [
        t
        for t in all_transactions
        if t.name.lower() == transaction.name.lower()
        and abs(t.amount - transaction.amount) / max(transaction.amount, 1) < 0.05
    ]

    if len(vendor_txs) < min_occurrences:
        return {"sequence_confidence": 0.0, "sequence_pattern": -1, "sequence_length": 0}

    vendor_txs_sorted = sorted(vendor_txs, key=lambda x: parse_date(x.date))

    intervals = [
        (parse_date(vendor_txs_sorted[i].date) - parse_date(vendor_txs_sorted[i - 1].date)).days
        for i in range(1, len(vendor_txs_sorted))
    ]
    avg_interval = statistics.mean(intervals)
    stdev_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0

    patterns = {1: 7, 2: 30, 3: 365}  # 1: weekly, 2: monthly, 3: yearly
    best_pattern, best_confidence = -1, 0.0

    for name, expected_interval in patterns.items():
        deviation = abs(avg_interval - expected_interval)
        tolerance = max(2, expected_interval * 0.1)
        if deviation <= tolerance:
            confidence = 1 - (stdev_interval / (expected_interval + 1e-6))
            if confidence > best_confidence:
                best_pattern, best_confidence = name, max(0, min(1, confidence))

    return {
        "sequence_confidence": best_confidence,
        "sequence_pattern": best_pattern,
        "sequence_length": len(vendor_txs),
    }


def get_is_recurring(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the transaction is part of a recurring pattern based on the time intervals
    between transactions with the same amount and vendor name.
    """
    transaction_date = parse_date(transaction.date)
    similar_transactions = [
        t
        for t in all_transactions
        if t.amount == transaction.amount and t.name == transaction.name and t.date != transaction.date
    ]

    if not similar_transactions:
        return False

    # Calculate the time intervals between the transaction and similar transactions
    intervals = sorted(abs((transaction_date - parse_date(t.date)).days) for t in similar_transactions)

    # Check if the intervals form a recurring pattern (e.g., weekly, bi-weekly, monthly)
    return any(interval % 7 == 0 or interval % 14 == 0 or interval % 30 == 0 for interval in intervals)


def get_recurring_transaction_confidence(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate a recurring transaction confidence score by combining:
    - Amount stability
    - Interval regularity
    - Transaction frequency
    - Metadata similarity
    """
    # 1. Amount Stability
    similar_transactions = [
        t.amount for t in all_transactions if t.name == transaction.name and t.date != transaction.date
    ]
    if len(similar_transactions) < 2:
        amount_stability = 1.0  # High variability if fewer than 2 transactions
    else:
        mean = sum(similar_transactions) / len(similar_transactions)
        stdev = statistics.stdev(similar_transactions)
        amount_stability = stdev / mean if mean != 0 else 1.0

    # 2. Interval Regularity
    similar_dates = [
        parse_date(t.date) for t in all_transactions if t.name == transaction.name and t.date != transaction.date
    ]
    if len(similar_dates) < 2:
        interval_regularities = -1.0  # No intervals if fewer than 2 transactions
    else:
        intervals = [(similar_dates[i] - similar_dates[i - 1]).days for i in range(1, len(similar_dates))]
        interval_regularities = (
            -1.0 if len(intervals) < 2 else statistics.stdev(intervals)
        )  # Default value for insufficient data

    # 3. Transaction Frequency
    transaction_date = parse_date(transaction.date)
    transaction_frequency = len([
        t
        for t in all_transactions
        if t.name == transaction.name and abs((parse_date(t.date) - transaction_date).days) <= 30
    ])

    # 4. Metadata Similarity
    def _jaccard_similarity(set1: set, set2: set) -> float:
        """Calculate Jaccard similarity between two sets."""
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union != 0 else 0.0

    metadata_similarities = [
        _jaccard_similarity(set(transaction.name.split()), set(t.name.split()))
        for t in all_transactions
        if t.name == transaction.name and t.date != transaction.date
    ]
    metadata_similarity = sum(metadata_similarities) / len(metadata_similarities) if metadata_similarities else 0.0

    # 5. Combine into a Confidence Score
    score = (
        (1 / (1 + max(amount_stability, 0))) * 0.3  # Weight: 30%
        + (1 / (1 + max(interval_regularities, 0))) * 0.3  # Weight: 30%
        + (transaction_frequency / max(transaction_frequency, 1)) * 0.2  # Weight: 20%
        + metadata_similarity * 0.2  # Weight: 20%
    )
    return score
