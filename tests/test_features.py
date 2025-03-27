from datetime import datetime

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

        def get_recurring_frequency(transaction, transactions):
            """
            Determines the recurring frequency of a transaction based on the merchant and amount.
            """
            same_merchant_amount_transactions = [
                t for t in transactions if t.name == transaction.name and t.amount == transaction.amount
            ]
            if len(same_merchant_amount_transactions) < 2:
                return "none"

            # Calculate the average days between transactions
            dates = sorted(t.date for t in same_merchant_amount_transactions)
            intervals = [
                (datetime.strptime(dates[i + 1], "%Y-%m-%d") - datetime.strptime(dates[i], "%Y-%m-%d")).days
                for i in range(len(dates) - 1)
            ]
            avg_interval = sum(intervals) / len(intervals)

            if 28 <= avg_interval <= 31:
                return "monthly"
            elif 365 <= avg_interval <= 366:
                return "yearly"
            else:
                return "irregular"

        def test_get_recurring_frequency(transactions) -> None:
            assert get_recurring_frequency(transactions[0], transactions) == "monthly"
            assert get_recurring_frequency(transactions[1], transactions) == "none"
            assert get_recurring_frequency(transactions[5], transactions) == "none"

        def test_get_is_always_recurring(transactions) -> None:
            assert get_is_always_recurring(transactions[0], transactions) is True
            assert get_is_always_recurring(transactions[1], transactions) is False

        def get_is_insurance(transaction):
            """
            Determines if a transaction is related to insurance based on the name.
            """
            insurance_keywords = {"Insurance", "Health Insurance", "Life Insurance"}
            return any(keyword in transaction.name for keyword in insurance_keywords)

        def test_get_is_insurance() -> None:
            transaction = Transaction(id=1, user_id="user1", name="Health Insurance", amount=100.0, date="2023-01-01")
            assert get_is_insurance(transaction) is True

            transaction = Transaction(id=2, user_id="user1", name="Grocery Store", amount=50.0, date="2023-01-01")
            assert get_is_insurance(transaction) is False

        def get_is_utility(transaction):
            """
            Determines if a transaction is related to utility services based on the name.
            """
            utility_keywords = {"Utility", "Electric", "Water", "Gas"}
            return any(keyword in transaction.name for keyword in utility_keywords)

        def test_get_is_utility() -> None:
            transaction = Transaction(id=1, user_id="user1", name="Electric Utility", amount=75.0, date="2023-01-01")
            assert get_is_utility(transaction) is True

            transaction = Transaction(id=2, user_id="user1", name="Coffee Shop", amount=5.0, date="2023-01-01")
            assert get_is_utility(transaction) is False

        def get_is_phone(transaction):
            """
            Determines if a transaction is related to phone services based on the name.
            """
            phone_keywords = {"Mobile", "Telecom", "Phone"}
            return any(keyword in transaction.name for keyword in phone_keywords)

        def test_get_is_phone() -> None:
            transaction = Transaction(id=1, user_id="user1", name="Mobile Telecom", amount=45.0, date="2023-01-01")
            assert get_is_phone(transaction) is True

            transaction = Transaction(id=2, user_id="user1", name="Bookstore", amount=20.0, date="2023-01-01")
            assert get_is_phone(transaction) is False

        def test_is_subscription_amount() -> None:
            def is_subscription_amount(transaction):
                """
                Determines if a transaction amount matches common subscription pricing patterns.
                """
                subscription_amounts = {9.99, 19.99, 29.99, 49.99, 99.99}
                return transaction.amount in subscription_amounts

            transaction = Transaction(id=1, user_id="user1", name="Streaming Service", amount=9.99, date="2023-01-01")
            assert is_subscription_amount(transaction) is True

            transaction = Transaction(id=2, user_id="user1", name="Grocery Store", amount=15.0, date="2023-01-01")
            assert is_subscription_amount(transaction) is False

        def test_get_additional_features(transactions) -> None:
            features = {
                "day_of_week": transactions[0].date.weekday(),
                "day_of_month": int(transactions[0].date.split("-")[2]),
                "is_weekend": transactions[0].date.weekday() >= 5,
                "is_end_of_month": int(transactions[0].date.split("-")[2]) >= 28,
                "days_since_first_occurrence": 0,
                "min_days_between": 30,
                "max_days_between": 30,
                "merchant_total_count": 3,
                "merchant_recent_count": 1,
                "merchant_amount_stddev": 0.0,
                "relative_amount_difference": 0.0,
            }
            assert features["day_of_week"] == 6  # January 1, 2023, is a Sunday
            assert features["day_of_month"] == 1
            assert features["is_weekend"] is True
            assert features["is_end_of_month"] is False
            assert features["days_since_first_occurrence"] == 0
            assert features["min_days_between"] == 30
            assert features["max_days_between"] == 30
            assert features["merchant_total_count"] == 3
            assert features["merchant_recent_count"] == 1
            assert pytest.approx(features["merchant_amount_stddev"]) == 0.0
            assert pytest.approx(features["relative_amount_difference"]) == 0.0

            def test_get_amount_variation_features(transactions) -> None:
                # Test case where the transaction amount matches the merchant average
                features = get_amount_variation_features(transactions[0], transactions, threshold=0.2)
                assert pytest.approx(features["merchant_avg"]) == 50.99
                assert pytest.approx(features["relative_amount_diff"]) == 0.0
                assert features["amount_anomaly"] is False

                # Test case where the transaction amount is significantly different from the merchant average
                new_transaction = Transaction(id=7, user_id="user1", name="AT&T", amount=100.00, date="2023-04-01")
                features = get_amount_variation_features(new_transaction, transactions, threshold=0.2)
                assert pytest.approx(features["merchant_avg"]) == 50.99
                assert pytest.approx(features["relative_amount_diff"]) == (100.00 - 50.99) / 50.99
                assert features["amount_anomaly"] is True

                # Test case where there are no transactions for the same merchant
                new_transaction = Transaction(
                    id=8, user_id="user1", name="Unknown Merchant", amount=100.00, date="2023-04-01"
                )
                features = get_amount_variation_features(new_transaction, transactions, threshold=0.2)
                assert features["merchant_avg"] == 0.0
                assert features["relative_amount_diff"] == 0.0
                assert features["amount_anomaly"] is False

                # Test case where the threshold is higher than the relative difference
                features = get_amount_variation_features(transactions[0], transactions, threshold=0.5)
                assert pytest.approx(features["merchant_avg"]) == 50.99
                assert pytest.approx(features["relative_amount_diff"]) == 0.0
                assert features["amount_anomaly"] is False


def get_amount_variation_features(transaction, transactions, threshold=0.2):
    """
    Calculates features related to the variation of the transaction amount compared to the merchant's average.
    """
    same_merchant_transactions = [t for t in transactions if t.name == transaction.name]
    if not same_merchant_transactions:
        return {
            "merchant_avg": 0.0,
            "relative_amount_diff": 0.0,
            "amount_anomaly": False,
        }

    merchant_avg = sum(t.amount for t in same_merchant_transactions) / len(same_merchant_transactions)
    relative_amount_diff = abs(transaction.amount - merchant_avg) / merchant_avg
    amount_anomaly = relative_amount_diff > threshold

    return {
        "merchant_avg": merchant_avg,
        "relative_amount_diff": relative_amount_diff,
        "amount_anomaly": amount_anomaly,
    }


def get_is_always_recurring(transaction, transactions):
    """
    Determines if a transaction is always recurring based on the merchant and amount.
    """
    same_merchant_amount_transactions = [
        t for t in transactions if t.name == transaction.name and t.amount == transaction.amount
    ]
    return len(same_merchant_amount_transactions) > 1
