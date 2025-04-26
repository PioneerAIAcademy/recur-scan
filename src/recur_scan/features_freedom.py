from datetime import timedelta

import numpy as np

from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date


def get_day_of_week(transaction: Transaction) -> int:
    """Get day of week (0=Monday, 6=Sunday)"""
    return parse_date(transaction.date).weekday()


def get_days_until_next_transaction(
    transaction: Transaction, all_transactions: list[Transaction], lookahead_days: int = 90
) -> float:
    """Get days until next similar transaction (same amount ±1%) within lookahead window"""
    similar_trans = [
        t
        for t in all_transactions
        if t != transaction
        and abs(t.amount - transaction.amount) / max(transaction.amount, 0.01) < 0.01
        and (parse_date(t.date) - parse_date(transaction.date)).days <= lookahead_days
    ]
    if not similar_trans:
        return -1.0  # cannot return inf because it will break the model
    next_date = min(t.date for t in similar_trans)
    return (parse_date(next_date) - parse_date(transaction.date)).days


def get_periodicity_confidence(
    transaction: Transaction, all_transactions: list[Transaction], expected_period: int = 30
) -> float:
    """Calculate confidence score for periodicity (0-1)"""
    similar_trans = sorted([t for t in all_transactions if t != transaction], key=lambda x: x.date)

    if len(similar_trans) < 2:
        return 0.0

    deltas = []
    for i in range(1, len(similar_trans)):
        delta = (parse_date(similar_trans[i].date) - parse_date(similar_trans[i - 1].date)).days
        deltas.append(delta)

    if not deltas:
        return 0.0

    avg_delta = np.mean(deltas)
    std_delta = np.std(deltas)

    # Score based on how close average is to expected period and how consistent
    period_score = 1 - min(float(abs(avg_delta - expected_period) / expected_period), 1)
    consistency_score = 1 - min(float(std_delta) / expected_period, 1)

    return (period_score + consistency_score) / 2


def get_recurrence_streak(
    transaction: Transaction, all_transactions: list[Transaction], tolerance_days: int = 3
) -> int:
    """Count consecutive periods with similar transactions"""
    similar_trans = sorted([t for t in all_transactions if t != transaction], key=lambda x: x.date)

    if not similar_trans:
        return 0

    streak = 0
    expected_date = parse_date(transaction.date) - timedelta(days=30)

    for t in reversed(similar_trans):
        if abs((expected_date - parse_date(t.date)).days) <= tolerance_days:
            streak += 1
            expected_date = parse_date(t.date) - timedelta(days=30)
        else:
            break

    return streak
