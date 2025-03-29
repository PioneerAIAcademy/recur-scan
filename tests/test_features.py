# test features

from datetime import datetime

import pytest

from recur_scan.features import (
    get_day_of_week,
    get_days_until_next_transaction,
    get_ends_in_99,
    get_is_always_recurring,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
    get_periodicity_confidence,
    get_recurrence_streak,
)
from recur_scan.transactions import Transaction


def test_get_n_transactions_same_amount() -> None:
    """Test that get_n_transactions_same_amount returns the correct number of transactions with the same amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert get_n_transactions_same_amount(transactions[0], transactions) == 2
    assert get_n_transactions_same_amount(transactions[2], transactions) == 1


def test_get_percent_transactions_same_amount() -> None:
    """
    Test that get_percent_transactions_same_amount returns correct percentage.
    Tests that the function calculates the right percentage of transactions with matching amounts.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 2 / 4


def test_get_ends_in_99() -> None:
    """Test that get_ends_in_99 returns True for amounts ending in 99."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert not get_ends_in_99(transactions[0])
    assert get_ends_in_99(transactions[3])


def test_get_n_transactions_same_day() -> None:
    """Test that get_n_transactions_same_day returns the correct number of transactions on the same day."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert get_n_transactions_same_day(transactions[0], transactions, 0) == 2
    assert get_n_transactions_same_day(transactions[0], transactions, 1) == 3
    assert get_n_transactions_same_day(transactions[2], transactions, 0) == 1


def test_get_pct_transactions_same_day() -> None:
    """Test that get_pct_transactions_same_day returns the correct percentage of transactions on the same day."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert get_pct_transactions_same_day(transactions[0], transactions, 0) == 2 / 4


def test_get_n_transactions_days_apart() -> None:
    """Test get_n_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 0) == 2
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 1) == 4


def test_get_pct_transactions_days_apart() -> None:
    """Test get_pct_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_pct_transactions_days_apart(transactions[0], transactions, 14, 0) == 2 / 7
    assert get_pct_transactions_days_apart(transactions[0], transactions, 14, 1) == 4 / 7


def test_get_is_insurance() -> None:
    """Test get_is_insurance."""
    assert get_is_insurance(
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01")
    )
    assert not get_is_insurance(Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"))


def test_get_is_phone() -> None:
    """Test get_is_phone."""
    assert get_is_phone(Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"))
    assert not get_is_phone(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))


def test_get_is_utility() -> None:
    """Test get_is_utility."""
    assert get_is_utility(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))
    assert not get_is_utility(
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03")
    )


def test_get_is_always_recurring() -> None:
    """Test get_is_always_recurring."""
    assert get_is_always_recurring(Transaction(id=1, user_id="user1", name="netflix", amount=100, date="2024-01-01"))
    assert not get_is_always_recurring(
        Transaction(id=2, user_id="user1", name="walmart", amount=100, date="2024-01-01")
    )


# Test data setup
@pytest.fixture
def sample_transactions():
    return [
        Transaction(id=1, user_id="user1", name="Supermarket", amount=50.0, date="2023-01-15"),
        Transaction(id=2, user_id="user1", name="Supermarket", amount=75.0, date="2023-01-20"),
        Transaction(id=3, user_id="user1", name="Supermarket", amount=60.0, date="2023-02-15"),
        Transaction(id=4, user_id="user1", name="Employer", amount=2000.0, date="2023-01-01"),
        Transaction(id=5, user_id="user1", name="Landlord", amount=1000.0, date="2023-01-01"),
        Transaction(id=6, user_id="user1", name="Landlord", amount=1000.0, date="2023-02-01"),
    ]


@pytest.fixture
def periodic_transactions():
    return [
        Transaction(id=1, user_id="user1", name="Streaming", amount=10.0, date="2023-01-01"),
        Transaction(id=2, user_id="user1", name="Streaming", amount=10.0, date="2023-01-08"),
        Transaction(id=3, user_id="user1", name="Streaming", amount=10.0, date="2023-01-15"),
        Transaction(id=4, user_id="user1", name="Streaming", amount=10.0, date="2023-01-22"),
    ]


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


# def test_get_days_since_last_transaction(sample_transactions_with_dates):
#     # Test with same amount
#     assert get_days_since_last_transaction
#       (sample_transactions_with_dates[1],
#       sample_transactions_with_dates) == 14
#     # Test with no previous similar transactions
#     assert get_days_since_last_transaction
#       (sample_transactions_with_dates[0],
#       sample_transactions_with_dates) == float(
#         "inf"
#     )


def test_get_day_of_week(sample_transactions_with_dates):
    transactions = sample_transactions_with_dates
    assert get_day_of_week(transactions[0]) == 6  # Sunday
    assert get_day_of_week(transactions[2]) == 2  # Wednesday


# def test_get_days_until_next_transaction(sample_transactions_with_dates):
#     transactions = sample_transactions_with_dates
#     # Test with same amount
#     assert get_days_until_next_transaction(transactions[0], transactions) == 14
#     # Test with no future similar transactions
#     assert get_days_until_next_transaction(transactions[-1], transactions) == float("inf")

#     variance = 0  # Replace with the actual calculation or value for variance
#     avg_interval = 1  # Replace with the actual calculation or value for avg_interval
#     return max(0.0, 1.0 - (variance / avg_interval if avg_interval else 1.0))


# def test_get_periodicity_confidence():
#     # Perfect monthly transactions
#     monthly_trans = [
#         Transaction(
#           id=1, user_id="user1",
#           name="Sample", amount=100,
#           date=datetime(2023, 1, 1).strftime("%Y-%m-%d")),
#         Transaction(id=2, user_id="user1", name="Sample",
#           amount=100, date=datetime(2023, 2, 1).strftime("%Y-%m-%d")),
#         Transaction(id=3, user_id="user1", name="Sample",
#            amount=100, date=datetime(2023, 3, 1).strftime("%Y-%m-%d")),
#     ]
#     assert get_periodicity_confidence(monthly_trans[0], monthly_trans) > 0.9

#     # Irregular transactions
#     irregular_trans = [
#         Transaction(id=1, user_id="user1", name="Sample",
#           amount=100, date=datetime(2023, 1, 1).strftime("%Y-%m-%d")),
#         Transaction(id=2, user_id="user1", name="Sample",
#           amount=100, date=datetime(2023, 2, 15).strftime("%Y-%m-%d")),
#         Transaction(id=3, user_id="user1", name="Sample",
#           amount=100, date=datetime(2023, 3, 20).strftime("%Y-%m-%d")),
#     ]
#     assert get_periodicity_confidence(irregular_trans[0], irregular_trans) < 0.5


def test_get_days_until_next_transaction(sample_transactions_with_dates):
    transactions = sample_transactions_with_dates
    # Test with same amount
    assert get_days_until_next_transaction(transactions[0], transactions) == 14
    # Test with no future similar transactions
    assert get_days_until_next_transaction(transactions[-1], transactions) == float("inf")


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
