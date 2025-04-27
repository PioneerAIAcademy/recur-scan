import math

import pytest

from recur_scan.features_precious import (
    amount_ends_in_00,
    get_additional_features,
    get_amount_variation_features,
    get_avg_days_between_same_merchant_amount,
    get_days_since_last_same_merchant_amount,
    get_is_phone,
    get_is_utility,
    get_n_transactions_same_merchant_amount,
    get_new_features,
    get_percent_transactions_same_merchant_amount,
    get_recurring_frequency,
    get_stddev_days_between_same_merchant_amount,
    is_recurring_merchant,
    is_subscription_amount,
)
from recur_scan.transactions import Transaction

# ------------------ Fixtures ------------------


@pytest.fixture
def sample_transactions():
    """
    A list of transactions used for testing.
    """
    return [
        Transaction(id=1, user_id="user1", name="AT&T", amount=50.99, date="2023-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=12.99, date="2023-01-05"),
        Transaction(id=3, user_id="user1", name="AT&T", amount=50.99, date="2023-01-31"),
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2023-02-10"),
        Transaction(id=5, user_id="user1", name="AT&T", amount=50.99, date="2023-03-02"),
        Transaction(id=6, user_id="user1", name="Electric Co", amount=100.00, date="2023-03-15"),
    ]


@pytest.fixture
def recurring_transactions():
    """
    Transactions with the same merchant and amount (for AT&T) exactly 30 days apart.
    """
    return [
        Transaction(id=1, user_id="user1", name="AT&T", amount=50.99, date="2023-01-01"),
        Transaction(id=2, user_id="user1", name="AT&T", amount=50.99, date="2023-01-31"),
        Transaction(id=3, user_id="user1", name="AT&T", amount=50.99, date="2023-03-02"),
    ]


# ------------------ Tests for Miscellaneous Functions ------------------


def test_get_is_utility():
    t1 = Transaction(id=6, user_id="user1", name="Duke Energy", amount=100, date="2023-02-01")
    t2 = Transaction(id=7, user_id="user1", name="Coffee Shop", amount=5, date="2023-02-01")
    assert get_is_utility(t1) is True
    assert get_is_utility(t2) is False


def test_get_is_phone():
    t1 = Transaction(id=8, user_id="user1", name="AT&T", amount=50.99, date="2023-03-01")
    t2 = Transaction(id=9, user_id="user1", name="Verizon Wireless", amount=60, date="2023-03-02")
    t3 = Transaction(id=10, user_id="user1", name="Local Cafe", amount=5, date="2023-03-03")
    assert get_is_phone(t1) is True
    assert get_is_phone(t2) is True
    assert get_is_phone(t3) is False


# ------------------ Tests for Temporal Functions ------------------

# ------------------ Tests for Amount Ending Functions ------------------


def test_amount_ends_in_00():
    t2 = Transaction(id=4, user_id="user1", name="Vendor", amount=15.00, date="2024-01-02")
    assert amount_ends_in_00(t2) is True


# ------------------ Tests for Amount Frequency Functions ------------------


def test_get_n_transactions_same_merchant_amount():
    t1 = Transaction(id=1, user_id="user1", name="AT&T", amount=50.99, date="2023-01-01")
    t2 = Transaction(id=2, user_id="user1", name="AT&T", amount=50.99, date="2023-01-31")
    t3 = Transaction(id=3, user_id="user1", name="AT&T", amount=50.99, date="2023-03-02")
    t4 = Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2023-02-01")
    txs = [t1, t2, t3, t4]
    assert get_n_transactions_same_merchant_amount(t1, txs) == 3
    assert get_percent_transactions_same_merchant_amount(t4, txs) == 1 / 4


# ------------------ Tests for Time Interval Functions ------------------


def test_get_avg_stddev_days_between_same_merchant_amount(recurring_transactions):
    avg = get_avg_days_between_same_merchant_amount(recurring_transactions[1], recurring_transactions)
    stddev = get_stddev_days_between_same_merchant_amount(recurring_transactions[1], recurring_transactions)
    assert pytest.approx(avg) == 30.0
    assert pytest.approx(stddev) == 0.0


def test_get_days_since_last_same_merchant_amount(recurring_transactions):
    assert get_days_since_last_same_merchant_amount(recurring_transactions[1], recurring_transactions) == 30
    assert get_days_since_last_same_merchant_amount(recurring_transactions[2], recurring_transactions) == 30


def test_get_recurring_frequency():
    t1 = Transaction(id=1, user_id="user1", name="AT&T", amount=50.99, date="2023-01-01")
    t2 = Transaction(id=2, user_id="user1", name="AT&T", amount=50.99, date="2023-01-31")
    t3 = Transaction(id=3, user_id="user1", name="AT&T", amount=50.99, date="2023-03-02")
    freq = get_recurring_frequency(t1, [t1, t2, t3])
    assert freq == 3


# ------------------ Tests for Miscellaneous Functions ------------------


def test_is_subscription_amount():
    t1 = Transaction(id=11, user_id="user1", name="Vendor", amount=9.99, date="2023-04-01")
    t2 = Transaction(id=12, user_id="user1", name="Vendor", amount=5.00, date="2023-04-02")
    assert is_subscription_amount(t1) is True
    assert is_subscription_amount(t2) is False


def test_get_additional_features():
    t = Transaction(id=13, user_id="user1", name="Spotify", amount=9.99, date="2023-04-01")
    txs = [
        t,
        Transaction(id=14, user_id="user1", name="Spotify", amount=9.99, date="2023-04-15"),
        Transaction(id=15, user_id="user1", name="Spotify", amount=9.99, date="2023-05-01"),
    ]
    feats = get_additional_features(t, txs)
    for key in ["day_of_week", "day_of_month", "is_weekend", "merchant_total_count"]:
        assert key in feats


def test_get_amount_variation_features():
    txs = [
        Transaction(id=16, user_id="user1", name="AT&T", amount=50.99, date="2023-01-01"),
        Transaction(id=17, user_id="user1", name="AT&T", amount=50.99, date="2023-01-31"),
        Transaction(id=18, user_id="user1", name="AT&T", amount=50.99, date="2023-03-02"),
    ]
    features = get_amount_variation_features(txs[0], txs, threshold=0.2)
    assert pytest.approx(features["merchant_avg"]) == 50.99
    assert features["relative_amount_diff"] == 0.0
    assert features["amount_anomaly"] is False

    t_anomaly = Transaction(id=19, user_id="user1", name="AT&T", amount=100.0, date="2023-04-01")
    features_anomaly = get_amount_variation_features(t_anomaly, txs, threshold=0.2)
    expected_relative = abs(100.0 - 50.99) / 50.99
    assert pytest.approx(features_anomaly["relative_amount_diff"]) == expected_relative
    assert features_anomaly["amount_anomaly"] is True


# ------------------ Test for New_recurring_merchant Features------------------


def test_is_recurring_merchant():
    # Test with a known recurring vendor
    t1 = Transaction(id=100, user_id="user1", name="AT&T", amount=50.99, date="2023-01-01")
    # Test with a vendor that should not be recognized as recurring.
    t2 = Transaction(id=101, user_id="user1", name="Local Cafe", amount=5.00, date="2023-01-02")
    assert is_recurring_merchant(t1) is True
    assert is_recurring_merchant(t2) is False

    def test_get_new_features(sample_transactions):
        transaction = sample_transactions[0]  # Use the first transaction as the test case
        features = get_new_features(transaction, sample_transactions, threshold=0.2)

        # Core features
        assert features["amount"] == transaction.amount
        assert features["rolling_mean_amount"] == pytest.approx(50.99)  # Based on sample data
        assert features["day_of_week"] == 6  # January 1, 2023, is a Sunday
        assert features["day_of_month"] == 1
        assert features["month"] == 1
        assert features["days_since_last"] == 0  # No prior transactions with same user+merchant+amount
        assert features["recurring"] is False  # No recurring flag in sample data

        # Additional features
        assert features["merchant_avg"] == pytest.approx(50.99)  # Average for AT&T in sample data
        assert features["relative_amount_diff"] == 0.0  # No difference from average
        assert features["amount_anomaly"] is False  # No anomaly since diff is 0
        assert features["interval_variance_ratio"] == 0.0  # Only one interval, so no variance
        assert features["dom_consistency"] is True  # All transactions occur on the same day of the month
        assert features["seasonality_score"] == 1.0  # Perfect monthly seasonality
        assert features["amount_drift"] == 0.0  # No drift in amounts
        assert features["burstiness_ratio"] == 1.0  # All transactions are recent
        assert features["next_date_error"] == 0  # Perfect prediction for next date
        assert features["serial_autocorrelation"] == 0.0  # Only one interval, so no autocorrelation
        assert features["sin_doy"] == pytest.approx(math.sin(2 * math.pi * 1 / 365))  # Day 1 of the year
        assert features["cos_doy"] == pytest.approx(math.cos(2 * math.pi * 1 / 365))
        assert features["weekday_concentration"] == 1.0  # All transactions occur on the same weekday
        assert features["interval_consistency_ratio"] == 0  # No intervals to calculate consistency
        assert features["median_interval"] == 0.0  # No intervals
        assert features["mad_interval"] == 0.0  # No intervals
        assert features["robust_iqr_amount"] == 0.0  # Only one amount
        assert features["median_amount"] == pytest.approx(50.99)  # Median of one amount
        assert features["mad_amount"] == 0.0  # No deviation from median
