from recur_scan.features import (
    get_average_transaction_amount,
    get_features,
    get_max_transaction_amount,
    get_min_transaction_amount,
    get_most_frequent_names,
    get_n_transactions_same_amount,
    get_percent_transactions_same_amount,
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
    assert features["average_transaction_amount"] == 133.33333333333334
    assert features["max_transaction_amount"] == 200.0
    assert features["min_transaction_amount"] == 100.0
    assert features["most_frequent_names"] == 0  # No recurring names in this test case


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
