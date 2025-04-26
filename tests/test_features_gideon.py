# test features

from recur_scan.features_gideon import is_microsoft_xbox_same_or_near_day
from recur_scan.transactions import Transaction


def test_is_microsoft_xbox_same_or_near_day():
    # Create sample transactions
    transactions = [
        Transaction(id=1, user_id="user", date="2023-01-01", amount=100.0, name="Microsoft Xbox"),
        Transaction(id=2, user_id="user", date="2023-01-02", amount=100.0, name="Microsoft Xbox"),
    ]

    # Test when transaction is on the same day
    assert is_microsoft_xbox_same_or_near_day(transactions[0], transactions)
