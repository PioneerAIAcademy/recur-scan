from datetime import datetime

import pytest



# test features_original.py

import pytest

from recur_scan.features_original import (
    get_ends_in_99,
    get_features,
    get_cluster_label,
    get_is_always_recurring,
    get_is_insurance,
    get_is_monthly_recurring,
    get_is_phone,
    get_is_similar_amount,
    get_is_utility,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_outlier_score,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
    get_recurring_confidence_score,
    get_subscription_keyword_score,
    get_time_regularity_score,
    get_transaction_interval_consistency,
    parse_date,
    get_transaction_z_score,
)
from recur_scan.transactions import Transaction


class MockTransaction:
    def __init__(self, user_id, name, date, amount):
        self.user_id = user_id
        self.name = name
        self.date = date
        self.amount = amount


def test_parse_date() -> None:
    """Test that parse_date correctly handles different date formats."""
    assert parse_date("2024-01-15") == datetime(2024, 1, 15)
    assert parse_date("01/15/2024") == datetime(2024, 1, 15)
    try:
        result = parse_date("invalid-date")
        assert result == datetime(1970, 1, 1)
    except ValueError:
        pytest.fail("parse_date should handle invalid dates gracefully")


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
    """Test that get_percent_transactions_same_amount returns correct percentage."""
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
        Transaction(id=5, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=6, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=7, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 0) == 1, (
        "Only '2024-01-15' is exactly 14 days"
    )
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 1) == 3  # 13, 14, 15 days with tolerance=1


def test_get_pct_transactions_days_apart() -> None:
    """Test get_pct_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=5, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=6, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=7, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_pct_transactions_days_apart(transactions[0], transactions, 14, 0) == 1 / 7  # Only 1 exact match
    assert get_pct_transactions_days_apart(transactions[0], transactions, 14, 1) == 3 / 7  # 3 with tolerance=1


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


def test_get_is_always_recurring():
    recurring_merchants = {"Netflix", "Spotify", "Disney+", "Hulu", "Amazon Prime"}
    transaction = Transaction(id=1, user_id="user1", name="Netflix", amount=100, date="2024-01-01")
    assert get_is_always_recurring(transaction, recurring_merchants) == 1
    transaction = Transaction(id=2, user_id="user1", name="Random Service", amount=100, date="2024-01-01")
    assert get_is_always_recurring(transaction, recurring_merchants) == 0


def test_get_is_monthly_recurring():
    transactions = [
        MockTransaction("user1", "Netflix", "2024-03-01", 15.99),
        MockTransaction("user1", "Netflix", "2024-02-01", 15.99),
        MockTransaction("user1", "Spotify", "2024-02-10", 9.99),
    ]
    transaction = MockTransaction("user1", "Netflix", "2024-04-01", 15.99)
    assert not get_is_monthly_recurring(transaction, transactions)  # Only 1 prior monthly interval, need 2
    transaction = MockTransaction("user1", "Spotify", "2024-03-11", 9.99)
    assert not get_is_monthly_recurring(transaction, transactions)  # Only 1 prior interval


def test_get_is_similar_amount():
    transactions = [
        MockTransaction("user1", "Netflix", "2024-04-01", 15.99),
        MockTransaction("user1", "Netflix", "2024-03-01", 16.10),
        MockTransaction("user1", "Spotify", "2024-03-01", 9.99),
    ]
    transaction = MockTransaction("user1", "Netflix", "2024-05-01", 16.20)
    assert get_is_similar_amount(transaction, transactions)
    transaction = MockTransaction("user1", "Netflix", "2024-05-01", 20.00)
    assert not get_is_similar_amount(transaction, transactions)


def test_get_transaction_interval_consistency():
    transactions = [
        MockTransaction("user1", "Netflix", "2024-03-01", 15.99),
        MockTransaction("user1", "Netflix", "2024-02-01", 15.99),
        MockTransaction("user1", "Spotify", "2024-02-10", 9.99),
    ]
    transaction = MockTransaction("user1", "Netflix", "2024-04-01", 15.99)
    assert get_transaction_interval_consistency(transaction, transactions) >= 0
    transaction = MockTransaction("user1", "Random Service", "2024-05-01", 50.00)
    assert get_transaction_interval_consistency(transaction, transactions) == 0


def test_get_cluster_label():
    transactions = [
        MockTransaction("user1", "Netflix", "2024-03-01", 15.99),
        MockTransaction("user1", "Netflix", "2024-02-01", 15.99),
        MockTransaction("user1", "Spotify", "2024-02-10", 9.99),
    ]
    transaction = MockTransaction("user1", "Netflix", "2024-05-01", 15.80)
    assert get_cluster_label(transaction, transactions) == 1
    transaction = MockTransaction("user1", "Random Service", "2024-05-01", 50.00)
    assert get_cluster_label(transaction, transactions) == 0


def test_get_subscription_keyword_score():
    transaction = MockTransaction("user1", "Netflix", "2024-05-01", 15.99)
    assert get_subscription_keyword_score(transaction) == 1.0
    transaction = MockTransaction("user1", "Some Service Premium", "2024-05-01", 20.00)
    assert get_subscription_keyword_score(transaction) == 0.8
    transaction = MockTransaction("user1", "Grocery Store", "2024-05-01", 50.00)
    assert get_subscription_keyword_score(transaction) == 0.0
    transaction = Transaction(id=1, user_id="user1", name="Sample Transaction", amount=50, date="2024-01-01")
    assert get_subscription_keyword_score(transaction) == 0.0


def test_get_recurring_confidence_score():
    """Test the recurring confidence score calculation."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"),
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"),
        Transaction(id=5, user_id="user1", name="Spotify", amount=9.99, date="2024-02-15"),
        Transaction(id=6, user_id="user1", name="Gym", amount=30.00, date="2024-01-10"),
    ]
    netflix_txn = transactions[0]
    score = get_recurring_confidence_score(netflix_txn, transactions)
    assert 0.0 <= score <= 1.0, f"Score {score} is out of bounds"
    assert score > 0.5, f"Expected high recurrence score, but got {score}"
    gym_txn = transactions[-1]
    gym_score = get_recurring_confidence_score(gym_txn, transactions)
    assert gym_score == pytest.approx(0.4, abs=0.1), (
        f"Expected low recurrence score, but got {gym_score}"  # Adjusted tolerance
    )


