# test features
import pytest

from recur_scan.features_nnanna import (
    get_average_transaction_amount,
    get_coefficient_of_variation,
    get_dispersion_transaction_amount,
    get_mad_transaction_amount,
    get_mobile_transaction,
    get_time_interval_between_transactions,
    get_transaction_frequency,
    get_transaction_interval_consistency,
)
from recur_scan.transactions import Transaction


def test_get_time_interval_between_transactions() -> None:
    """
    Test that get_time_interval_between_transactions returns the correct average time interval between
    transactions with the same amount.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="T-Mobile", amount=50, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="AT&T", amount=60, date="2024-01-05"),
        Transaction(id=6, user_id="user1", name="Verizon", amount=70, date="2024-01-06"),
        Transaction(id=7, user_id="user1", name="vendor1", amount=100, date="2024-01-26"),
        Transaction(id=8, user_id="user1", name="vendor2", amount=100.99, date="2024-01-07"),
        Transaction(id=9, user_id="user1", name="vendor2", amount=100.99, date="2024-01-14"),
        Transaction(id=10, user_id="user1", name="vendor2", amount=100.99, date="2024-01-21"),
        Transaction(id=11, user_id="user1", name="Sony Playstation", amount=500, date="2024-01-15"),
    ]
    assert get_time_interval_between_transactions(transactions[0], transactions) == 12.5
    assert get_time_interval_between_transactions(transactions[2], transactions) == 365.0


def test_get_mobile_transaction() -> None:
    """
    Test that get_mobile_transaction returns True for mobile company transactions and False otherwise.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="T-Mobile", amount=50, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="AT&T", amount=60, date="2024-01-05"),
        Transaction(id=6, user_id="user1", name="Verizon", amount=70, date="2024-01-06"),
        Transaction(id=7, user_id="user1", name="vendor1", amount=100, date="2024-01-26"),
        Transaction(id=8, user_id="user1", name="vendor2", amount=100.99, date="2024-01-07"),
        Transaction(id=9, user_id="user1", name="vendor2", amount=100.99, date="2024-01-14"),
        Transaction(id=10, user_id="user1", name="vendor2", amount=100.99, date="2024-01-21"),
        Transaction(id=11, user_id="user1", name="Sony Playstation", amount=500, date="2024-01-15"),
    ]
    assert get_mobile_transaction(transactions[3]) is True  # T-Mobile
    assert get_mobile_transaction(transactions[4]) is True  # AT&T
    assert get_mobile_transaction(transactions[5]) is True  # Verizon
    assert get_mobile_transaction(transactions[0]) is False  # vendor1


def test_get_transaction_frequency() -> None:
    """Test get_transaction_frequency."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03"),
    ]
    assert get_transaction_frequency(transactions[0], transactions) == 0.0
    assert (
        get_transaction_frequency(
            Transaction(id=12, user_id="user1", name="vendor3", amount=99.99, date="2024-01-08"), transactions
        )
        == 0.0
    )


def test_get_dispersion_transaction_amount() -> None:
    """Test get_dispersion_transaction_amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03"),
    ]
    assert (
        get_dispersion_transaction_amount(transactions[0], transactions) == 0.0
    )  # Replace with the correct expected value


def test_get_mad_transaction_amount() -> None:
    """Test get_mad_transaction_amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="vendor2", amount=60, date="2024-01-05"),
        Transaction(id=6, user_id="user1", name="vendor2", amount=70, date="2024-01-06"),
    ]
    # Test for vendor1
    assert pytest.approx(get_mad_transaction_amount(transactions[0], transactions)) == 50.0
    # Test for vendor2
    assert pytest.approx(get_mad_transaction_amount(transactions[3], transactions)) == 10.0
    # Test for a vendor with only one transaction
    assert (
        get_mad_transaction_amount(
            Transaction(id=7, user_id="user1", name="vendor3", amount=100, date="2024-01-07"), transactions
        )
        == 0.0
    )


def test_get_coefficient_of_variation() -> None:
    """Test get_coefficient_of_variation."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="vendor2", amount=60, date="2024-01-05"),
        Transaction(id=6, user_id="user1", name="vendor2", amount=70, date="2024-01-06"),
    ]
    # Test for vendor1
    assert pytest.approx(get_coefficient_of_variation(transactions[0], transactions), rel=1e-4) == 0.2721655269759087
    # Test for vendor2
    assert pytest.approx(get_coefficient_of_variation(transactions[3], transactions), rel=1e-4) == 0.13608276348795434
    # Test for a vendor with only one transaction
    assert (
        get_coefficient_of_variation(
            Transaction(id=7, user_id="user1", name="vendor3", amount=100, date="2024-01-07"), transactions
        )
        == 0.0
    )
    # Test for a vendor with mean = 0 (edge case)
    assert (
        get_coefficient_of_variation(
            Transaction(id=8, user_id="user1", name="vendor4", amount=0, date="2024-01-08"), transactions
        )
        == 0.0
    )
    # Test for a vendor with mean = 0 (edge case)
    assert (
        get_coefficient_of_variation(
            Transaction(id=8, user_id="user1", name="vendor4", amount=0, date="2024-01-08"), transactions
        )
        == 0.0
    )


def test_get_transaction_interval_consistency() -> None:
    """Test get_transaction_interval_consistency."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-15"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-30"),
        Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-01"),
        Transaction(id=5, user_id="user1", name="vendor2", amount=60, date="2024-01-10"),
        Transaction(id=6, user_id="user1", name="vendor2", amount=70, date="2024-01-20"),
    ]
    # Test for vendor1
    assert pytest.approx(get_transaction_interval_consistency(transactions[0], transactions), rel=1e-4) == 14.5

    # Test for vendor2
    assert pytest.approx(get_transaction_interval_consistency(transactions[3], transactions), rel=1e-4) == 9.5

    # Test for a vendor with only one transaction
    assert (
        get_transaction_interval_consistency(
            Transaction(id=7, user_id="user1", name="vendor3", amount=100, date="2024-01-01"), transactions
        )
        == 0.0
    )


def test_get_average_transaction_amount() -> None:
    """Test get_average_transaction_amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="vendor2", amount=60, date="2024-01-05"),
        Transaction(id=6, user_id="user1", name="vendor2", amount=70, date="2024-01-06"),
    ]
    # Test for vendor1
    assert pytest.approx(get_average_transaction_amount(transactions[0], transactions)) == 150.0
    # Test for vendor2
    assert pytest.approx(get_average_transaction_amount(transactions[3], transactions)) == 60.0
    # Test for a vendor with only one transaction
    assert (
        get_average_transaction_amount(
            Transaction(id=7, user_id="user1", name="vendor3", amount=100, date="2024-01-07"), transactions
        )
        == 0.0
    )
