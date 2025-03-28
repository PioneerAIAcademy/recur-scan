import pytest

from recur_scan.features import (
    get_amount_std_dev,
    get_ends_in_99,
    get_is_always_recurring,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_is_weekend_transaction,
    get_median_transaction_amount,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
    get_transaction_frequency,
)
from recur_scan.transactions import Transaction


def test_get_is_always_recurring():
    transaction = Transaction(id=1, user_id="user1", name="Netflix", amount=100, date="2024-01-01")
    assert get_is_always_recurring(transaction) is True


def test_get_is_insurance():
    transaction = Transaction(id=1, user_id="user1", name="Health Insurance", amount=200, date="2024-01-01")
    assert get_is_insurance(transaction) is True


def test_get_is_utility():
    transaction = Transaction(id=1, user_id="user1", name="Duke Energy", amount=150, date="2024-01-01")
    assert get_is_utility(transaction) is True


def test_get_is_phone():
    transaction = Transaction(id=1, user_id="user1", name="Verizon", amount=80, date="2024-01-01")
    assert get_is_phone(transaction) is True


def test_get_n_transactions_days_apart():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=100, date="2024-01-15"),
    ]
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 0) == 1


def test_get_pct_transactions_days_apart():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=100, date="2024-01-15"),
    ]
    assert get_pct_transactions_days_apart(transactions[0], transactions, 14, 0) == 0.5


def test_get_n_transactions_same_day():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Spotify", amount=50, date="2024-01-01"),
    ]
    assert get_n_transactions_same_day(transactions[0], transactions, 0) == 2


def test_get_pct_transactions_same_day():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Spotify", amount=50, date="2024-01-01"),
    ]
    assert get_pct_transactions_same_day(transactions[0], transactions, 0) == 1.0


def test_get_ends_in_99():
    transaction = Transaction(id=1, user_id="user1", name="Product", amount=9.99, date="2024-01-01")
    assert get_ends_in_99(transaction) is True


def test_get_n_transactions_same_amount():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Spotify", amount=100, date="2024-01-08"),
    ]
    assert get_n_transactions_same_amount(transactions[0], transactions) == 2


def test_get_percent_transactions_same_amount():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Spotify", amount=100, date="2024-01-08"),
    ]
    assert get_percent_transactions_same_amount(transactions[0], transactions) == 1.0


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
