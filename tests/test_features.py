import pytest

from recur_scan.features import (
    # amount_ends_in_00,
    # amount_ends_in_99,
    get_avg_days_between_same_merchant_amount,
    get_features,
    get_n_transactions_same_amount,
    get_percent_transactions_same_amount,
    is_recurring_merchant,
)
from recur_scan.transactions import Transaction


# Helper function to create transactions
def create_transaction(id, user_id, name, date, amount):
    return Transaction(id=id, user_id=user_id, name=name, date=date, amount=amount)


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
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 2 / 4


# def test_amount_ends_in_99(transactions) -> None:
#     """Test that amount_ends_in_99 returns True for amounts ending in 99."""
#     assert not amount_ends_in_99(transactions[0])
#     assert amount_ends_in_99(transactions[3])


# def test_amount_ends_in_00() -> None:
#     """Test that amount_ends_in_00 returns True for amounts ending in 00."""
#     transaction = create_transaction(1, "user1", "VendorA", "2023-01-01", 10.00)
#     assert amount_ends_in_00(transaction)
#     transaction = create_transaction(2, "user1", "VendorB", "2023-01-02", 9.99)
#     assert not amount_ends_in_00(transaction)


def test_is_recurring_merchant() -> None:
    """Test that is_recurring_merchant returns True for recurring merchants."""
    transaction = create_transaction(1, "user1", "Google Play", "2023-01-01", 10.00)
    assert is_recurring_merchant(transaction)
    transaction = create_transaction(2, "user1", "Local Store", "2023-01-02", 9.99)
    assert not is_recurring_merchant(transaction)


def test_get_avg_days_between_same_merchant_amount(transactions) -> None:
    """
    Test that get_avg_days_between_same_merchant_amount returns the correct average days
    between transactions with the same merchant and amount.
    """
    transactions = [
        create_transaction(1, "user1", "VendorA", "2023-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2023-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2023-01-15", 100.0),
    ]
    transaction = transactions[0]
    assert get_avg_days_between_same_merchant_amount(transaction, transactions) == 7.0


def test_get_features(transactions) -> None:
    """Test that get_features returns the correct features for a transaction."""
    transaction = transactions[0]
    features = get_features(transaction, transactions)
    assert features["n_transactions_same_amount"] == 2
    assert features["percent_transactions_same_amount"] == 2 / 4
    # assert not features["amount_ends_in_99"]
    # assert features["amount_ends_in_00"]
    assert not features["is_recurring_merchant"]
    assert features["avg_days_between_same_merchant_amount"] == 0.0
    assert round(features["average_transaction_amount"], 2) == 100.75
    assert features["max_transaction_amount"] == 200.0
    assert features["min_transaction_amount"] == 2.99
    assert features["most_frequent_names"] == 0
    assert not features["is_recurring"]
