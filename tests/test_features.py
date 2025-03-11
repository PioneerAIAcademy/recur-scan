import pytest

from recur_scan.features import (
    amount_ends_in_00,
    amount_ends_in_99,
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
    """Fixture providing test transactions."""
    return [
        Transaction(id=1, user_id="user1", name="AT&T", amount=50.99, date="2023-01-01"),
        Transaction(id=2, user_id="user1", name="Google Play", amount=30.00, date="2023-01-15"),
        Transaction(id=3, user_id="user1", name="AT&T", amount=50.99, date="2023-02-01"),
        Transaction(id=4, user_id="user1", name="Amazon Prime", amount=20.00, date="2023-02-15"),
        Transaction(id=5, user_id="user1", name="AT&T", amount=50.99, date="2023-03-01"),
        Transaction(id=6, user_id="user1", name="Disney+", amount=9.99, date="2023-03-15"),
    ]


def test_get_n_transactions_same_amount(transactions) -> None:
    assert get_n_transactions_same_amount(transactions[0], transactions) == 3
    assert get_n_transactions_same_amount(transactions[1], transactions) == 1


def test_get_percent_transactions_same_amount(transactions) -> None:
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 3 / 6
    assert pytest.approx(get_percent_transactions_same_amount(transactions[1], transactions)) == 1 / 6


def test_amount_ends_in_99(transactions) -> None:
    assert amount_ends_in_99(transactions[0]) is True
    assert amount_ends_in_99(transactions[1]) is False


def test_amount_ends_in_00(transactions) -> None:
    assert amount_ends_in_00(transactions[1]) is True
    assert amount_ends_in_00(transactions[0]) is False


def test_is_recurring_merchant(transactions) -> None:
    assert is_recurring_merchant(transactions[0]) is True
    assert is_recurring_merchant(transactions[1]) is True
    assert is_recurring_merchant(transactions[3]) is True
    assert is_recurring_merchant(transactions[5]) is True


def test_get_n_transactions_same_merchant_amount(transactions) -> None:
    assert get_n_transactions_same_merchant_amount(transactions[0], transactions) == 3
    assert get_n_transactions_same_merchant_amount(transactions[1], transactions) == 1


def test_get_percent_transactions_same_merchant_amount(transactions) -> None:
    assert pytest.approx(get_percent_transactions_same_merchant_amount(transactions[0], transactions)) == 3 / 6
    assert pytest.approx(get_percent_transactions_same_merchant_amount(transactions[1], transactions)) == 1 / 6


def test_get_avg_days_between_same_merchant_amount(transactions) -> None:
    assert pytest.approx(get_avg_days_between_same_merchant_amount(transactions[0], transactions)) == 30.0


def test_get_stddev_days_between_same_merchant_amount(transactions) -> None:
    assert pytest.approx(get_stddev_days_between_same_merchant_amount(transactions[0], transactions)) == 0.0


def test_get_days_since_last_same_merchant_amount(transactions) -> None:
    assert get_days_since_last_same_merchant_amount(transactions[2], transactions) == 31


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
    assert features["days_since_last_same_merchant_amount"] == 31

    def test_get_n_transactions_same_amount(transactions) -> None:
        assert get_n_transactions_same_amount(transactions[0], transactions) == 3
        assert get_n_transactions_same_amount(transactions[1], transactions) == 1

    def test_get_percent_transactions_same_amount(transactions) -> None:
        assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 3 / 6
        assert pytest.approx(get_percent_transactions_same_amount(transactions[1], transactions)) == 1 / 6

    def test_amount_ends_in_99(transactions) -> None:
        assert amount_ends_in_99(transactions[0]) is True
        assert amount_ends_in_99(transactions[1]) is False

    def test_amount_ends_in_00(transactions) -> None:
        assert amount_ends_in_00(transactions[1]) is True
        assert amount_ends_in_00(transactions[0]) is False

    def test_is_recurring_merchant(transactions) -> None:
        assert is_recurring_merchant(transactions[0]) is True
        assert is_recurring_merchant(transactions[1]) is True
        assert is_recurring_merchant(transactions[3]) is True
        assert is_recurring_merchant(transactions[5]) is True

    def test_get_n_transactions_same_merchant_amount(transactions) -> None:
        assert get_n_transactions_same_merchant_amount(transactions[0], transactions) == 3
        assert get_n_transactions_same_merchant_amount(transactions[1], transactions) == 1

    def test_get_percent_transactions_same_merchant_amount(transactions) -> None:
        assert pytest.approx(get_percent_transactions_same_merchant_amount(transactions[0], transactions)) == 3 / 6
        assert pytest.approx(get_percent_transactions_same_merchant_amount(transactions[1], transactions)) == 1 / 6

    def test_get_avg_days_between_same_merchant_amount(transactions) -> None:
        assert pytest.approx(get_avg_days_between_same_merchant_amount(transactions[0], transactions)) == 30.0

    def test_get_stddev_days_between_same_merchant_amount(transactions) -> None:
        assert pytest.approx(get_stddev_days_between_same_merchant_amount(transactions[0], transactions)) == 0.0

    def test_get_days_since_last_same_merchant_amount(transactions) -> None:
        assert get_days_since_last_same_merchant_amount(transactions[2], transactions) == 31

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
        assert features["days_since_last_same_merchant_amount"] == 31
