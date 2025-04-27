import os
import sys

# Add the parent directory of 'recur_scan' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from recur_scan.features_victor import (
    amount_cluster_count,
    amount_stability_index,
    get_avg_days_between,
    get_count_same_amount_monthly,
    get_days_since_last_same_amount,
    get_new_features,
    interval_variability,
    is_small_fixed_amount,
    merchant_recurrence_score,
    near_interval_ratio,
    recurring_day_of_month,
    sequence_length,
)
from recur_scan.transactions import Transaction


def test_get_avg_days_between():
    transactions = [
        Transaction(id=1, user_id="1", name="Apple", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="1", name="Apple", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="1", name="Apple", amount=100, date="2024-01-03"),
    ]
    assert get_avg_days_between(transactions) == 1.0


def test_interval_variability():
    transactions = [
        Transaction(id=1, user_id="1", name="Apple", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="1", name="Apple", amount=100, date="2024-01-31"),
        Transaction(id=3, user_id="1", name="Apple", amount=100, date="2024-03-02"),
    ]
    assert abs(interval_variability(transactions) - 0.7071) < 0.01  # Sample std dev of [30, 31]


def test_amount_cluster_count():
    transactions = [
        Transaction(id=1, user_id="1", name="Apple", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="1", name="Apple", amount=102, date="2024-01-02"),
        Transaction(id=3, user_id="1", name="Apple", amount=200, date="2024-01-03"),
    ]
    assert amount_cluster_count(transactions, tolerance=0.05) == 2  # Two clusters: [100, 102], [200]


def test_recurring_day_of_month():
    transactions = [
        Transaction(id=1, user_id="1", name="Apple", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="1", name="Apple", amount=100, date="2024-02-01"),
        Transaction(id=3, user_id="1", name="Apple", amount=100, date="2024-03-01"),
    ]
    assert recurring_day_of_month(transactions) == 1.0  # All on day 1


def test_near_interval_ratio():
    transactions = [
        Transaction(id=1, user_id="1", name="Apple", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="1", name="Apple", amount=100, date="2024-01-08"),
        Transaction(id=3, user_id="1", name="Apple", amount=100, date="2024-02-07"),
    ]
    assert abs(near_interval_ratio(transactions, tolerance=5) - 1.0) < 0.01  # Intervals [7, 30] near 7, 30 days


def test_amount_stability_index():
    transactions = [
        Transaction(id=1, user_id="1", name="Apple", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="1", name="Apple", amount=105, date="2024-01-02"),
        Transaction(id=3, user_id="1", name="Apple", amount=200, date="2024-01-03"),
    ]
    assert abs(amount_stability_index(transactions, tolerance=0.1) - 0.6667) < 0.01  # 2/3 within 10% of median (~102.5)


def test_merchant_recurrence_score():
    transactions = [
        Transaction(id=1, user_id="1", name="Apple", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="1", name="Apple", amount=100, date="2024-01-02"),
    ]
    merchant_scores = {"Apple": 0.75}
    assert merchant_recurrence_score(transactions, merchant_scores) == 0.75
    assert merchant_recurrence_score(transactions, {}) == 0.0


def test_sequence_length():
    transactions = [
        Transaction(id=1, user_id="1", name="Apple", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="1", name="Apple", amount=100, date="2024-01-02"),
    ]
    assert sequence_length(transactions) == 2


def test_get_count_same_amount_monthly():
    transactions = [
        Transaction(id=1, user_id="1", name="Apple", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="1", name="Apple", amount=2.99, date="2024-02-01"),  # 31 days
        Transaction(id=3, user_id="1", name="Apple", amount=2.99, date="2024-03-02"),  # 30 days
    ]
    current_transaction = Transaction(id=2, user_id="1", name="Apple", amount=2.99, date="2024-02-01")
    assert get_count_same_amount_monthly(transactions, current_transaction) == 2  # Matches id=1, id=3


def test_is_small_fixed_amount():
    transaction = Transaction(id=1, user_id="1", name="Apple", amount=2.99, date="2024-01-01")
    assert is_small_fixed_amount(transaction) == 1.0
    transaction = Transaction(id=2, user_id="1", name="Cleo", amount=50.00, date="2024-01-01")
    assert is_small_fixed_amount(transaction) == 0.0
    transaction = Transaction(id=3, user_id="1", name="Brigit", amount=5.00, date="2024-01-01")
    assert is_small_fixed_amount(transaction) == 1.0
    transaction = Transaction(id=4, user_id="1", name="Cleo AI", amount=7.50, date="2024-01-01")
    assert is_small_fixed_amount(transaction) == 0.0


def test_get_days_since_last_same_amount():
    transactions = [
        Transaction(id=1, user_id="1", name="Apple", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="1", name="Apple", amount=2.99, date="2024-02-01"),
        Transaction(id=3, user_id="1", name="Apple", amount=2.99, date="2024-03-02"),
    ]
    current_transaction = Transaction(id=3, user_id="1", name="Apple", amount=2.99, date="2024-03-02")
    assert get_days_since_last_same_amount(transactions, current_transaction) == 30  # Last was 2024-02-01
    current_transaction = Transaction(id=1, user_id="1", name="Brigit", amount=5.00, date="2024-01-01")
    assert get_days_since_last_same_amount(transactions, current_transaction) == 999.0  # No prior match


def test_get_new_features():
    transactions = [
        Transaction(id=1, user_id="1", name="Apple", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="1", name="Apple", amount=2.99, date="2024-01-31"),
        Transaction(id=3, user_id="1", name="Apple", amount=2.99, date="2024-03-02"),
    ]
    merchant_scores = {"Apple": 0.8}
    current_transaction = Transaction(id=2, user_id="1", name="Apple", amount=2.99, date="2024-01-31")
    features = get_new_features(transactions, merchant_scores, current_transaction=current_transaction)
    assert len(features) == 11
    assert features[0] == ("avg_days_between", 30.5)
    assert features[1][0] == "interval_variability"
    assert abs(features[1][1] - 0.7071) < 0.01  # Sample std dev of [30, 31]
    assert features[2] == ("amount_cluster_count", 1)
    assert features[3] == ("recurring_day_of_month", 1 / 3)
    assert features[4][0] == "near_interval_ratio"
    assert abs(features[4][1] - 1.0) < 0.01  # Intervals [30, 31] near 30 days
    assert features[5][0] == "amount_stability_index"
    assert abs(features[5][1] - 1.0) < 0.01  # All amounts identical
    assert features[6] == ("merchant_recurrence_score", 0.8)
    assert features[7] == ("sequence_length", 3)
    assert features[8][0] == "count_same_amount_monthly"
    assert features[8][1] == 2.0  # Matches id=1, id=3 (30, 31 days)
    assert features[9][0] == "is_small_fixed_amount"
    assert features[9][1] == 1.0  # 2.99 is small and ends in .99
    assert features[10][0] == "days_since_last_same_amount"
    assert features[10][1] == 30.0  # Last was 2024-01-01
