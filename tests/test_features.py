import pytest

from recur_scan.features import (
    amount_ends_in_00,
    amount_ends_in_99,
    get_amount_variation_features,  # Added import for the new function
    get_avg_days_between_same_merchant_amount,
    get_days_since_last_same_merchant_amount,
    get_features,
    get_n_transactions_same_amount,
    get_n_transactions_same_merchant_amount,
    get_percent_transactions_same_amount,
    get_percent_transactions_same_merchant_amount,
    get_stddev_days_between_same_merchant_amount,
    is_recurring_merchant,
)
from recur_scan.transactions import Transaction


@pytest.fixture
def transactions():
    """
    Fixture providing test transactions.
    Adjusted so that the AT&T transactions are exactly 30 days apart:
      - 2023-01-01
      - 2023-01-31 (30 days after January 1)
      - 2023-03-02 (30 days after January 31, given Feb 2023 has 28 days)
    """
    return [
        Transaction(id=1, user_id="user1", name="AT&T", amount=50.99, date="2023-01-01"),
        Transaction(id=2, user_id="user1", name="Google Play", amount=30.00, date="2023-01-15"),
        # AT&T transaction with a 30-day gap from January 1
        Transaction(id=3, user_id="user1", name="AT&T", amount=50.99, date="2023-01-31"),
        Transaction(id=4, user_id="user1", name="Amazon Prime", amount=20.00, date="2023-02-15"),
        # AT&T transaction with a 30-day gap from January 31
        Transaction(id=5, user_id="user1", name="AT&T", amount=50.99, date="2023-03-02"),
        Transaction(id=6, user_id="user1", name="Disney+", amount=9.99, date="2023-03-15"),
    ]


def test_get_n_transactions_same_amount(transactions) -> None:
    # For AT&T, there are three transactions with amount 50.99.
    assert get_n_transactions_same_amount(transactions[0], transactions) == 3
    # For Google Play (30.00), there is only one transaction.
    assert get_n_transactions_same_amount(transactions[1], transactions) == 1


def test_get_percent_transactions_same_amount(transactions) -> None:
    # AT&T: 3 out of 6 transactions have the same amount (50.99).
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 3 / 6
    # Google Play: 1 out of 6 transactions.
    assert pytest.approx(get_percent_transactions_same_amount(transactions[1], transactions)) == 1 / 6


def test_amount_ends_in_99(transactions) -> None:
    # 50.99 ends in .99
    assert amount_ends_in_99(transactions[0]) is True
    # 30.00 does not end in .99
    assert amount_ends_in_99(transactions[1]) is False


def test_amount_ends_in_00(transactions) -> None:
    # 30.00 ends in .00
    assert amount_ends_in_00(transactions[1]) is True
    # 50.99 does not end in .00
    assert amount_ends_in_00(transactions[0]) is False


def test_is_recurring_merchant(transactions) -> None:
    # Based on recurring keywords, these merchant names should be flagged as recurring.
    assert is_recurring_merchant(transactions[0]) is True
    assert is_recurring_merchant(transactions[1]) is True
    assert is_recurring_merchant(transactions[3]) is True
    assert is_recurring_merchant(transactions[5]) is True


def test_get_n_transactions_same_merchant_amount(transactions) -> None:
    # For AT&T with amount 50.99, there are three transactions.
    assert get_n_transactions_same_merchant_amount(transactions[0], transactions) == 3
    # For Google Play, there is only one.
    assert get_n_transactions_same_merchant_amount(transactions[1], transactions) == 1


def test_get_percent_transactions_same_merchant_amount(transactions) -> None:
    assert pytest.approx(get_percent_transactions_same_merchant_amount(transactions[0], transactions)) == 3 / 6
    assert pytest.approx(get_percent_transactions_same_merchant_amount(transactions[1], transactions)) == 1 / 6


