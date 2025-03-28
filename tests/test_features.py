# test features
import re

import numpy as np
import pandas as pd
import pytest

from recur_scan.features import (
    get_amount_cv,
    get_days_between_std,
    get_ends_in_99,
    get_is_always_recurring,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
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


# Removed from here and moved to the top


def test_get_days_between_std():
    sample_transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-03"),
        Transaction(id=3, user_id="user1", name="name1", amount=100, date="2024-01-05"),
        Transaction(id=4, user_id="user1", name="name1", amount=100, date="2024-01-07"),
        Transaction(id=5, user_id="user1", name="name1", amount=100, date="2024-01-09"),
    ]
    all_transactions = sample_transactions  # Provide a suitable value for all_transactions
    results = [get_days_between_std(transaction, all_transactions) for transaction in sample_transactions]
    assert all(result is not None for result in results)  # Ensure it returns a value for each transaction


# Removed redundant import


def test_get_amount_cv():
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=150, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="name1", amount=175, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="name1", amount=225, date="2024-01-05"),
    ]
    result = get_amount_cv(transactions[0], transactions)
    assert result >= 0  # Ensure it returns a valid coefficient of variation


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


def get_is_convenience_store(transaction: Transaction) -> int:
    """Check if the transaction is at a convenience store using regex."""
    convenience_stores = (
        r"\b(7-eleven|cvs|walgreens|rite aid|circle k|quiktrip|speedway|ampm|"
        r"7 eleven|seven eleven|sheetz)\b"
    )
    return int(bool(re.search(convenience_stores, transaction.name, re.IGNORECASE)))


def get_day_of_month_consistency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate entropy of day-of-month distribution for this user_id and name (low = consistent)."""
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name]
    if not user_transactions:
        return 1.0
    days = [int(t.date.split("-")[2]) for t in user_transactions]
    value_counts = pd.Series(days).value_counts(normalize=True)
    entropy = -sum(p * np.log2(p + 1e-10) for p in value_counts)
    return float(entropy / np.log2(31))


def get_exact_amount_count(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Count transactions with the exact same amount for this user_id and name."""
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name]
    return sum(1 for t in user_transactions if t.amount == transaction.amount)


def get_has_recurring_keyword(transaction: Transaction) -> int:
    """Check if the transaction name contains recurring-related keywords using regex."""
    recurring_keywords = (
        r"\b(sub|membership|renewal|monthly|annual|premium|bill|plan|fee|auto|pay|"
        r"service|recurring|subscription|auto-renew|recurr|autopay|rec|month|year|"
        r"quarterly|weekly|due)\b"
    )
    return int(bool(re.search(recurring_keywords, transaction.name, re.IGNORECASE)))
