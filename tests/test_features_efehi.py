# test features

from recur_scan.features_efehi import (
    get_irregular_periodicity,
    get_irregular_periodicity_with_tolerance,
    get_n_same_name_transactions,
    get_time_between_transactions,
    get_transaction_amount_stability,
    get_transaction_frequency,
    get_transaction_time_of_month,
    get_user_transaction_frequency,
    get_vendor_recurrence_consistency,
    get_vendor_recurring_ratio,
)
from recur_scan.transactions import Transaction


def test_get_transaction_time_of_month() -> None:
    """Test that get_transaction_time_of_month categorizes transactions correctly."""
    transaction_early = Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-05")
    transaction_mid = Transaction(id=2, user_id="user1", name="Test", amount=100, date="2024-01-15")
    transaction_late = Transaction(id=3, user_id="user1", name="Test", amount=100, date="2024-01-25")
    assert get_transaction_time_of_month(transaction_early) == 0
    assert get_transaction_time_of_month(transaction_mid) == 1
    assert get_transaction_time_of_month(transaction_late) == 2


def test_get_transaction_amount_stability() -> None:
    """Test that get_transaction_amount_stability calculates the standard deviation of transaction amounts."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Test", amount=200, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="Test", amount=300, date="2024-01-03"),
    ]
    assert get_transaction_amount_stability(transactions[0], transactions) > 0.0
    assert get_transaction_amount_stability(transactions[0], [transactions[0]]) == 0.0


def test_get_time_between_transactions() -> None:
    """Test that get_time_between_transactions calculates the average time gap between transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Test", amount=100, date="2024-01-05"),
        Transaction(id=3, user_id="user1", name="Test", amount=100, date="2024-01-10"),
    ]
    assert get_time_between_transactions(transactions[0], transactions) == 4.5
    assert get_time_between_transactions(transactions[0], [transactions[0]]) == 0.0


def test_get_transaction_frequency() -> None:
    """Test that get_transaction_frequency calculates average frequency correctly."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Allstate Insurance", date="2024-01-01", amount=100),
        Transaction(id=2, user_id="user1", name="Allstate Insurance", date="2024-01-02", amount=100),
        Transaction(id=3, user_id="user1", name="AT&T", date="2024-01-01", amount=200),
        Transaction(id=4, user_id="user1", name="Duke Energy", date="2024-01-02", amount=150),
        Transaction(id=5, user_id="user1", name="HighEnergy Soft Drinks", date="2024-01-03", amount=2.99),
    ]
    transaction = transactions[0]
    result = get_transaction_frequency(transaction, transactions)
    assert result > 0


def test_get_n_same_name_transactions() -> None:
    """Test that get_n_same_name_transactions correctly counts transactions with the same name."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Allstate Insurance", date="2024-01-01", amount=100),
        Transaction(id=2, user_id="user1", name="AT&T", date="2024-01-01", amount=200),
        Transaction(id=3, user_id="user1", name="Duke Energy", date="2024-01-02", amount=150),
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", date="2024-01-03", amount=2.99),
    ]
    assert get_n_same_name_transactions(transactions[0], transactions) == 1  # "Allstate Insurance" appears once
    assert get_n_same_name_transactions(transactions[1], transactions) == 1  # "AT&T" appears once
    # Add a duplicate transaction to test multiple occurrences
    transactions.append(Transaction(id=5, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-04"))
    assert get_n_same_name_transactions(transactions[0], transactions) == 2  # "Allstate Insurance" now appears twice


def test_get_irregular_periodicity() -> None:
    """Test that get_irregular_periodicity calculates the standard deviation of time gaps correctly."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Test", amount=100, date="2024-03-01"),
        Transaction(id=3, user_id="user1", name="Test", amount=100, date="2024-06-01"),
    ]
    assert get_irregular_periodicity(transactions[0], transactions) > 0.0
    assert get_irregular_periodicity(transactions[0], [transactions[0]]) == 0.0


def test_get_irregular_periodicity_with_tolerance() -> None:
    """Test that get_irregular_periodicity_with_tolerance calculates the standard deviation with tolerance."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Test", amount=100, date="2024-01-10"),
        Transaction(id=3, user_id="user1", name="Test", amount=100, date="2024-01-20"),
        Transaction(id=4, user_id="user1", name="Test", amount=100, date="2024-02-01"),
    ]
    result = get_irregular_periodicity_with_tolerance(transactions[0], transactions, tolerance=5)
    assert result > 0.0  # Ensure the result is greater than 0
    assert result < 0.4  # Ensure the result is within the expected range


def test_get_user_transaction_frequency() -> None:
    """Test that get_user_transaction_frequency calculates the average frequency of user transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Test", amount=100, date="2024-01-10"),
        Transaction(id=3, user_id="user1", name="Test", amount=100, date="2024-01-20"),
        Transaction(id=4, user_id="user1", name="Test", amount=100, date="2024-02-01"),
    ]
    assert get_user_transaction_frequency("user1", transactions) == 10.333333333333334  # Update expected value
    assert get_user_transaction_frequency("user2", transactions) == 0.0


def test_get_vendor_recurring_ratio() -> None:
    """Test that get_vendor_recurring_ratio calculates the correct ratio of recurring transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Test", amount=100, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Test", amount=200, date="2024-03-01"),
    ]
    assert get_vendor_recurring_ratio(transactions[0], transactions) == 2 / 3
    assert get_vendor_recurring_ratio(transactions[2], transactions) == 1 / 3
    assert get_vendor_recurring_ratio(transactions[0], []) == 0.0


def test_get_vendor_recurrence_consistency() -> None:
    """Test that get_vendor_recurrence_consistency calculates the correct percentage of consistent intervals."""
    transactions = [
        Transaction(id=1, user_id="user1", name="VendorA", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="VendorA", amount=100, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="VendorA", amount=100, date="2024-03-01"),
        Transaction(id=4, user_id="user1", name="VendorA", amount=100, date="2024-05-01"),
    ]
    result = get_vendor_recurrence_consistency(transactions[0], transactions)
    assert 0.5 < result < 0.8  # Adjusted to match expected behavior
