from recur_scan.features import (
    get_average_transaction_amount,
    get_avg_days_between_same_merchant_amount,
    get_ends_in_99,
    get_features,
    get_is_always_recurring,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_max_transaction_amount,
    get_min_transaction_amount,
    get_most_frequent_names,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
    is_recurring,
    is_recurring_merchant,
)
from recur_scan.transactions import Transaction

# Helper function to create transactions
def create_transaction(id, user_id, name, date, amount):
    return Transaction(id=id, user_id=user_id, name=name, date=date, amount=amount)


def test_get_n_transactions_same_amount() -> None:
    """Test that get_n_transactions_same_amount returns the correct number of transactions with the same amount."""
    transactions = [
        create_transaction(1, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(2, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(3, "user1", "name1", "2024-01-02", 200.0),
        create_transaction(4, "user1", "name1", "2024-01-03", 2.99),
    ]
    assert get_n_transactions_same_amount(transactions[0], transactions) == 2
    assert get_n_transactions_same_amount(transactions[2], transactions) == 1


def test_get_percent_transactions_same_amount() -> None:
    """Test that get_percent_transactions_same_amount returns correct percentage."""
    transactions = [
        create_transaction(1, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(2, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(3, "user1", "name1", "2024-01-02", 200.0),
        create_transaction(4, "user1", "name1", "2024-01-03", 2.99),
    ]
    assert get_percent_transactions_same_amount(transactions[0], transactions) == 0.5  # 2/4


def test_is_recurring_merchant() -> None:
    """Test that is_recurring_merchant returns True for recurring merchants."""
    transaction = create_transaction(1, "user1", "Google Play", "2023-01-01", 10.00)
    assert is_recurring_merchant(transaction)
    transaction = create_transaction(2, "user1", "Local Store", "2023-01-02", 9.99)
    assert not is_recurring_merchant(transaction)


def test_get_avg_days_between_same_merchant_amount() -> None:
    """Test get_avg_days_between_same_merchant_amount returns correct average days."""
    transactions = [
        create_transaction(1, "user1", "VendorA", "2023-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2023-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2023-01-15", 100.0),
    ]
    transaction = transactions[0]
    assert get_avg_days_between_same_merchant_amount(transaction, transactions) == 7.0


def test_get_features() -> None:
    """Test that get_features returns the correct features for a transaction."""
    transactions = [
        create_transaction(1, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(2, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(3, "user1", "name1", "2024-01-02", 200.0),
        create_transaction(4, "user1", "name1", "2024-01-03", 2.99),
    ]
    transaction = transactions[0]
    features = get_features(transaction, transactions)
    assert features["n_transactions_same_amount"] == 2
    assert features["percent_transactions_same_amount"] == 0.5  # 2/4
    assert not features["is_recurring_merchant"]
    assert features["avg_days_between_same_merchant_amount"] == 0.0
    assert round(features["average_transaction_amount"], 2) == 100.75
    assert features["max_transaction_amount"] == 200.0
    assert features["min_transaction_amount"] == 2.99
    assert features["most_frequent_names"] == 1  # name1 appears with multiple amounts
    assert not features["is_recurring"]


def test_get_is_always_recurring() -> None:
    """Test get_is_always_recurring identifies recurring vendors."""
    transaction = create_transaction(1, "user1", "Netflix", "2024-01-01", 15.99)
    assert get_is_always_recurring(transaction)
    transaction = create_transaction(2, "user1", "Local Store", "2024-01-02", 9.99)
    assert not get_is_always_recurring(transaction)


def test_get_is_insurance() -> None:
    """Test get_is_insurance identifies insurance payments."""
    transaction = create_transaction(1, "user1", "Geico Insurance", "2024-01-01", 150.0)
    assert get_is_insurance(transaction)
    transaction = create_transaction(2, "user1", "Grocery Store", "2024-01-02", 50.0)
    assert not get_is_insurance(transaction)


def test_get_is_utility() -> None:
    """Test get_is_utility identifies utility payments."""
    transaction = create_transaction(1, "user1", "Electric Utility", "2024-01-01", 75.0)
    assert get_is_utility(transaction)
    transaction = create_transaction(2, "user1", "Restaurant", "2024-01-02", 30.0)
    assert not get_is_utility(transaction)


def test_get_is_phone() -> None:
    """Test get_is_phone identifies phone payments."""
    transaction = create_transaction(1, "user1", "AT&T Wireless", "2024-01-01", 60.0)
    assert get_is_phone(transaction)
    transaction = create_transaction(2, "user1", "Coffee Shop", "2024-01-02", 5.0)
    assert not get_is_phone(transaction)


def test_get_n_transactions_days_apart() -> None:
    """Test get_n_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 0) == 2
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 1) == 4


def test_get_n_transactions_same_day() -> None:
    """Test get_n_transactions_same_day counts transactions on same day of month."""
    transactions = [
        create_transaction(1, "user1", "Netflix", "2024-01-01", 15.99),
        create_transaction(2, "user1", "Netflix", "2024-02-01", 15.99),
        create_transaction(3, "user1", "Netflix", "2024-03-03", 15.99),
    ]
    transaction = transactions[0]
    assert get_n_transactions_same_day(transaction, transactions, 1) == 2


def test_get_pct_transactions_same_day() -> None:
    """Test get_pct_transactions_same_day calculates correct percentage."""
    transactions = [
        create_transaction(1, "user1", "Netflix", "2024-01-01", 15.99),
        create_transaction(2, "user1", "Netflix", "2024-02-01", 15.99),
        create_transaction(3, "user1", "Netflix", "2024-03-03", 15.99),
    ]
    transaction = transactions[0]
    assert get_pct_transactions_same_day(transaction, transactions, 1) == 2 / 3


def test_get_ends_in_99() -> None:
    """Test that get_ends_in_99 returns True for amounts ending in 99."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert not get_ends_in_99(transactions[0])
    assert get_ends_in_99(transactions[3])


def test_get_average_transaction_amount() -> None:
    """Test get_average_transaction_amount calculates correct average."""
    transactions = [
        create_transaction(1, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(2, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(3, "user1", "name1", "2024-01-02", 200.0),
        create_transaction(4, "user1", "name1", "2024-01-03", 2.99),
    ]
    # (100 + 100 + 200 + 2.99) / 4 = 100.7475 ≈ 100.75
    assert round(get_average_transaction_amount(transactions), 2) == 100.75


def test_get_max_transaction_amount() -> None:
    """Test get_max_transaction_amount identifies maximum amount."""
    transactions = [
        create_transaction(1, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(2, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(3, "user1", "name1", "2024-01-02", 200.0),
        create_transaction(4, "user1", "name1", "2024-01-03", 2.99),
    ]
    assert get_max_transaction_amount(transactions) == 200.0


def test_get_min_transaction_amount() -> None:
    """Test get_min_transaction_amount identifies minimum amount."""
    transactions = [
        create_transaction(1, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(2, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(3, "user1", "name1", "2024-01-02", 200.0),
        create_transaction(4, "user1", "name1", "2024-01-03", 2.99),
    ]
    assert get_min_transaction_amount(transactions) == 2.99


def test_get_most_frequent_names() -> None:
    """Test get_most_frequent_names identifies merchants with multiple amounts."""
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 10.0),  # Same amount
        create_transaction(3, "user1", "StoreA", "2024-01-03", 20.0),  # Different amount
        create_transaction(4, "user1", "StoreB", "2024-01-04", 30.0),
    ]
    # StoreA has transactions with same amount (10.0) and different amounts (10.0 and 20.0)
    assert len(get_most_frequent_names(transactions)) == 1  # StoreA has multiple amounts


def test_is_recurring() -> None:
    """Test is_recurring identifies recurring transactions."""
    transactions = [
        create_transaction(1, "user1", "Netflix", "2024-01-01", 15.99),
        create_transaction(2, "user1", "Netflix", "2024-02-01", 15.99),
        create_transaction(3, "user1", "Netflix", "2024-03-01", 15.99),
    ]
    transaction = transactions[0]
    assert is_recurring(transaction, transactions)
