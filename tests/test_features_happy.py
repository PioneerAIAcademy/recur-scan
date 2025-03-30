# test features

import pytest

from recur_scan.features_happy import (
    get_day_of_month_consistency,
    get_n_transactions_same_description,
    get_percent_transactions_same_description,
    get_transaction_frequency,
)
from recur_scan.transactions import Transaction


# Test data setup
@pytest.fixture
def sample_transactions():
    return [
        Transaction(id=1, user_id="user1", name="Supermarket", amount=50.0, date="2023-01-15"),
        Transaction(id=2, user_id="user1", name="Supermarket", amount=75.0, date="2023-01-20"),
        Transaction(id=3, user_id="user1", name="Supermarket", amount=60.0, date="2023-02-15"),
        Transaction(id=4, user_id="user1", name="Employer", amount=2000.0, date="2023-01-01"),
        Transaction(id=5, user_id="user1", name="Landlord", amount=1000.0, date="2023-01-01"),
        Transaction(id=6, user_id="user1", name="Landlord", amount=1000.0, date="2023-02-01"),
    ]


@pytest.fixture
def periodic_transactions():
    return [
        Transaction(id=1, user_id="user1", name="Streaming", amount=10.0, date="2023-01-01"),
        Transaction(id=2, user_id="user1", name="Streaming", amount=10.0, date="2023-01-08"),
        Transaction(id=3, user_id="user1", name="Streaming", amount=10.0, date="2023-01-15"),
        Transaction(id=4, user_id="user1", name="Streaming", amount=10.0, date="2023-01-22"),
    ]


# Test cases (remain the same as before)
def test_get_n_transactions_same_description(sample_transactions):
    target = sample_transactions[0]  # Groceries transaction
    assert get_n_transactions_same_description(target, sample_transactions) == 3

    target = sample_transactions[3]  # Salary transaction
    assert get_n_transactions_same_description(target, sample_transactions) == 1

    # Test with empty list
    assert get_n_transactions_same_description(target, []) == 0


def test_get_percent_transactions_same_description(sample_transactions):
    target = sample_transactions[0]  # Groceries transaction
    assert get_percent_transactions_same_description(target, sample_transactions) == 0.5

    target = sample_transactions[3]  # Salary transaction
    assert get_percent_transactions_same_description(target, sample_transactions) == pytest.approx(1 / 6)

    # Test with empty list
    assert get_percent_transactions_same_description(target, []) == 0.0


def test_get_transaction_frequency(sample_transactions, periodic_transactions):
    # Test with periodic transactions (weekly)
    target = periodic_transactions[0]
    assert get_transaction_frequency(target, periodic_transactions) == 7.0

    # Test with non-periodic transactions
    target = sample_transactions[0]
    assert get_transaction_frequency(target, sample_transactions) == pytest.approx(15.5)  # (5 + 26) / 2

    # Test with insufficient data
    single_transaction = [sample_transactions[0]]
    assert get_transaction_frequency(target, single_transaction) == 0.0


def test_get_day_of_month_consistency(sample_transactions):
    # Rent transactions are on the 1st consistently
    target = sample_transactions[4]  # Rent transaction
    assert get_day_of_month_consistency(target, sample_transactions) == 1.0

    # Groceries transactions are on 15th and 20th (inconsistent)
    target = sample_transactions[0]  # Groceries transaction
    assert get_day_of_month_consistency(target, sample_transactions) == pytest.approx(2 / 3)

    # Test with insufficient data
    single_transaction = [sample_transactions[0]]
    assert get_day_of_month_consistency(target, single_transaction) == 0.0
