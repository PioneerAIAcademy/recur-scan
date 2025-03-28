# test features

import pytest

from recur_scan.features import (
    get_day_of_month_consistency,
    get_ends_in_99,
    get_is_always_recurring,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_n_transactions_same_description,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
    get_percent_transactions_same_description,
    get_transaction_frequency,
)
from recur_scan.transactions import Transaction


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
    """
    Test that get_percent_transactions_same_amount returns correct percentage.
    Tests that the function calculates the right percentage of transactions with matching amounts.
    """
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
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 0) == 2
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 1) == 4


def test_get_pct_transactions_days_apart() -> None:
    """Test get_pct_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_pct_transactions_days_apart(transactions[0], transactions, 14, 0) == 2 / 7
    assert get_pct_transactions_days_apart(transactions[0], transactions, 14, 1) == 4 / 7


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


def test_get_is_always_recurring() -> None:
    """Test get_is_always_recurring."""
    assert get_is_always_recurring(Transaction(id=1, user_id="user1", name="netflix", amount=100, date="2024-01-01"))
    assert not get_is_always_recurring(
        Transaction(id=2, user_id="user1", name="walmart", amount=100, date="2024-01-01")
    )


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


# def test_calculate_merchant_pattern_consistency(sample_transactions):
#     # Landlord transactions have consistent amount and name
#     target = sample_transactions[4]  # Rent transaction
#     merchant_transactions = [t for t in sample_transactions if t.name == "Landlord"]
#     assert calculate_merchant_pattern_consistency(
#         target,
#         sample_transactions,
#         merchant_transactions
#         ) == pytest.approx(1 / 6)

#     # Supermarket transactions have varying amounts
#     target = sample_transactions[0]  # Groceries transaction
#     merchant_transactions = [t for t in sample_transactions if t.name == "Supermarket"]
#     assert calculate_merchant_pattern_consistency(target, sample_transactions, merchant_transactions) == 0.0

#     # Test with empty lists
#     assert calculate_merchant_pattern_consistency(target, [], merchant_transactions) == 0.0
#     assert calculate_merchant_pattern_consistency(target, sample_transactions, []) == 0.0
