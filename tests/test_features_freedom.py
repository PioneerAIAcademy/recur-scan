# test features

from datetime import datetime

import pytest

from recur_scan.features_freedom import (
    amount_similarity,
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


# New test features started here


def test_amount_similarity():
    amounts = [100.0, 99.5, 100.5, 101.0]
    similarity = amount_similarity(amounts)
    assert similarity > 0.9  # Very similar amounts

    amounts = [100.0, 150.0, 50.0]
    similarity = amount_similarity(amounts)
    assert similarity < 0.5  # Less similar amounts

    @pytest.fixture
    def sample_dates_monthly():
        return [
            datetime(2023, 1, 1),
            datetime(2023, 2, 1),
            datetime(2023, 3, 1),
        ]

    def day_of_month_consistency(dates):
        """Calculate consistency of day-of-month for a list of dates."""
        days = [date.day for date in dates]
        return 1.0 if len(set(days)) == 1 else 0.0

    def test_day_of_month_consistency(sample_dates_monthly):
        consistency = day_of_month_consistency(sample_dates_monthly)
        assert consistency == 1.0  # Perfect day-of-month consistency
