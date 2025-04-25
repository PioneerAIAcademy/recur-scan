# test features
import datetime
from math import isclose

import pytest

from recur_scan.features_felix import (
    get_average_transaction_amount,
    get_day,
    get_dispersion_transaction_amount,
    get_is_always_recurring,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_max_transaction_amount,
    get_median_variation_transaction_amount,
    get_min_transaction_amount,
    get_month,
    get_n_transactions_same_vendor,
    get_transaction_intervals,
    get_transaction_rate,
    get_transactions_interval_stability,
    get_variation_ratio,
    get_year,
)
from recur_scan.transactions import Transaction


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


def test_get_n_transactions_same_vendor() -> None:
    """Test that get_n_transactions_same_vendor returns the correct number of transactions with the same vendor."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="vendor2", amount=300, date="2024-01-04"),
    ]
    assert get_n_transactions_same_vendor(transactions[0], transactions) == 3
    assert get_n_transactions_same_vendor(transactions[3], transactions) == 1


def test_get_max_transaction_amount() -> None:
    """
    Test that get_max_transaction_amount returns the correct maximum amount of all transactions.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="vendor2", date="2023-01-02", amount=200.0),
        Transaction(id=3, user_id="user2", name="vendor1", date="2023-01-03", amount=300.0),
    ]
    assert get_max_transaction_amount(transactions) == 300.0


def test_get_min_transaction_amount() -> None:
    """
    Test that get_min_transaction_amount returns the correct minimum amount of all transactions.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="vendor2", date="2023-01-02", amount=200.0),
        Transaction(id=3, user_id="user2", name="vendor1", date="2023-01-03", amount=300.0),
    ]
    assert get_min_transaction_amount(transactions) == 100.0


def test_get_transaction_intervals_single_transaction():
    """
    Test get_transaction_intervals with only one transaction.

    With a single transaction, there is no interval to compute so all features should be zero.
    """
    single_tx = [
        Transaction(
            id=1,
            user_id="user1",
            name="vendor1",
            amount=100,
            date=datetime.datetime.strptime("2024-01-02", "%Y-%m-%d").date(),
        )
    ]
    result = get_transaction_intervals(single_tx)
    expected = {
        "avg_days_between_transactions": 0.0,
        "std_dev_days_between_transactions": 0.0,
        "monthly_recurrence": 0,
        "same_weekday": 0,
        "same_amount": 0,
    }
    assert result == expected


def test_get_transaction_intervals_multiple_transactions() -> None:
    """
    Test get_transaction_intervals with multiple transactions.

    This test includes transactions with different dates, amounts, and weekdays.
    """
    transactions = [
        Transaction(
            id=1,
            user_id="user1",
            name="vendor1",
            amount=100,
            date=datetime.datetime.strptime("2024-01-02", "%Y-%m-%d").date(),
        ),
        Transaction(
            id=2,
            user_id="user1",
            name="vendor1",
            amount=100,
            date=datetime.datetime.strptime("2024-02-09", "%Y-%m-%d").date(),
        ),
        Transaction(
            id=3,
            user_id="user1",
            name="vendor1",
            amount=200,
            date=datetime.datetime.strptime("2024-03-03", "%Y-%m-%d").date(),
        ),
    ]
    result = get_transaction_intervals(transactions)
    expected = {
        "avg_days_between_transactions": 30.5,
        "std_dev_days_between_transactions": 10.6066,
        "monthly_recurrence": 1.0,
        "same_weekday": 0,
        "same_amount": 2 / 3,
    }
    assert isclose(result["avg_days_between_transactions"], expected["avg_days_between_transactions"], rel_tol=1e-5)
    assert isclose(
        result["std_dev_days_between_transactions"], expected["std_dev_days_between_transactions"], rel_tol=1e-3
    )
    assert result["monthly_recurrence"] == expected["monthly_recurrence"]
    assert result["same_weekday"] == expected["same_weekday"]
    assert result["same_amount"] == expected["same_amount"]


def test_get_month() -> None:
    """Test that get_month returns the correct month for the transaction date."""
    transaction = Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01")
    assert get_month(transaction) == 1


def test_get_day() -> None:
    """Test that get_day returns the correct day for the transaction date."""
    transaction = Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01")
    assert get_day(transaction) == 1


def test_get_year() -> None:
    """Test that get_year returns the correct year for the transaction date."""
    transaction = Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01")
    assert get_year(transaction) == 2024


def test_get_transaction_rate() -> None:
    """Test get_transaction_frequency."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03"),
    ]
    assert get_transaction_rate(transactions[0], transactions) == 0.0
    assert (
        get_transaction_rate(
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


def test_get_median_variation_transaction_amount() -> None:
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
    assert pytest.approx(get_median_variation_transaction_amount(transactions[0], transactions)) == 50.0
    # Test for vendor2
    assert pytest.approx(get_median_variation_transaction_amount(transactions[3], transactions)) == 10.0
    # Test for a vendor with only one transaction
    assert (
        get_median_variation_transaction_amount(
            Transaction(id=7, user_id="user1", name="vendor3", amount=100, date="2024-01-07"), transactions
        )
        == 0.0
    )


def test_get_variation_ratio() -> None:
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
    assert pytest.approx(get_variation_ratio(transactions[0], transactions), rel=1e-4) == 0.2721655269759087
    # Test for vendor2
    assert pytest.approx(get_variation_ratio(transactions[3], transactions), rel=1e-4) == 0.13608276348795434
    # Test for a vendor with only one transaction
    assert (
        get_variation_ratio(
            Transaction(id=7, user_id="user1", name="vendor3", amount=100, date="2024-01-07"), transactions
        )
        == 0.0
    )
    # Test for a vendor with mean = 0 (edge case)
    assert (
        get_variation_ratio(
            Transaction(id=8, user_id="user1", name="vendor4", amount=0, date="2024-01-08"), transactions
        )
        == 0.0
    )
    # Test for a vendor with mean = 0 (edge case)
    assert (
        get_variation_ratio(
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
    assert pytest.approx(get_transactions_interval_stability(transactions[0], transactions), rel=1e-4) == 14.5

    # Test for vendor2
    assert pytest.approx(get_transactions_interval_stability(transactions[3], transactions), rel=1e-4) == 9.5

    # Test for a vendor with only one transaction
    assert (
        get_transactions_interval_stability(
            Transaction(
                id=7, user_id="useget_transactions_interval_stabilityr1", name="vendor3", amount=100, date="2024-01-01"
            ),
            transactions,
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
