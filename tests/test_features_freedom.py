# test features

from datetime import datetime

import pytest

from recur_scan.features_freedom import (
    get_day_of_week,
    get_days_until_next_transaction,
    get_periodicity_confidence,
    get_recurrence_streak,
)
from recur_scan.transactions import Transaction


@pytest.fixture
def sample_transactions_with_dates():
    return [
        Transaction(
            id=1,
            user_id="user1",
            name="Sample",
            amount=100.0,
            date=datetime(2023, 1, 1).strftime("%Y-%m-%d"),  # Sunday
        ),
        Transaction(
            id=2,
            user_id="user1",
            name="Sample",
            amount=100.0,
            date=datetime(2023, 1, 15).strftime("%Y-%m-%d"),  # Sunday
        ),
        Transaction(
            id=3,
            user_id="user1",
            name="Sample",
            amount=100.0,
            date=datetime(2023, 2, 1).strftime("%Y-%m-%d"),  # Wednesday
        ),
        Transaction(
            id=4,
            user_id="user1",
            name="Sample",
            amount=50.0,
            date=datetime(2023, 2, 15).strftime("%Y-%m-%d"),  # Wednesday
        ),
    ]


def test_get_day_of_week(sample_transactions_with_dates):
    transactions = sample_transactions_with_dates
    assert get_day_of_week(transactions[0]) == 6  # Sunday
    assert get_day_of_week(transactions[2]) == 2  # Wednesday


def test_get_days_until_next_transaction(sample_transactions_with_dates):
    transactions = sample_transactions_with_dates
    # Test with same amount
    assert get_days_until_next_transaction(transactions[0], transactions) == 14
    # Test with no future similar transactions
    assert get_days_until_next_transaction(transactions[-1], transactions) == -1.0


def test_get_periodicity_confidence():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", date="2023-01-01", amount=10),
        Transaction(id=2, user_id="user1", name="Netflix", date="2023-02-01", amount=10),
        Transaction(id=3, user_id="user1", name="Netflix", date="2023-03-01", amount=10),
    ]
    # Use pytest.approx for floating point comparisons
    assert get_periodicity_confidence(transactions[0], transactions) == pytest.approx(0.966, abs=0.01)


def test_get_recurrence_streak_function():
    # 3-month streak
    streak_trans = [
        Transaction(id=1, user_id="user1", name="Sample", amount=100, date=datetime(2023, 3, 1).strftime("%Y-%m-%d")),
        Transaction(id=2, user_id="user1", name="Sample", amount=100, date=datetime(2023, 2, 1).strftime("%Y-%m-%d")),
        Transaction(id=3, user_id="user1", name="Sample", amount=100, date=datetime(2023, 1, 1).strftime("%Y-%m-%d")),
    ]
    assert get_recurrence_streak(streak_trans[0], streak_trans) == 2

    # Broken streak
    broken_streak_trans = [
        Transaction(id=1, user_id="user1", name="Sample", amount=100, date=datetime(2023, 3, 1).strftime("%Y-%m-%d")),
        Transaction(
            id=2, user_id="user1", name="Sample", amount=100, date=datetime(2023, 1, 1).strftime("%Y-%m-%d")
        ),  # Missing February
    ]
    assert get_recurrence_streak(broken_streak_trans[0], broken_streak_trans) == 0