def test_get_avg_days_between_same_merchant_amount(transactions) -> None:
    """
    For AT&T transactions with dates:
      - 2023-01-01
      - 2023-01-31  -> Difference: 30 days
      - 2023-03-02  -> Difference: 30 days
    Average = (30 + 30) / 2 = 30.0
    """
    assert pytest.approx(get_avg_days_between_same_merchant_amount(transactions[0], transactions)) == 30.0


def test_get_stddev_days_between_same_merchant_amount(transactions) -> None:
    """
    With two intervals of exactly 30 days, the standard deviation is 0.0.
    """
    assert pytest.approx(get_stddev_days_between_same_merchant_amount(transactions[0], transactions)) == 0.0


def test_get_days_since_last_same_merchant_amount(transactions) -> None:
    """
    For the third AT&T transaction (id=5, date "2023-03-02"), the previous AT&T is on "2023-01-31",
    which is exactly 30 days earlier.
    """
    assert get_days_since_last_same_merchant_amount(transactions[4], transactions) == 30


def test_get_features(transactions) -> None:
    features = get_features(transactions[0], transactions)
    assert features["amount"] == 50.99
    assert features["amount_ends_in_99"] is True
    assert features["amount_ends_in_00"] is False
    assert features["is_recurring_merchant"] is True
    assert features["n_transactions_same_amount"] == 3
    assert pytest.approx(features["percent_transactions_same_amount"]) == 3 / 6
    assert features["n_transactions_same_merchant_amount"] == 3
    assert pytest.approx(features["percent_transactions_same_merchant_amount"]) == 3 / 6
    assert pytest.approx(features["avg_days_between_same_merchant_amount"]) == 30.0
    assert pytest.approx(features["stddev_days_between_same_merchant_amount"]) == 0.0
    # For the first AT&T transaction, there is no previous transaction,
    # so days_since_last_same_merchant_amount should be 0.
    assert features["days_since_last_same_merchant_amount"] == 0


# ------------------ New Tests for get_amount_variation_features ------------------


def test_get_amount_variation_features_no_other_transactions() -> None:
    """
    When there are no transactions for the merchant, the function should return
    an average of 0.0, a relative difference of 0.0, and amount_anomaly as False.
    """
    transaction = Transaction(id=10, user_id="user2", name="Unique Merchant", amount=100.0, date="2023-04-01")
    features = get_amount_variation_features(transaction, [])
    assert features["merchant_avg"] == 0.0
    assert features["relative_amount_diff"] == 0.0
    assert features["amount_anomaly"] is False


def test_get_amount_variation_features_no_anomaly(transactions) -> None:
    """
    When the transaction amount equals the merchant's average, the relative difference
    should be 0.0 and no anomaly flagged.
    """
    # Use one of the existing AT&T transactions, which are all 50.99.
    transaction = transactions[0]
    features = get_amount_variation_features(transaction, transactions)
    assert pytest.approx(features["merchant_avg"]) == 50.99
    assert features["relative_amount_diff"] == 0.0
    assert features["amount_anomaly"] is False


def test_get_amount_variation_features_anomaly(transactions) -> None:
    """
    When the transaction amount significantly deviates from the merchant's average,
    the relative difference should exceed the threshold and amount_anomaly should be True.
    """
    # Create a new AT&T transaction with an amount different from the regular 50.99.
    new_transaction = Transaction(id=7, user_id="user1", name="AT&T", amount=100.0, date="2023-04-01")
    features = get_amount_variation_features(new_transaction, transactions, threshold=0.2)
    expected_avg = 50.99  # Average of AT&T transactions in the fixture.
    expected_relative = abs(100.0 - expected_avg) / expected_avg
    assert pytest.approx(features["merchant_avg"]) == expected_avg
    assert pytest.approx(features["relative_amount_diff"]) == expected_relative
    # Since the relative difference is much larger than 0.2, anomaly is flagged.
    assert features["amount_anomaly"] is True
