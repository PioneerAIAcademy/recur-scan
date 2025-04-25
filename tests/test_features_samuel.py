import pytest

from recur_scan.features_samuel import (
    get_amount_std_dev,
    get_is_always_recurring,
    get_is_weekend_transaction,
    get_median_transaction_amount,
    get_transaction_frequency,
)
from recur_scan.transactions import Transaction


def test_get_is_always_recurring():
    transaction = Transaction(id=1, user_id="user1", name="Netflix", amount=100, date="2024-01-01")
    assert get_is_always_recurring(transaction) is True


def test_get_transaction_frequency():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=100, date="2024-01-08"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=100, date="2024-01-15"),
    ]
    assert get_transaction_frequency(transactions[0], transactions) == 3


def test_get_amount_std_dev():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=120, date="2024-01-08"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=110, date="2024-01-15"),
    ]
    assert pytest.approx(get_amount_std_dev(transactions[0], transactions), 0.01) == 8.16


def test_get_median_transaction_amount():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=90, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=110, date="2024-01-08"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=100, date="2024-01-15"),
    ]
    assert get_median_transaction_amount(transactions[0], transactions) == 100


def test_get_is_weekend_transaction():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=100, date="2024-03-23"),  # Saturday
        Transaction(id=2, user_id="user1", name="Netflix", amount=100, date="2024-03-25"),  # Monday
    ]
    assert get_is_weekend_transaction(transactions[0]) is True
    assert get_is_weekend_transaction(transactions[1]) is False
