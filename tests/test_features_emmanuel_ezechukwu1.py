# test features
import pytest

from recur_scan.features_emmanuel_ezechukwu1 import (
    get_amount_cv,
    get_day_of_month_consistency,
    get_days_between_std,
    get_exact_amount_count,
    get_has_recurring_keyword,
    get_is_always_recurring,
    get_is_convenience_store,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_pct_transactions_days_apart,
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


def test_get_n_transactions_days_apart() -> None:
    """Test get_n_transactions_days_apart."""
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


def test_get_pct_transactions_days_apart() -> None:
    """Test get_pct_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=5, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=6, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=7, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
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


def test_get_day_of_month_consistency() -> None:
    """Test get_day_of_month_consistency."""
    # Case 1: All transactions on the same day of the month (low entropy)
    transactions_same_day = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=100, date="2024-03-01"),
    ]
    result_same_day = get_day_of_month_consistency(transactions_same_day[0], transactions_same_day)
    assert result_same_day == pytest.approx(0.0, abs=1e-5)  # Should be very close to 0

    # Case 2: Transactions on different days (higher entropy)
    transactions_diff_days = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-02-15"),
        Transaction(id=3, user_id="user1", name="name1", amount=100, date="2024-03-30"),
    ]
    result_diff_days = get_day_of_month_consistency(transactions_diff_days[0], transactions_diff_days)
    assert result_diff_days == pytest.approx(0.20184908652385852, abs=1e-5)  # Expected entropy for 2 distinct days
    assert result_diff_days > result_same_day  # Ensure varied days have higher entropy

    # Case 3: No matching transactions (different user_id)
    transactions_no_match = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user2", name="name1", amount=100, date="2024-02-01"),
    ]
    result_no_match = get_day_of_month_consistency(transactions_no_match[0], transactions_no_match)
    assert result_no_match == 1.0  # Should return 1.0 when no matching transactions


def test_get_exact_amount_count() -> None:
    """Test get_exact_amount_count."""
    # Case 1: Multiple transactions with the same amount
    transactions_same_amount = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-03-01"),
    ]
    assert get_exact_amount_count(transactions_same_amount[0], transactions_same_amount) == 2

    # Case 2: No transactions with the same amount
    transactions_diff_amount = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=200, date="2024-02-01"),
    ]
    assert get_exact_amount_count(transactions_diff_amount[0], transactions_diff_amount) == 1

    # Case 3: No matching transactions (different user_id)
    transactions_no_match = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user2", name="name1", amount=100, date="2024-02-01"),
    ]
    assert get_exact_amount_count(transactions_no_match[0], transactions_no_match) == 1


def test_get_has_recurring_keyword() -> None:
    """Test get_has_recurring_keyword."""
    # Case 1: Transaction name contains a recurring keyword
    assert (
        get_has_recurring_keyword(
            Transaction(id=1, user_id="user1", name="Netflix Subscription", amount=100, date="2024-01-01")
        )
        == 1
    )

    # Case 2: Transaction name does not contain a recurring keyword
    assert (
        get_has_recurring_keyword(Transaction(id=2, user_id="user1", name="Walmart", amount=100, date="2024-01-01"))
        == 0
    )


def test_get_is_convenience_store() -> None:
    """Test get_is_convenience_store."""
    # Case 1: Transaction name is a convenience store
    assert (
        get_is_convenience_store(Transaction(id=1, user_id="user1", name="7-Eleven", amount=100, date="2024-01-01"))
        == 1
    )

    # Case 2: Transaction name is not a convenience store
    assert (
        get_is_convenience_store(Transaction(id=2, user_id="user1", name="Netflix", amount=100, date="2024-01-01")) == 0
    )