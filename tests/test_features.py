import unittest
from datetime import datetime

import pytest
from recur_scan.features import calculate_merchant_pattern_consistency
from recur_scan.features import (
    Transaction,
    _get_days,
    get_day_of_month_consistency,
    get_ends_in_99,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_n_transactions_same_description,
    get_percent_transactions_same_amount,
    get_percent_transactions_same_description,
    get_transaction_frequency,
)
# Removed duplicate import of Transaction to avoid conflicts

@pytest.fixture
def transactions():
    """Fixture providing test transactions."""
    return [
        Transaction(name="Allstate Insurance", amount=100, date="2024-01-01"),
        Transaction(name="AT&T", amount=100, date="2024-01-01"),
        Transaction(name="Duke Energy", amount=200, date="2024-01-02"),
        Transaction(name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03"),
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


def test_get_ends_in_99(transactions) -> None:
    """Test that get_ends_in_99 returns True for amounts ending in 99."""
    assert not get_ends_in_99(transactions[0])
    assert get_ends_in_99(transactions[3])


def test_get_n_transactions_same_day(transactions) -> None:
    """Test that get_n_transactions_same_day returns the correct number of transactions on the same day."""
    assert get_n_transactions_same_day(transactions[0], transactions, 0) == 2
    assert get_n_transactions_same_day(transactions[0], transactions, 1) == 3
    assert get_n_transactions_same_day(transactions[2], transactions, 0) == 1


def test_get_days_since_epoch() -> None:
    """Test get the number of days since the epoch."""
    assert _get_days(datetime(1970, 1, 1).strftime("%Y-%m-%d")) == 0
    assert _get_days(datetime(1971, 1, 1).strftime("%Y-%m-%d")) == 365
    assert _get_days(datetime(1970, 2, 1).strftime("%Y-%m-%d")) == 31


def test_get_n_transactions_days_apart() -> None:
    """Test get_n_transactions_days_apart."""
    transactions = [
        Transaction(name="name1", amount=2.99, date="2024-01-01"),
        Transaction(name="name1", amount=2.99, date="2024-01-02"),
        Transaction(name="name1", amount=2.99, date="2024-01-14"),
        Transaction(name="name1", amount=2.99, date="2024-01-15"),
        Transaction(name="name1", amount=2.99, date="2024-01-16"),
        Transaction(name="name1", amount=2.99, date="2024-01-29"),
        Transaction(name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 0) == 2
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 1) == 4


def test_get_is_insurance(transactions) -> None:
    """Test get_is_insurance."""
    assert get_is_insurance(transactions[0])
    assert not get_is_insurance(transactions[1])


def test_get_is_phone(transactions) -> None:
    """Test get_is_phone."""
    assert get_is_phone(transactions[1])
    assert not get_is_phone(transactions[2])


def test_get_is_utility(transactions) -> None:
    """Test get_is_utility."""
    assert get_is_utility(transactions[2])
    assert not get_is_utility(transactions[3])


def test_get_n_transactions_same_description():
    t1 = Transaction(name="Groceries", amount=50, date="2024-01-01")
    t2 = Transaction(name="Groceries", amount=50, date="2024-01-02")
    t3 = Transaction(name="Rent", amount=1000, date="2024-01-03")
    t4 = Transaction(name="Groceries", amount=50, date="2024-01-04")
    all_transactions = [t1, t2, t3, t4]

    assert get_n_transactions_same_description(t1, all_transactions) == 3
    assert get_n_transactions_same_description(t3, all_transactions) == 1
    assert (
        get_n_transactions_same_description(
            Transaction(name="Utilities", amount=100, date="2024-01-05"), all_transactions
        )
        == 0
    )


def test_get_percent_transactions_same_description():
    t1 = Transaction(name="Groceries", amount=50, date="2024-01-01")
    t2 = Transaction(name="Groceries", amount=50, date="2024-01-02")
    t3 = Transaction(name="Rent", amount=1000, date="2024-01-03")
    t4 = Transaction(name="Groceries", amount=50, date="2024-01-04")
    all_transactions = [t1, t2, t3, t4]

    assert get_percent_transactions_same_description(t1, all_transactions) == 3 / 4
    assert get_percent_transactions_same_description(t3, all_transactions) == 1 / 4
    assert (
        get_percent_transactions_same_description(
            Transaction(name="Utilities", amount=100, date="2024-01-05"), all_transactions
        )
        == 0.0
    )
    assert get_percent_transactions_same_description(t1, []) == 0.0


class TestTransactionFeatures(unittest.TestCase):
    def setUp(self):
        # Common transactions for all tests
        self.transactions = [
            Transaction(name="Netflix", amount=15.99, date="2023-01-15"),
            Transaction(name="Netflix", amount=15.99, date="2023-02-15"),
            Transaction(name="Netflix", amount=15.99, date="2023-03-15"),
            Transaction(name="Spotify", amount=9.99, date="2023-01-10"),
            Transaction(name="Spotify", amount=9.99, date="2023-02-10"),
            Transaction(name="Spotify", amount=9.99, date="2023-03-10"),
            Transaction(name="Gym", amount=50.0, date="2023-01-05"),
            Transaction(name="Gym", amount=50.0, date="2023-02-05"),
            Transaction(name="Gym", amount=50.0, date="2023-03-05"),
        ]



def test_transaction_frequency(self):
    netflix_transaction = self.transactions[0]
    frequency = get_transaction_frequency(netflix_transaction, self.transactions)
    assert abs(frequency - 29.5) < 0.1  # Replace assertAlmostEqual

    single_transaction = Transaction(name="Single", amount=10.0, date="2023-01-01")
    frequency = get_transaction_frequency(single_transaction, self.transactions)
    assert frequency == 0.0  # Replace assertEqual


def test_get_day_of_month_consistency(self):
    # Test with Netflix transactions (all on the 15th)
    netflix_transaction = self.transactions[0]
    consistency = get_day_of_month_consistency(netflix_transaction, self.transactions)
    assert consistency == 1.0  # 100% consistency for Netflixistency for Netflix

    # Test with transactions that have inconsistent days
    inconsistent_transactions = [
        Transaction(name="Inconsistent", amount=10.0, date="2023-01-05"),
        Transaction(name="Inconsistent", amount=10.0, date="2023-02-10"),
        Transaction(name="Inconsistent", amount=10.0, date="2023-03-15"),
    ]
    inconsistent_transaction = inconsistent_transactions[0]
    consistency = get_day_of_month_consistency(inconsistent_transaction, inconsistent_transactions)
    assert abs(consistency - (1 / 3)) < 0.0010



import pytest
from recur_scan.features import interval_based_on_periodic

# Test cases grouped by pattern type
WEEKLY_TESTS = [
    ({"mean": 7, "std": 1}, 1.0),      # Perfect weekly
    ({"mean": 6, "std": 0.5}, 0.5),    # 1 day under weekly
    ({"mean": 8, "std": 1.5}, 0.5),    # 1 day over weekly
    ({"mean": 5, "std": 2}, 0.0),      # Too far from weekly
    ({"mean": 7, "std": 5}, 0.0),      # Too inconsistent
]

MONTHLY_TESTS = [
    ({"mean": 30, "std": 1}, 1.0),     # Perfect monthly
    ({"mean": 28, "std": 2}, 0.666),   # 2 days under
    ({"mean": 33, "std": 1}, 0.666),   # 3 days over
    ({"mean": 25, "std": 1}, 0.0),     # Too far
]

YEARLY_TESTS = [
    ({"mean": 365, "std": 5}, 1.0),    # Perfect yearly
    ({"mean": 355, "std": 4}, 0.5),    # 10 days under
    ({"mean": 375, "std": 3}, 0.5),    # 10 days over
]

EDGE_CASES = [
    ({"mean": 0, "std": 0}, 0.0),      # Zero mean
    ({}, 0.0),                         # Empty input
    ({"mean": 10}, 0.0),               # Missing std
    ({"mean": 100, "std": 1}, 0.0),    # No matching pattern
]

@pytest.mark.parametrize("interval_stats, expected",
    WEEKLY_TESTS + MONTHLY_TESTS + YEARLY_TESTS + EDGE_CASES)
def test_interval_based_on_periodic(interval_stats, expected):
    """Test various interval patterns and edge cases"""
    assert pytest.approx(interval_based_on_periodic(interval_stats), abs=0.01) == expected

def test_prioritizes_closest_pattern():
    """Should return the highest score among all matching patterns"""
    # Between weekly and monthly (closer to weekly)
    assert interval_based_on_periodic({"mean": 10, "std": 1}) > 0
    # Between monthly and yearly (closer to monthly)
    assert interval_based_on_periodic({"mean": 50, "std": 2}) > 0

def test_requires_low_std_deviation():
    """Should return 0 if standard deviation is too high"""
    assert interval_based_on_periodic({"mean": 7, "std": 5}) == 0
    assert interval_based_on_periodic({"mean": 30, "std": 10}) == 0







@pytest.fixture
def sample_transactions():
    return [
        Transaction(25.99, "Coffee Shop", date="2024-01-01"),
        Transaction(25.99, "Coffee Shop", date="2024-01-02"),
        Transaction(12.50, "Coffee Shop", date="2024-01-03"),
        Transaction(100.00, "Electronics Store", date="2024-01-04"),
        Transaction(25.99, "Different Merchant", date="2024-01-05")
    ]

def test_high_consistency(sample_transactions):
    target = Transaction(amount=25.99, name="Coffee Shop", date="2024-01-01")
    merchant_only = [t for t in sample_transactions if t.name == "Coffee Shop"]

    result = calculate_merchant_pattern_consistency(
        target,
        sample_transactions,
        merchant_only
    )
    assert result == pytest.approx(0.4)  # 2 matches / 5 total

def test_no_matches(sample_transactions):
    target = Transaction(9.99, "Coffee Shop", date="2024-01-01")
    merchant_only = [t for t in sample_transactions if t.name == "Coffee Shop"]

    result = calculate_merchant_pattern_consistency(
        target,
        sample_transactions,
        merchant_only
    )
    assert result == 0.0

def test_empty_transactions():
    assert calculate_merchant_pattern_consistency(
        Transaction(1.0, "Test", date="2024-01-01"),
        [],
        []
    ) == 0.0

def test_perfect_match():
    transactions = [
        Transaction(10.0, "Test Merchant", date="2024-01-01"),
        Transaction(10.0, "Test Merchant", date="2024-01-02"),
        Transaction(10.0, "Test Merchant", date="2024-01-03")
    ]

    result = calculate_merchant_pattern_consistency(
        transactions[0],
        transactions,
        transactions
    )
    assert result == 1.0

def test_partial_match(sample_transactions):
    target = Transaction(12.50, "Coffee Shop", date="2024-01-01")
    merchant_only = [t for t in sample_transactions if t.name == "Coffee Shop"]

    result = calculate_merchant_pattern_consistency(
        target,
        sample_transactions,
        merchant_only
    )
    assert result == pytest.approx(0.2)  # 1 match / 5 total

def test_different_merchant_excluded(sample_transactions):
    target = Transaction(25.99, "Coffee Shop", date="2024-01-01")
    # Intentionally include transactions from different merchant
    wrong_merchant = sample_transactions

    result = calculate_merchant_pattern_consistency(
        target,
        sample_transactions,
        wrong_merchant
    )
    # Should only count the 2 coffee shop transactions, not the same amount at different merchant
    assert result == pytest.approx(0.4)









if __name__ == "__main__":
    unittest.main()


