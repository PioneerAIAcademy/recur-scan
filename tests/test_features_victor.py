from recur_scan.features_victor import (
    get_avg_days_between,
)
from recur_scan.transactions import Transaction


def test_get_avg_days_between():
    transactions = [
        Transaction(id=1, user_id="1", name="vendor", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="1", name="vendor", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="1", name="vendor", amount=100, date="2024-01-03"),
    ]
    assert get_avg_days_between(transactions) == 1.0
