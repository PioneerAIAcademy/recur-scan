# test features
import pytest

from recur_scan.features import (
    get_n_transactions_same_amount, 
    get_percent_transactions_same_amount, 
    get_time_interval_between_transactions, 
    get_mobile_transaction,
    get_is_phone,    
    get_transaction_frequency,
    get_dispersion_transaction_amount,
    get_ends_in_99,
    get_is_insurance,    
    get_is_utility,
    get_n_transactions_days_apart,    
    get_n_transactions_same_day,
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
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 2 / 3


def test_get_time_interval_between_transactions(transactions) -> None:
    """
    Test that get_time_interval_between_transactions returns the correct average time interval between transactions with the same amount.
    """
    assert get_time_interval_between_transactions(transactions[0], transactions) == 1.0
    assert get_time_interval_between_transactions(transactions[2], transactions) == 365.0

def test_get_mobile_transaction(transactions) -> None:
    """
    Test that get_mobile_transaction returns True for mobile company transactions and False otherwise.
    """
    assert get_mobile_transaction(transactions[3]) is True  # T-Mobile
    assert get_mobile_transaction(transactions[4]) is True  # AT&T
    assert get_mobile_transaction(transactions[5]) is True  # Verizon
    assert get_mobile_transaction(transactions[0]) is False  # vendor1

def test_get_n_transactions_same_day(transactions) -> None:
    """Test that get_n_transactions_same_day returns the correct number of transactions on the same day."""
    assert get_n_transactions_same_day(transactions[0], transactions, 0) == 2
    assert get_n_transactions_same_day(transactions[0], transactions, 1) == 3
    assert get_n_transactions_same_day(transactions[2], transactions, 0) == 1


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

def test_get_ends_in_99(transactions) -> None:
    """Test get_ends_in_99."""
    assert get_ends_in_99(Transaction(id=12, user_id="user1", name="vendor3", amount=99.99, date="2024-01-08")) is True
    assert get_ends_in_99(Transaction(id=13, user_id="user1", name="vendor4", amount=100.00, date="2024-01-09")) is False
    assert get_ends_in_99(Transaction(id=14, user_id="user1", name="vendor5", amount=199.99, date="2024-01-10")) is True
    assert get_ends_in_99(Transaction(id=15, user_id="user1", name="vendor6", amount=200.00, date="2024-01-11")) is False
    assert get_ends_in_99(transactions[0]) is False  # vendor1 with amount 100

def test_get_transaction_frequency(transactions) -> None:
    """Test get_transaction_frequency."""
    assert get_transaction_frequency(transactions[0], transactions) > 0
    assert get_transaction_frequency(Transaction(id=12, user_id="user1", name="vendor3", amount=99.99, date="2024-01-08"), transactions) == 0.0

def test_get_dispersion_transaction_amount(transactions) -> None:
    """Test get dispersion in transaction amounts for the same vendor"""
    assert get_dispersion_transaction_amount(transactions[0], transactions) == 0.0
    assert get_dispersion_transaction_amount(Transaction(id=12, user_id="user1", name="vendor3", amount=99.99, date="2024-01-08"), transactions) == 0.0

def test_get_is_utility(transactions) -> None:
    """Test get_is_utility."""
    assert get_is_utility(transactions[2])
    assert not get_is_utility(transactions[3])