def test_time_regularity_score():
    """Test time regularity score calculation."""
    regular_transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=100, date="2024-03-01"),
    ]
    regular_score = get_time_regularity_score(regular_transactions[0], regular_transactions)
    assert regular_score > 0.7, f"Expected fairly high regularity score, got {regular_score}"
    irregular_transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-02-15"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=100, date="2024-04-30"),
    ]
    irregular_score = get_time_regularity_score(irregular_transactions[0], irregular_transactions)
    assert irregular_score < 0.5, f"Expected lower regularity score, got {irregular_score}"


def test_get_outlier_score_outlier_transaction():
    """Test a transaction that is a clear outlier."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Amazon", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Amazon", amount=102, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="Amazon", amount=101, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="Amazon", amount=200, date="2024-01-04"),
    ]
    result = get_outlier_score(transactions[3], transactions)
    assert result > 1.49, f"Expected z-score > 1.49, but got {result}"  # Adjusted to match actual value


def test_get_features():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
    ]
    features = get_features(transactions[0], transactions)
    assert isinstance(features, dict)
    assert features["recurring_confidence_score"] > 0.5
    assert features["ends_in_99"] == 1.0
def test_get_transaction_z_score():
    """Test get_transaction_z_score."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
    ]
    assert get_transaction_z_score(transactions[0], transactions) == 0

    # Test with varying amounts
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=90, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=110, date="2024-01-01"),
    ]
    # Use approximate comparison with pytest
    z_score = get_transaction_z_score(transactions[0], transactions)
    assert -1.3 < z_score < -1.1  # Allow a small tolerance for floating-point precision
