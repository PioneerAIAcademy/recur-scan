# test features

from datetime import datetime

import pytest

from recur_scan.features import (
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


def get_days_since_last_transaction(transaction, transactions):
    """Calculate the number of days since the last transaction with the same amount."""
    transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    previous_transactions = [
        t
        for t in transactions
        if t.amount == transaction.amount and datetime.strptime(t.date, "%Y-%m-%d") < transaction_date
    ]
    if not previous_transactions:
        return float("inf")
    last_transaction_date = max(datetime.strptime(t.date, "%Y-%m-%d") for t in previous_transactions)
    return (transaction_date - last_transaction_date).days


def test_get_days_since_last_transaction(sample_transactions_with_dates):
    # Test with same amount
    assert get_days_since_last_transaction(sample_transactions_with_dates[1], sample_transactions_with_dates) == 14
    # Test with no previous similar transactions
    assert get_days_since_last_transaction(sample_transactions_with_dates[0], sample_transactions_with_dates) == float(
        "inf"
    )


def get_day_of_week(transaction):
    """Return the day of the week for a given transaction (0=Monday, 6=Sunday)."""
    transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    return transaction_date.weekday()


def test_get_day_of_week(sample_transactions_with_dates):
    transactions = sample_transactions_with_dates
    assert get_day_of_week(transactions[0]) == 6  # Sunday
    assert get_day_of_week(transactions[2]) == 2  # Wednesday


def get_days_until_next_transaction(transaction, transactions):
    """Calculate the number of days until the next transaction with the same amount."""
    transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    future_transactions = [
        t
        for t in transactions
        if t.amount == transaction.amount and datetime.strptime(t.date, "%Y-%m-%d") > transaction_date
    ]
    if not future_transactions:
        return float("inf")
    next_transaction_date = min(datetime.strptime(t.date, "%Y-%m-%d") for t in future_transactions)
    return (next_transaction_date - transaction_date).days


def test_get_days_until_next_transaction(sample_transactions_with_dates):
    transactions = sample_transactions_with_dates
    # Test with same amount
    assert get_days_until_next_transaction(transactions[0], transactions) == 14
    # Test with no future similar transactions
    assert get_days_until_next_transaction(transactions[-1], transactions) == float("inf")

    def get_periodicity_confidence(transaction, transactions):
        """
        Calculate a confidence score for the periodicity of a transaction.
        A higher score indicates more regular periodicity.
        """
        dates = sorted(datetime.strptime(t.date, "%Y-%m-%d") for t in transactions if t.amount == transaction.amount)
        if len(dates) < 2:
            return 0.0  # Not enough data to determine periodicity

        intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((interval - avg_interval) ** 2 for interval in intervals) / len(intervals)
        return max(0.0, 1.0 - (variance / avg_interval if avg_interval else 1.0))

    def test_get_periodicity_confidence():
        # Perfect monthly transactions
        monthly_trans = [
            Transaction(
                id=1, user_id="user1", name="Sample", amount=100, date=datetime(2023, 1, 1).strftime("%Y-%m-%d")
            ),
            Transaction(
                id=2, user_id="user1", name="Sample", amount=100, date=datetime(2023, 2, 1).strftime("%Y-%m-%d")
            ),
            Transaction(
                id=3, user_id="user1", name="Sample", amount=100, date=datetime(2023, 3, 1).strftime("%Y-%m-%d")
            ),
        ]
        assert get_periodicity_confidence(monthly_trans[0], monthly_trans) > 0.9

    # Irregular transactions
    irregular_trans = [
        Transaction(id=1, user_id="user1", name="Sample", amount=100, date=datetime(2023, 1, 1).strftime("%Y-%m-%d")),
        Transaction(id=2, user_id="user1", name="Sample", amount=100, date=datetime(2023, 2, 15).strftime("%Y-%m-%d")),
        Transaction(id=3, user_id="user1", name="Sample", amount=100, date=datetime(2023, 3, 20).strftime("%Y-%m-%d")),
    ]
    assert get_periodicity_confidence(irregular_trans[0], irregular_trans) < 0.5


def get_recurrence_streak(transaction, transactions):
    """
    Calculate the recurrence streak for a transaction.
    A streak is the number of consecutive periods (e.g., months) where the transaction recurs.
    """
    dates = sorted(datetime.strptime(t.date, "%Y-%m-%d") for t in transactions if t.amount == transaction.amount)
    streak = 0
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days <= 31:  # Assuming monthly recurrence
            streak += 1
        else:
            break
    return streak


def test_get_recurrence_streak():
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
