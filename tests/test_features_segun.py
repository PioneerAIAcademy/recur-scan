# test features
import pytest

from recur_scan.features_segun import (
    get_average_transaction_amount,
    get_average_transaction_interval,
    get_max_transaction_amount,
    get_min_transaction_amount,
    get_total_transaction_amount,
    get_transaction_amount_frequency,
    get_transaction_amount_median,
    get_transaction_amount_range,
    get_transaction_amount_std,
    get_transaction_count,
    get_transaction_day_of_week,
    get_transaction_time_of_day,
    get_unique_transaction_amount_count,
)
from recur_scan.transactions import Transaction


def test_get_total_transaction_amount() -> None:
    """Test that get_total_transaction_amount returns the correct total amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-02"),
    ]
    assert get_total_transaction_amount(transactions) == 450.0


def test_get_average_transaction_amount() -> None:
    """Test that get_average_transaction_amount returns the correct average amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-02"),
    ]
    assert get_average_transaction_amount(transactions) == 150.0


def test_get_max_transaction_amount() -> None:
    """Test that get_max_transaction_amount returns the correct maximum amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-02"),
    ]
    assert get_max_transaction_amount(transactions) == 200.0


def test_get_min_transaction_amount() -> None:
    """Test that get_min_transaction_amount returns the correct minimum amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-02"),
    ]
    assert get_min_transaction_amount(transactions) == 100.0


def test_get_transaction_count() -> None:
    """Test that get_transaction_count returns the correct number of transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-02"),
    ]
    assert get_transaction_count(transactions) == 3


def test_get_transaction_amount_std() -> None:
    """Test that get_transaction_amount_std returns the correct standard deviation of transaction amounts."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-02"),
    ]
    assert get_transaction_amount_std(transactions) == pytest.approx(50.0)


def test_get_transaction_amount_median() -> None:
    """Test that get_transaction_amount_median returns the correct median transaction amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-02"),
    ]
    assert get_transaction_amount_median(transactions) == 150.0


def test_get_transaction_amount_range() -> None:
    """Test that get_transaction_amount_range returns the correct range of transaction amounts."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-02"),
    ]
    assert get_transaction_amount_range(transactions) == 100.0


def test_get_unique_transaction_amount_count() -> None:
    """Test that get_unique_transaction_amount_count returns the correct number of unique transaction amounts."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-02"),
    ]
    assert get_unique_transaction_amount_count(transactions) == 3


def test_get_transaction_amount_frequency() -> None:
    """Test that get_transaction_amount_frequency returns the correct frequency of the transaction amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=100.0, date="2024-01-02"),
    ]
    assert get_transaction_amount_frequency(transactions[0], transactions) == 2


def test_get_transaction_day_of_week() -> None:
    """Test that get_transaction_day_of_week returns the correct day of the week."""
    transaction = Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01")  # Monday
    assert get_transaction_day_of_week(transaction) == 0  # 0 = Monday


def test_get_transaction_time_of_day() -> None:
    """Test that get_transaction_time_of_day returns the correct time of day."""
    transaction = Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01 15:30:00")
    assert get_transaction_time_of_day(transaction) == 2


def test_get_average_transaction_interval() -> None:
    """Test that get_average_transaction_interval returns the correct average interval between transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100.0, date="2024-01-05"),
        Transaction(id=3, user_id="user1", name="name1", amount=100.0, date="2024-01-10"),
    ]
    assert get_average_transaction_interval(transactions) == 4.5  # (4 + 5) / 2
