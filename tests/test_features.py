# test features
import pytest

from recur_scan.features import (
    get_day_of_week_features,
    get_features,
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
def test_get_day_of_week_features(transactions) -> None:
    """Test that get_day_of_week_features returns the correct day of the month and weekday."""
    # Transaction on January 1, 2024, which is a Monday
    result = get_day_of_week_features(transactions[0])
    assert result["day_of_month"] == 1
    assert result["weekday"] == 0  # Monday = 0

    # Transaction on January 2, 2024, which is a Tuesday
    result = get_day_of_week_features(transactions[1])
    assert result["day_of_month"] == 2
    assert result["weekday"] == 1  # Tuesday = 1


def test_get_features(transactions) -> None:
    """Test that get_features returns the correct dictionary of features."""
    result = get_features(transactions[0], transactions)
    expected = {
        "n_transactions_same_amount": 2,
        "percent_transactions_same_amount": 2 / 3,
        "day_of_month": 1,
        "weekday": 0,
        "week_of_year": 1,
        "frequency": 1.0,  
        "date_variability": 0,

    }
    assert result == expected

    result = get_features(transactions[2], transactions)
    expected = {
        "n_transactions_same_amount": 1,
        "percent_transactions_same_amount": 1 / 3,
        "day_of_month": 3,
        "weekday": 2,
        "week_of_year": 1,  
        "frequency": 1.0,  
        "date_variability": 0,

    }
    assert result == expected
