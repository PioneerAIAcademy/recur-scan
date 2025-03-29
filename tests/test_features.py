import unittest

import pytest

from recur_scan.features import (
    call_features,
    get_ends_in_99,
    get_is_always_recurring,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_newfeatures,
    get_percent_transactions_same_amount,
)
from recur_scan.transactions import Transaction


# Pytest-style tests
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
    """Test that get_percent_transactions_same_amount returns the correct percentage."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 0.5


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


def test_get_n_transactions_days_apart() -> None:
    """Test get_n_transactions_days_apart counts transactions within n_days_off of n_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=5, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=6, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=7, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 0) == 2
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 1) == 4


def test_get_is_insurance() -> None:
    """Test get_is_insurance identifies insurance transactions."""
    assert get_is_insurance(
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01")
    )
    assert not get_is_insurance(Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"))


def test_get_is_phone() -> None:
    """Test get_is_phone identifies phone transactions."""
    assert get_is_phone(Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"))
    assert not get_is_phone(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))


def test_get_is_utility() -> None:
    """Test get_is_utility identifies utility transactions."""
    assert get_is_utility(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))
    assert not get_is_utility(
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03")
    )


def test_get_is_always_recurring() -> None:
    """Test get_is_always_recurring identifies always-recurring vendors."""
    assert get_is_always_recurring(Transaction(id=1, user_id="user1", name="netflix", amount=100, date="2024-01-01"))
    assert not get_is_always_recurring(
        Transaction(id=2, user_id="user1", name="walmart", amount=100, date="2024-01-01")
    )


# Unittest-style tests with plain assert statements
class TestFeatureFunctions(unittest.TestCase):
    def test_call_features(self):
        """Test call_features calculates amount, frequency, and time-based features correctly."""
        transaction = {"amount": 100.0, "date": "2025-03-15"}
        group = [
            Transaction(amount=100.0, date="2025-03-01", id=1, user_id="user1", name="test"),
            Transaction(amount=100.0, date="2025-03-08", id=2, user_id="user1", name="test"),
            Transaction(amount=100.0, date="2025-03-15", id=3, user_id="user1", name="test"),
        ]
        expected_features = {
            "amount": 100.0,
            "frequency": 3,
            "avg_days_between": 7.0,
            "std_days_between": 0.0,
        }
        features = call_features(transaction, group)
        assert features["amount"] == expected_features["amount"]
        assert features["frequency"] == expected_features["frequency"]
        assert features["avg_days_between"] == pytest.approx(expected_features["avg_days_between"])
        assert features["std_days_between"] == pytest.approx(expected_features["std_days_between"])

    def test_get_newfeatures(self):
        """Test get_newfeatures calculates all features correctly."""
        transaction = Transaction(amount=100.0, date="2025-03-15", id=1, user_id="user1", name="test")
        group = [
            Transaction(amount=100.0, date="2025-03-01", id=2, user_id="user1", name="test"),
            Transaction(amount=100.0, date="2025-03-08", id=3, user_id="user1", name="test"),
            Transaction(amount=100.0, date="2025-03-15", id=4, user_id="user1", name="test"),
        ]
        expected_features = {
            "amount": 100.0,
            "n_transactions_same_amount": 3,
            "percent_transactions_same_amount": 1.0,
            "avg_days_between": 7.0,
            "std_days_between": 0.0,
            "min_days_between": 7,
            "max_days_between": 7,
        }
        features = get_newfeatures(transaction, group)
        assert features["amount"] == expected_features["amount"]
        assert features["n_transactions_same_amount"] == expected_features["n_transactions_same_amount"]
        assert features["percent_transactions_same_amount"] == pytest.approx(
            expected_features["percent_transactions_same_amount"]
        )
        assert features["avg_days_between"] == pytest.approx(expected_features["avg_days_between"])
        assert features["std_days_between"] == pytest.approx(expected_features["std_days_between"])
        assert features["min_days_between"] == expected_features["min_days_between"]
        assert features["max_days_between"] == expected_features["max_days_between"]


if __name__ == "__main__":
    unittest.main()
