# test features
from math import isclose

import pytest

from recur_scan.features_felix import (
    get_average_transaction_amount,
    get_day,
    get_dispersion_transaction_amount,
    get_is_always_recurring,
    get_is_amazon_prime,
    get_is_att_transaction,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_likelihood_of_recurrence,
    get_max_transaction_amount,
    get_median_variation_transaction_amount,
    get_min_transaction_amount,
    get_month,
    get_n_transactions_same_vendor,
    get_transaction_intervals,
    get_transaction_rate,
    get_transaction_recency,
    get_transactions_interval_stability,
    get_variation_ratio,
    get_vendor_transaction_frequency,
    get_vendor_transaction_recurring,
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
            date="2024-01-02",  # Use string date directly
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
            date="2024-01-02",  # Tuesday
        ),
        Transaction(
            id=2,
            user_id="user1",
            name="vendor1",
            amount=100,
            date="2024-02-09",  # Friday
        ),
        Transaction(
            id=3,
            user_id="user1",
            name="vendor1",
            amount=200,
            date="2024-03-03",  # Sunday
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


# New tests for additional features


def test_get_is_amazon_prime() -> None:
    """Test get_is_amazon_prime with 4 transactions covering Amazon Prime and non-Prime cases."""
    test_transactions = [
        # True cases (Amazon Prime)
        Transaction(id=1, user_id="user1", name="Amazon Prime Membership", amount=12.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="AMAZON PRIME VIDEO", amount=8.99, date="2024-01-15"),
        # False cases
        Transaction(id=3, user_id="user1", name="Amazon Fresh Delivery", amount=35.99, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="Netflix Subscription", amount=14.99, date="2024-01-03"),
    ]

    assert get_is_amazon_prime(test_transactions[0]) is True
    assert get_is_amazon_prime(test_transactions[1]) is True
    assert get_is_amazon_prime(test_transactions[2]) is False
    assert get_is_amazon_prime(test_transactions[3]) is False


def test_get_vendor_transaction_frequency() -> None:
    """Test get_vendor_transaction_frequency with different transaction frequencies."""
    # Test case 1: Rare (1 transaction)
    transactions_rare = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
    ]
    assert get_vendor_transaction_frequency(transactions_rare[0], transactions_rare) == 0

    # Test case 2: Occasional (2 transactions)
    transactions_occasional = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=200, date="2024-01-02"),
    ]
    assert get_vendor_transaction_frequency(transactions_occasional[0], transactions_occasional) == 1

    # Test case 3: Frequent (4 transactions)
    transactions_frequent = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=200, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=300, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="vendor1", amount=400, date="2024-01-04"),
    ]
    assert get_vendor_transaction_frequency(transactions_frequent[0], transactions_frequent) == 2


def test_get_vendor_transaction_recurring() -> None:
    """Test get_vendor_transaction_recurring feature function."""

    transactions = [
        # Recurring transactions: Same user, name, amount, around the same day each month
        Transaction(id=1, user_id="user1", name="Spotify", amount=9.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Spotify", amount=9.99, date="2024-02-02"),
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-03-03"),
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-04-01"),
        # Different vendor
        Transaction(id=5, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        # Same vendor but varying amount
        Transaction(id=6, user_id="user1", name="Spotify", amount=12.99, date="2024-02-01"),
        # Same vendor and amount but one-off transaction outside pattern
        Transaction(id=7, user_id="user1", name="Spotify", amount=9.99, date="2023-08-15"),
    ]

    # True for recurring pattern
    assert get_vendor_transaction_recurring(transactions[0], transactions) == 1
    assert get_vendor_transaction_recurring(transactions[1], transactions) == 1
    assert get_vendor_transaction_recurring(transactions[3], transactions) == 1

    # False for different vendor
    assert get_vendor_transaction_recurring(transactions[4], transactions) == 0

    # False for different amount
    assert get_vendor_transaction_recurring(transactions[5], transactions) == 0

    # False for outlier one-off date
    assert get_vendor_transaction_recurring(transactions[6], transactions) == 0


def test_get_likelihood_of_recurrence() -> None:
    """Test get_likelihood_of_recurrence with different patterns of transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Spotify", amount=9.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-03-01"),
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-04-01"),
        Transaction(id=5, user_id="user1", name="Spotify", amount=9.99, date="2024-05-01"),
    ]
    # High likelihood of recurrence (consistent monthly pattern)
    assert pytest.approx(get_likelihood_of_recurrence(transactions[0], transactions, n=5)) == 1.0

    # Low likelihood of recurrence (inconsistent intervals)
    inconsistent_transactions = [
        Transaction(id=1, user_id="user1", name="Spotify", amount=9.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"),
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"),
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-03-20"),
        Transaction(id=5, user_id="user1", name="Spotify", amount=9.99, date="2024-04-01"),
    ]
    assert get_likelihood_of_recurrence(inconsistent_transactions[0], inconsistent_transactions, n=5) < 1.0

    # Not enough transactions to calculate recurrence
    assert get_likelihood_of_recurrence(transactions[0], transactions[:2], n=5) == 0.0


def test_get_transaction_recency() -> None:
    """Test get_transaction_recency with different transaction dates."""
    # Setup test transactions
    transactions = [
        Transaction(id=1, user_id="user1", name="Spotify", amount=9.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"),  # 31 days after Jan 1
        Transaction(
            id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-03-01"
        ),  # 29 days after Feb 1 (2024 is leap year)
    ]

    # Test 1: Days between Feb 1 and Mar 1 (29 days in 2024 due to leap year)
    assert get_transaction_recency(transactions[2], transactions) == 29

    # Test 2: Days between Jan 1 and Feb 1
    assert get_transaction_recency(transactions[1], transactions) == 31

    # Test 3: No previous transactions for the vendor
    assert (
        get_transaction_recency(
            Transaction(id=4, user_id="user1", name="Netflix", amount=15.99, date="2024-04-01"), transactions
        )
        == -1
    )


def test_get_is_att_transaction() -> None:
    """Test get_is_att_transaction with AT&T and non-AT&T transactions."""
    assert get_is_att_transaction(
        Transaction(id=1, user_id="user1", name="AT&T Wireless", amount=100, date="2024-01-01")
    )
    assert not get_is_att_transaction(
        Transaction(id=2, user_id="user1", name="Verizon Wireless", amount=100, date="2024-01-01")
    )
