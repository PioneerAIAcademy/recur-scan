# test features
import pytest

from recur_scan.features import (
    get_day_of_week_features,
    get_features,
    get_n_transactions_same_amount,
    get_percent_transactions_same_amount,
    get_frequency_features,
    get_time_features,
    get_vendor_features,
    get_amount_features
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
    result = get_day_of_week_features(transactions[0], transactions)
    assert result["day_of_month"] == 1
    assert result["weekday"] == 0  # Monday = 0
    assert result["is_weekend"] == 0  # Monday is not a weekend
    assert result["days_since_last_transaction"] == 0 

    # Transaction on January 2, 2024, which is a Tuesday
    result = get_day_of_week_features(transactions[1], transactions)
    assert result["day_of_month"] == 2
    assert result["weekday"] == 1  # Tuesday = 1
    assert result["is_weekend"] == 0  # Tuesday is not a weekend
    assert result["days_since_last_transaction"] == 1 

def test_get_frequency_features(transactions) -> None:
    """Test that get_frequency_features returns the correct frequency and variability."""
    result = get_frequency_features(transactions[0], transactions)
    assert result["frequency"] == 1.0  
    assert result["date_variability"] == 0  
    assert result["median_frequency"] == 1.0  
    assert pytest.approx(result["std_frequency"]) == 0.0 

def test_get_time_features(transactions) -> None:
    """Test that get_time_features returns the correct time-related features."""
    result = get_time_features(transactions[0], transactions)
    assert result["month"] == 1
    assert result["days_until_next_transaction"] == 1 

def test_get_vendor_features(transactions) -> None:
    """Test that get_vendor_features returns the correct vendor-related features."""
    result = get_vendor_features(transactions[0], transactions)
    assert result["n_transactions_with_vendor"] == 3  # 3 transactions for vendor1
    assert pytest.approx(result["avg_amount_for_vendor"]) == (100 + 100 + 200) / 3

def test_get_amount_features() -> None:
    """Test that get_amount_features returns the correct amount-related features."""
    transaction = Transaction(id=1, user_id="user1", name="vendor1", amount=100.00, date="2024-01-01")
    result = get_amount_features(transaction)
    assert result["is_amount_rounded"] == 1  # 100.00 is a rounded amount
    assert result["amount_category"] == 10  

def test_get_features(transactions) -> None:
    """Test that get_features returns the correct dictionary of features."""
    result = get_features(transactions[0], transactions)
    expected = {
        "n_transactions_same_amount": 2,
        "percent_transactions_same_amount": 2 / 3,
        "day_of_month": 1,
        "weekday": 0,
        "week_of_year": 1,
        "is_weekend": 0,
        "days_since_last_transaction": 0,
        "frequency": 1.0,  
        "date_variability": 0,
        "median_frequency": 1.0,
        "std_frequency": 0.0,
        "is_amount_rounded": 1,
        "amount_category": 10,
        "n_transactions_with_vendor": 3,
        "avg_amount_for_vendor": pytest.approx((100 + 100 + 200) / 3),
        "month": 1,
        "days_until_next_transaction": 1,
        "is_recurring": True,
    }
    assert result == expected

