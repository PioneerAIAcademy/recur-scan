import datetime
from math import isclose

import pytest

from recur_scan.features import (
    get_day,
    get_day_of_week,
    get_ends_in_99,
    get_is_always_recurring,
    get_is_insurance,
    get_is_utility,
    get_max_transaction_amount,
    get_min_transaction_amount,
    get_month,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_n_transactions_same_vendor,
    get_percent_transactions_same_amount,
    get_transaction_intervals,
    get_year,
    is_recurring_mobile_transaction,
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
        Transaction(id=1, user_id="user1", name="vendor1", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="vendor2", date="2023-01-02", amount=200.0),
        Transaction(id=3, user_id="user2", name="vendor1", date="2023-01-03", amount=300.0),
    ]
    assert get_max_transaction_amount(transactions) == 300.0


def test_get_min_transaction_amount():
    """
    Test that get_min_transaction_amount returns the correct minimum amount of all transactions.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="vendor2", date="2023-01-02", amount=200.0),
        Transaction(id=3, user_id="user2", name="vendor1", date="2023-01-03", amount=300.0),
    ]
    assert get_min_transaction_amount(transactions) == 100.0


def test_is_recurring_mobile_transaction() -> None:
    """
    Test that is_recurring_mobile_transaction returns True for mobile company transactions and False otherwise.
    """
    test_transactions = [
        Transaction(id=1, user_id="user1", name="T-Mobile", amount=50, date="2024-01-02"),  # Mobile company
        Transaction(id=2, user_id="user1", name="AT&T", amount=60, date="2024-01-03"),  # Mobile company
        Transaction(id=3, user_id="user1", name="Verizon", amount=70, date="2024-01-04"),  # Mobile company
        Transaction(id=4, user_id="user1", name="Boost Mobile", amount=80, date="2024-02-01"),  # Mobile company
        Transaction(id=5, user_id="user1", name="Tello Mobile", amount=90, date="2024-03-01"),  # Mobile company
        Transaction(id=6, user_id="user1", name="Amazon", amount=100, date="2024-01-01"),  # NOT a mobile company
        Transaction(id=7, user_id="user1", name="Walmart", amount=110, date="2024-02-15"),  # NOT a mobile company
    ]

    assert is_recurring_mobile_transaction(test_transactions[0]) is True  # T-Mobile
    assert is_recurring_mobile_transaction(test_transactions[1]) is True  # AT&T
    assert is_recurring_mobile_transaction(test_transactions[2]) is True  # Verizon
    assert is_recurring_mobile_transaction(test_transactions[3]) is True  # Boost Mobile
    assert is_recurring_mobile_transaction(test_transactions[4]) is True  # Tello Mobile
    assert is_recurring_mobile_transaction(test_transactions[5]) is False  # Amazon (not a mobile company)
    assert is_recurring_mobile_transaction(test_transactions[6]) is False  # Walmart (not a mobile company)


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


def test_get_day_of_week(transactions) -> None:
    """Test that get_day_of_week returns the correct day of the week for the transaction date."""
    transaction = transactions[0]
    assert get_day_of_week(transaction) == 0  # 0 = Monday


def test_get_month(transactions) -> None:
    """Test that get_month returns the correct month for the transaction date."""
    transaction = transactions[0]
    assert get_month(transaction) == 1


def test_get_day(transactions) -> None:
    """Test that get_day returns the correct day for the transaction date."""
    transaction = transactions[0]
    assert get_day(transaction) == 1


def test_get_year(transactions) -> None:
    """Test that get_year returns the correct year for the transaction date."""
    transaction = transactions[0]
    assert get_year(transaction) == 2024


def test_get_ends_in_99() -> None:
    """Test that get_ends_in_99 returns True if the transaction amount ends in 99."""
    transaction = Transaction(id=1, user_id="user1", name="vendor1", amount=99.99, date="2024-01-01")
    assert get_ends_in_99(transaction) is True

    transaction = Transaction(id=2, user_id="user1", name="vendor2", amount=100.00, date="2024-01-02")
    assert get_ends_in_99(transaction) is False


def test_get_is_insurance() -> None:
    """Test that get_is_insurance returns True if the transaction is from a known insurance company."""
    transaction = Transaction(id=1, user_id="user1", name="Geico", amount=100.0, date="2024-01-01")
    assert get_is_insurance(transaction) is True

    transaction = Transaction(id=2, user_id="user1", name="Amazon", amount=100.0, date="2024-01-02")
    assert get_is_insurance(transaction) is False


def test_get_is_utility() -> None:
    """Test that get_is_utility returns True if the transaction is from a known utility company."""
    transaction = Transaction(id=1, user_id="user1", name="Electricity", amount=100.0, date="2024-01-01")
    assert get_is_utility(transaction) is True

    transaction = Transaction(id=2, user_id="user1", name="Amazon", amount=100.0, date="2024-01-02")
    assert get_is_utility(transaction) is False


def test_get_is_always_recurring() -> None:
    """Test that get_is_always_recurring returns True if the transaction is from a known recurring vendor."""
    transaction = Transaction(id=1, user_id="user1", name="Netflix", amount=100.0, date="2024-01-01")
    assert get_is_always_recurring(transaction) is True

    transaction = Transaction(id=2, user_id="user1", name="Amazon", amount=100.0, date="2024-01-02")
    assert get_is_always_recurring(transaction) is False


def test_get_n_transactions_days_apart() -> None:
    """Test that get_n_transactions_days_apart returns the correct number of transactions that are n days apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-15"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=100, date="2024-01-29"),
        Transaction(id=4, user_id="user1", name="vendor1", amount=100, date="2024-02-12"),
    ]
    transaction = transactions[0]
    assert get_n_transactions_days_apart(transaction, transactions, 14, 0) == 3
    assert get_n_transactions_days_apart(transaction, transactions, 14, 1) == 3
    assert get_n_transactions_days_apart(transaction, transactions, 14, 2) == 3


def test_get_n_transactions_same_day() -> None:
    """Test that get_n_transactions_same_day returns the correct number of transactions on the same day of the month."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=100, date="2024-03-01"),
        Transaction(id=4, user_id="user1", name="vendor1", amount=100, date="2024-04-01"),
    ]
    transaction = transactions[0]
    assert get_n_transactions_same_day(transaction, transactions, 0) == 4
    assert get_n_transactions_same_day(transaction, transactions, 1) == 4
    assert get_n_transactions_same_day(transaction, transactions, 2) == 4
