# test features
import pytest

from recur_scan.features import (
    _get_days,
    get_ends_in_99,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_percent_transactions_same_amount,
)
from recur_scan.transactions import Transaction


@pytest.fixture
def transactions():
    """Fixture providing test transactions."""
    return [
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03"),
    ]


def test_get_n_transactions_same_amount(transactions) -> None:
    """Test that get_n_transactions_same_amount returns the correct number of transactions with the same amount."""
    assert get_n_transactions_same_amount(transactions[0], transactions) == 2
    assert get_n_transactions_same_amount(transactions[2], transactions) == 1


def test_get_percent_transactions_same_amount(transactions) -> None:
    """
    Test that get_percent_transactions_same_amount returns correct percentage.
    Tests that the function calculates the right percentage of transactions with matching amounts.
    """
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 2 / 4


def test_get_ends_in_99(transactions) -> None:
    """Test that get_ends_in_99 returns True for amounts ending in 99."""
    assert not get_ends_in_99(transactions[0])
    assert get_ends_in_99(transactions[3])


def test_get_n_transactions_same_day(transactions) -> None:
    """Test that get_n_transactions_same_day returns the correct number of transactions on the same day."""
    assert get_n_transactions_same_day(transactions[0], transactions, 0) == 2
    assert get_n_transactions_same_day(transactions[0], transactions, 1) == 3
    assert get_n_transactions_same_day(transactions[2], transactions, 0) == 1


def test_get_days_since_epoch() -> None:
    """Test get the number of days since the epoch."""
    assert _get_days("1970-01-01") == 0
    assert _get_days("1971-01-01") == 365
    assert _get_days("1970-02-01") == 31


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


def test_get_is_insurance(transactions) -> None:
    """Test get_is_insurance."""
    assert get_is_insurance(transactions[0])
    assert not get_is_insurance(transactions[1])


def test_get_is_phone(transactions) -> None:
    """Test get_is_phone."""
    assert get_is_phone(transactions[1])
    assert not get_is_phone(transactions[2])


def test_get_is_utility(transactions) -> None:
    """Test get_is_utility."""
    assert get_is_utility(transactions[2])
    assert not get_is_utility(transactions[3])
