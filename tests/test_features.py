import datetime
from math import isclose

import pytest

from recur_scan.features import (
    get_max_transaction_amount,
    get_min_transaction_amount,
    get_n_transactions_same_amount,
    get_n_transactions_same_vendor,
    get_percent_transactions_same_amount,
    get_transaction_intervals,
)
from recur_scan.transactions import Transaction


@pytest.fixture
def transactions():
    """Fixture providing test transactions."""
    return [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="vendor2", amount=300, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="vendor1", amount=100, date="2024-02-01"),
        Transaction(id=6, user_id="user1", name="vendor1", amount=100, date="2024-03-01"),
        Transaction(id=7, user_id="user2", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=8, user_id="user2", name="vendor1", amount=100, date="2024-01-15"),
        Transaction(id=9, user_id="user2", name="vendor1", amount=100, date="2024-02-01"),
    ]


def test_get_n_transactions_same_amount(transactions) -> None:
    """Test that get_n_transactions_same_amount returns the correct number of transactions with the same amount."""
    assert get_n_transactions_same_amount(transactions[0], transactions) == 7
    assert get_n_transactions_same_amount(transactions[2], transactions) == 1


def test_get_percent_transactions_same_amount(transactions) -> None:
    """
    Test that get_percent_transactions_same_amount returns correct percentage.
    Tests that the function calculates the right percentage of transactions with matching amounts.
    """
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 7 / 9
    assert pytest.approx(get_percent_transactions_same_amount(transactions[2], transactions)) == 1 / 9


def test_get_n_transactions_same_vendor(transactions) -> None:
    """Test that get_n_transactions_same_vendor returns the correct number of transactions with the same vendor."""
    assert get_n_transactions_same_vendor(transactions[0], transactions) == 8
    assert get_n_transactions_same_vendor(transactions[3], transactions) == 1


def test_get_max_transaction_amount():
    """
    Test that get_max_transaction_amount returns the correct maximum amount of all transactions.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="VendorA", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="VendorB", date="2023-01-02", amount=200.0),
        Transaction(id=3, user_id="user2", name="VendorA", date="2023-01-03", amount=300.0),
    ]
    assert get_max_transaction_amount(transactions) == 300.0


def test_get_min_transaction_amount():
    """
    Test that get_min_transaction_amount returns the correct minimum amount of all transactions.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="VendorA", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="VendorB", date="2023-01-02", amount=200.0),
        Transaction(id=3, user_id="user2", name="VendorA", date="2023-01-03", amount=300.0),
    ]
    assert get_min_transaction_amount(transactions) == 100.0


def test_get_transaction_intervals_single_transaction():
    """
    Test get_transaction_intervals with only one transaction.

    With a single transaction, there is no interval to compute so all features should be zero.
    """
    single_tx = [
        Transaction(
            id=1,
            user_id="user1",
            name="vendor1",
            amount=100,
            date=datetime.datetime.strptime("2024-01-02", "%Y-%m-%d").date(),
        )
    ]
    result = get_transaction_intervals(single_tx)
    expected = {
        "avg_days_between_transactions": 0.0,
        "std_dev_days_between_transactions": 0.0,
        "monthly_recurrence": 0,
        "same_weekday": 0,
        "same_amount": 0,
    }
    assert result == expected


def test_get_transaction_intervals_multiple_transactions():
    """
    Test get_transaction_intervals with multiple transactions.

    This test includes transactions with different dates, amounts, and weekdays.
    """
    transactions = [
        Transaction(
            id=1,
            user_id="user1",
            name="vendor1",
            amount=100,
            date=datetime.datetime.strptime("2024-01-02", "%Y-%m-%d").date(),
        ),
        Transaction(
            id=2,
            user_id="user1",
            name="vendor1",
            amount=100,
            date=datetime.datetime.strptime("2024-02-09", "%Y-%m-%d").date(),
        ),
        Transaction(
            id=3,
            user_id="user1",
            name="vendor1",
            amount=200,
            date=datetime.datetime.strptime("2024-03-03", "%Y-%m-%d").date(),
        ),
    ]
    result = get_transaction_intervals(transactions)
    expected = {
        "avg_days_between_transactions": 30.5,
        "std_dev_days_between_transactions": 10.6066,
        "monthly_recurrence": 1.0,
        "same_weekday": 0,
        "same_amount": 2 / 3,
    }
    print("Result:", result)
    print("Expected:", expected)

    assert isclose(result["avg_days_between_transactions"], expected["avg_days_between_transactions"], rel_tol=1e-5)
    assert isclose(
        result["std_dev_days_between_transactions"], expected["std_dev_days_between_transactions"], rel_tol=1e-3
    )
    assert result["monthly_recurrence"] == expected["monthly_recurrence"]
    assert result["same_weekday"] == expected["same_weekday"]
    assert result["same_amount"] == expected["same_amount"]
