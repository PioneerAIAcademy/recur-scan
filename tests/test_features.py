import pytest

from recur_scan.features import (
    _get_day,
    amount_ends_in_00,
    amount_ends_in_99,
    get_additional_features,
    get_amount_variation_features,
    get_avg_days_between_same_merchant_amount,
    get_days_since_last_same_merchant_amount,
    get_ends_in_99,
    get_features,
    get_is_always_recurring,
    get_is_always_recurring_transaction,
    get_is_insurance,
    get_is_phone,
    get_is_phone_regex,
    get_is_utility,
    get_is_utility_regex,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_n_transactions_same_merchant_amount,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
    get_percent_transactions_same_merchant_amount,
    get_recurring_frequency,
    get_stddev_days_between_same_merchant_amount,
    is_insurance_related,
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


# ------------------ Tests for Basic Functions ------------------


def test_get_is_always_recurring():
    t1 = Transaction(id=1, user_id="user1", name="Netflix", amount=12.99, date="2023-01-01")
    t2 = Transaction(id=2, user_id="user1", name="Hulu", amount=11.99, date="2023-01-05")
    # According to the current implementation, both "netflix" and "hulu" are considered always recurring.
    assert get_is_always_recurring(t1) is True
    assert get_is_always_recurring(t2) is True


def test_get_is_insurance():
    t = Transaction(id=10, user_id="user1", name="Allstate Insurance", amount=100, date="2023-02-01")
    assert get_is_insurance(t) is True
    t2 = Transaction(id=11, user_id="user1", name="AT&T", amount=50.99, date="2023-02-01")
    assert get_is_insurance(t2) is False


def test_get_is_utility_regex():
    t = Transaction(id=12, user_id="user1", name="Electric Utility", amount=75.00, date="2023-02-10")
    assert get_is_utility_regex(t) is True
    t2 = Transaction(id=13, user_id="user1", name="Random Shop", amount=20.00, date="2023-02-10")
    assert get_is_utility_regex(t2) is False


def test_get_is_phone_regex():
    t = Transaction(id=14, user_id="user1", name="AT&T", amount=50.99, date="2023-03-01")
    t2 = Transaction(id=15, user_id="user1", name="T-Mobile", amount=40.00, date="2023-03-02")
    t3 = Transaction(id=16, user_id="user1", name="Verizon", amount=60.00, date="2023-03-03")
    for tx in (t, t2, t3):
        assert get_is_phone_regex(tx) is True
    t4 = Transaction(id=17, user_id="user1", name="Some Other Vendor", amount=10.00, date="2023-03-04")
    assert get_is_phone_regex(t4) is False


def test__get_day():
    assert _get_day("2024-05-17") == 17
    assert _get_day("2024-12-01") == 1


# ------------------ Tests for Temporal Functions ------------------


def test_get_n_transactions_days_apart(sample_transactions):
    t = sample_transactions[0]
    count = get_n_transactions_days_apart(t, sample_transactions, n_days_apart=30, n_days_off=2)
    assert isinstance(count, int)
    assert count >= 1


def test_get_pct_transactions_days_apart(sample_transactions):
    pct = get_pct_transactions_days_apart(sample_transactions[0], sample_transactions, n_days_apart=30, n_days_off=2)
    assert 0.0 <= pct <= 1.0


def test_get_n_transactions_same_day():
    t1 = Transaction(id=1, user_id="user1", name="Vendor", amount=100, date="2024-01-15")
    t2 = Transaction(id=2, user_id="user1", name="Vendor", amount=100, date="2024-01-15")
    t3 = Transaction(id=3, user_id="user1", name="Vendor", amount=50, date="2024-01-16")
    txs = [t1, t2, t3]
    assert get_n_transactions_same_day(t1, txs, n_days_off=0) == 2
    assert get_n_transactions_same_day(t3, txs, n_days_off=1) == 3


def test_get_pct_transactions_same_day():
    t1 = Transaction(id=1, user_id="user1", name="Vendor", amount=100, date="2024-01-15")
    t2 = Transaction(id=2, user_id="user1", name="Vendor", amount=100, date="2024-01-15")
    t3 = Transaction(id=3, user_id="user1", name="Vendor", amount=50, date="2024-01-16")
    txs = [t1, t2, t3]
    pct = get_pct_transactions_same_day(t1, txs, n_days_off=0)
    assert pytest.approx(pct) == 2 / 3


# ------------------ Tests for Amount Ending Functions ------------------


def test_get_ends_in_99():
    t1 = Transaction(id=1, user_id="user1", name="Vendor", amount=19.99, date="2024-01-01")
    t2 = Transaction(id=2, user_id="user1", name="Vendor", amount=20.00, date="2024-01-01")
    assert get_ends_in_99(t1) is True
    assert get_ends_in_99(t2) is False


def test_amount_ends_in_99_and_00():
    t1 = Transaction(id=3, user_id="user1", name="Vendor", amount=9.99, date="2024-01-02")
    t2 = Transaction(id=4, user_id="user1", name="Vendor", amount=15.00, date="2024-01-02")
    assert amount_ends_in_99(t1) is True
    assert amount_ends_in_00(t2) is True


# ------------------ Tests for Amount Frequency Functions ------------------


def test_get_n_transactions_same_amount():
    t1 = Transaction(id=1, user_id="user1", name="Vendor", amount=100, date="2024-01-01")
    t2 = Transaction(id=2, user_id="user1", name="Vendor", amount=100, date="2024-01-02")
    t3 = Transaction(id=3, user_id="user1", name="Vendor", amount=50, date="2024-01-03")
    txs = [t1, t2, t3]
    assert get_n_transactions_same_amount(t1, txs) == 2
    assert get_percent_transactions_same_amount(t3, txs) == 1 / 3


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
    assert freq == "monthly"


# ------------------ Tests for Miscellaneous Functions ------------------


def test_get_is_always_recurring_transaction():
    t1 = Transaction(id=1, user_id="user1", name="Spotify", amount=9.99, date="2023-01-01")
    t2 = Transaction(id=2, user_id="user1", name="Spotify", amount=9.99, date="2023-02-01")
    t3 = Transaction(id=3, user_id="user1", name="Coffee Shop", amount=5.00, date="2023-01-15")
    assert get_is_always_recurring_transaction(t1, [t1, t2, t3]) is True
    assert get_is_always_recurring_transaction(t3, [t1, t2, t3]) is False


def test_is_insurance_related():
    t = Transaction(id=4, user_id="user1", name="Policy Insurance", amount=100, date="2023-03-01")
    assert is_insurance_related(t) is True
    t2 = Transaction(id=5, user_id="user1", name="Grocery Store", amount=50, date="2023-03-01")
    assert is_insurance_related(t2) is False


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


def test_get_features():
    txs = [
        Transaction(id=20, user_id="user1", name="AT&T", amount=50.99, date="2023-01-01"),
        Transaction(id=21, user_id="user1", name="Netflix", amount=12.99, date="2023-01-05"),
        Transaction(id=22, user_id="user1", name="AT&T", amount=50.99, date="2023-01-31"),
    ]
    feats = get_features(txs[0], txs)
    expected_keys = {
        "amount",
        "amount_ends_in_99",
        "amount_ends_in_00",
        "is_recurring_merchant",
        "n_transactions_same_amount",
        "percent_transactions_same_amount",
    }
    for key in expected_keys:
        assert key in feats


# ------------------ Test for is_recurring_merchant ------------------


def test_is_recurring_merchant():
    # Test with a known recurring vendor
    t1 = Transaction(id=100, user_id="user1", name="AT&T", amount=50.99, date="2023-01-01")
    # Test with a vendor that should not be recognized as recurring.
    t2 = Transaction(id=101, user_id="user1", name="Local Cafe", amount=5.00, date="2023-01-02")
    assert is_recurring_merchant(t1) is True
    assert is_recurring_merchant(t2) is False
