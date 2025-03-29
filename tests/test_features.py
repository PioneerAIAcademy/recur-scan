# test features
import pytest

from recur_scan.features import (
    get_average_transaction_amount,
    get_average_transaction_interval,
    get_ends_in_99,
    get_is_always_recurring,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_max_transaction_amount,
    get_min_transaction_amount,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
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
    assert get_transaction_time_of_day(transaction) == "afternoon"


def test_get_average_transaction_interval() -> None:
    """Test that get_average_transaction_interval returns the correct average interval between transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100.0, date="2024-01-05"),
        Transaction(id=3, user_id="user1", name="name1", amount=100.0, date="2024-01-10"),
    ]
    assert get_average_transaction_interval(transactions) == 4.5  # (4 + 5) / 2
