# test features
import pytest

from recur_scan.features import get_n_transactions_same_amount, get_percent_transactions_same_amount, get_time_interval_between_transactions, get_mobile_company
from recur_scan.transactions import Transaction


@pytest.fixture
def transactions():
    """Fixture providing test transactions."""
    return [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
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


def test_get_mobile_company(transactions) -> None:
    """
    Test that get_mobile_company returns True for mobile company transactions and False otherwise.
    """
    assert get_mobile_company(transactions[3]) is True  # T-Mobile
    assert get_mobile_company(transactions[4]) is True  # AT&T
    assert get_mobile_company(transactions[5]) is True  # Verizon
    assert get_mobile_company(transactions[0]) is False  # vendor1

