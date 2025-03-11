from recur_scan.features import (
    amount_ends_in_00,
    amount_ends_in_99,
    get_average_transaction_amount,
    get_features,
    get_max_transaction_amount,
    get_min_transaction_amount,
    get_most_frequent_names,
    get_n_transactions_same_amount,
    get_percent_transactions_same_amount,
    is_recurring_merchant,
)
from recur_scan.transactions import Transaction


def test_get_n_transactions_same_amount():
    transactions = [
        Transaction(id=1, user_id="user1", name="VendorA", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="VendorB", date="2023-01-02", amount=100.0),
        Transaction(id=3, user_id="user2", name="VendorA", date="2023-01-03", amount=200.0),
    ]
    transaction = transactions[0]
    assert get_n_transactions_same_amount(transaction, transactions) == 2


def test_get_percent_transactions_same_amount():
    transactions = [
        Transaction(id=1, user_id="user1", name="VendorA", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="VendorB", date="2023-01-02", amount=100.0),
        Transaction(id=3, user_id="user2", name="VendorA", date="2023-01-03", amount=200.0),
    ]
    transaction = transactions[0]
    assert get_percent_transactions_same_amount(transaction, transactions) == 2 / 3


def test_get_features():
    transactions = [
        Transaction(id=1, user_id="user1", name="VendorA", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="VendorB", date="2023-01-02", amount=100.0),
        Transaction(id=3, user_id="user2", name="VendorA", date="2023-01-03", amount=200.0),
    ]
    transaction = transactions[0]
    features = get_features(transaction, transactions)
    assert features["n_transactions_same_amount"] == 2
    assert features["percent_transactions_same_amount"] == 2 / 3
    assert not features["amount_ends_in_99"]
    assert features["amount_ends_in_00"]
    assert not features["is_recurring_merchant"]
    assert features["n_transactions_same_merchant_amount"] == 1
    assert features["percent_transactions_same_merchant_amount"] == 1 / 3
    assert features["avg_days_between_same_merchant_amount"] == 0.0
    assert features["stddev_days_between_same_merchant_amount"] == 0.0
    assert features["days_since_last_same_merchant_amount"] == 0
    assert round(features["average_transaction_amount"], 2) == 133.33
    assert features["max_transaction_amount"] == 200.0
    assert features["min_transaction_amount"] == 100.0
    assert features["most_frequent_names"] == 0
    assert not features["is_recurring"]


def test_get_most_frequent_names():
    transactions = [
        Transaction(id=1, user_id="user1", name="VendorA", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="VendorA", date="2023-01-02", amount=100.0),
        Transaction(id=3, user_id="user2", name="VendorB", date="2023-01-03", amount=200.0),
        Transaction(id=4, user_id="user2", name="VendorB", date="2023-01-04", amount=200.0),
        Transaction(id=5, user_id="user2", name="VendorC", date="2023-01-05", amount=300.0),
    ]
    assert set(get_most_frequent_names(transactions)) == {"VendorA", "VendorB"}


def test_get_average_transaction_amount():
    transactions = [
        Transaction(id=1, user_id="user1", name="VendorA", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="VendorB", date="2023-01-02", amount=200.0),
        Transaction(id=3, user_id="user2", name="VendorA", date="2023-01-03", amount=300.0),
    ]
    assert get_average_transaction_amount(transactions) == 200.0


def test_get_max_transaction_amount():
    transactions = [
        Transaction(id=1, user_id="user1", name="VendorA", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="VendorB", date="2023-01-02", amount=200.0),
        Transaction(id=3, user_id="user2", name="VendorA", date="2023-01-03", amount=300.0),
    ]
    assert get_max_transaction_amount(transactions) == 300.0


def test_get_min_transaction_amount():
    transactions = [
        Transaction(id=1, user_id="user1", name="VendorA", date="2023-01-01", amount=100.0),
        Transaction(id=2, user_id="user1", name="VendorB", date="2023-01-02", amount=200.0),
        Transaction(id=3, user_id="user2", name="VendorA", date="2023-01-03", amount=300.0),
    ]
    assert get_min_transaction_amount(transactions) == 100.0


def test_amount_ends_in_99():
    transaction = Transaction(id=1, user_id="user1", name="VendorA", date="2023-01-01", amount=9.99)
    assert amount_ends_in_99(transaction)
    transaction = Transaction(id=2, user_id="user1", name="VendorB", date="2023-01-02", amount=10.00)
    assert not amount_ends_in_99(transaction)


def test_amount_ends_in_00():
    transaction = Transaction(id=1, user_id="user1", name="VendorA", date="2023-01-01", amount=10.00)
    assert amount_ends_in_00(transaction)
    transaction = Transaction(id=2, user_id="user1", name="VendorB", date="2023-01-02", amount=9.99)
    assert not amount_ends_in_00(transaction)


def test_is_recurring_merchant():
    transaction = Transaction(id=1, user_id="user1", name="Google Play", date="2023-01-01", amount=10.00)
    assert is_recurring_merchant(transaction)
    transaction = Transaction(id=2, user_id="user1", name="Local Store", date="2023-01-02", amount=9.99)
    assert not is_recurring_merchant(transaction)
