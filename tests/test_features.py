# test features
import pytest

from recur_scan.features import (
    get_most_frequent_names,
    get_n_transactions_same_amount,
    get_percent_transactions_same_amount,
)
from recur_scan.transactions import Transaction


@pytest.fixture
def transactions():
    """Fixture providing test transactions."""
    return [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="user2", name="vendor2", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="vendor1", amount=100, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="vendor3", amount=300, date="2024-01-05"),
        Transaction(id=6, user_id="user1", name="vendor2", amount=200, date="2024-01-06"),
    ]


def test_get_n_transactions_same_amount(transactions) -> None:
    """Test that get_n_transactions_same_amount returns the correct number of transactions with the same amount."""
    assert get_n_transactions_same_amount(transactions[0], transactions) == 3
    assert get_n_transactions_same_amount(transactions[2], transactions) == 2


def test_get_percent_transactions_same_amount(transactions) -> None:
    """
    Test that get_percent_transactions_same_amount returns correct percentage.
    Tests that the function calculates the right percentage of transactions with matching amounts.
    """
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 3 / 6
    assert pytest.approx(get_percent_transactions_same_amount(transactions[2], transactions)) == 2 / 6


def test_get_most_frequent_names(transactions) -> None:
    """Test that get_most_frequent_names returns the correct most frequent names."""
    most_frequent_names = get_most_frequent_names(transactions)
    assert most_frequent_names == ["vendor1", "vendor2", "vendor3"]
