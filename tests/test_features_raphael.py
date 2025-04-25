from recur_scan.features_raphael import (
    get_has_irregular_spike,
    get_is_common_subscription_amount,
    get_is_first_of_month,
    get_is_fixed_interval,
    get_is_similar_name,
    get_n_transactions_days_apart,
    get_n_transactions_same_day,
    get_occurs_same_week,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
)
from recur_scan.transactions import Transaction

# Test data setup
user_id = "user1"
transactions = [
    Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
    Transaction(id=2, user_id="user1", name="Hulu", amount=12.99, date="2024-01-15"),
    Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"),
    Transaction(id=4, user_id="user1", name="Auto Insurance", amount=100.00, date="2024-01-10"),
    Transaction(id=5, user_id="user1", name="T-Mobile Payment", amount=50.00, date="2024-01-20"),
    Transaction(id=6, user_id="user1", name="Electric Utility Bill", amount=75.00, date="2024-01-25"),
    Transaction(id=7, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
    Transaction(id=8, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"),
    Transaction(id=9, user_id="user2", name="Disney+", amount=10.99, date="2024-01-01"),
]
test_transaction = Transaction(id=10, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01")


def get_user_transactions(transactions: list[Transaction], user_id: str) -> list[Transaction]:
    """Filter transactions to only include those belonging to the same user."""
    return [t for t in transactions if t.user_id == user_id]


def test_get_n_transactions_days_apart() -> None:
    user_transactions = get_user_transactions(transactions, "user1")
    result = get_n_transactions_days_apart(test_transaction, user_transactions, 30, 2)
    assert result == 2  # Netflix transactions are 30 days apart


def test_get_pct_transactions_days_apart() -> None:
    user_transactions = get_user_transactions(transactions, "user1")
    pct = get_pct_transactions_days_apart(test_transaction, user_transactions, 30, 2)
    assert pct >= 0.1


def test_get_n_transactions_same_day() -> None:
    test_transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    # Function returns count of OTHER transactions on same day
    assert get_n_transactions_same_day(test_transactions[0], test_transactions, 0) == 1
    # With 1-day tolerance, should catch Jan 1 and Jan 2 transactions
    assert get_n_transactions_same_day(test_transactions[0], test_transactions, 1) == 2
    # Only Jan 2 transaction
    assert get_n_transactions_same_day(test_transactions[2], test_transactions, 0) == 0


def test_get_pct_transactions_same_day() -> None:
    user_transactions = get_user_transactions(transactions, "user1")
    pct = get_pct_transactions_same_day(test_transaction, user_transactions, 0)
    assert pct >= 0.1


def test_get_is_common_subscription_amount() -> None:
    assert get_is_common_subscription_amount(
        Transaction(id=20, user_id="user1", name="Hulu", amount=9.99, date="2024-01-01")
    )
    assert not get_is_common_subscription_amount(
        Transaction(id=21, user_id="user1", name="Store Purchase", amount=27.5, date="2024-01-15")
    )


def test_get_occurs_same_week() -> None:
    assert get_occurs_same_week(
        Transaction(id=22, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"), transactions
    )
    assert not get_occurs_same_week(
        Transaction(id=23, user_id="user1", name="One-time Purchase", amount=99.99, date="2024-01-20"),
        transactions,
    )


def test_get_is_similar_name() -> None:
    assert get_is_similar_name(
        Transaction(id=24, user_id="user1", name="Spotify Premium", amount=9.99, date="2024-02-01"),
        transactions,
    )
    assert not get_is_similar_name(
        Transaction(id=25, user_id="user1", name="Amazon Purchase", amount=50.0, date="2024-03-05"),
        transactions,
    )


def test_get_is_fixed_interval() -> None:
    user_transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"),
    ]
    assert get_is_fixed_interval(
        Transaction(id=26, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"), user_transactions
    )
    assert not get_is_fixed_interval(
        Transaction(id=27, user_id="user1", name="Gas Station", amount=40.0, date="2024-02-10"), transactions
    )


def test_get_has_irregular_spike() -> None:
    user_transactions = [
        *transactions,
        Transaction(id=28, user_id="user1", name="Internet Bill", amount=80.0, date="2024-02-01"),
        Transaction(id=29, user_id="user1", name="Internet Bill", amount=90.0, date="2024-01-01"),
    ]
    assert get_has_irregular_spike(
        Transaction(id=30, user_id="user1", name="Internet Bill", amount=150.0, date="2024-03-01"),
        user_transactions,
    )
    assert not get_has_irregular_spike(
        Transaction(id=31, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"), transactions
    )


def test_get_is_first_of_month() -> None:
    assert get_is_first_of_month(
        Transaction(id=32, user_id="user1", name="Rent Payment", amount=1200.0, date="2024-02-01")
    )
    assert not get_is_first_of_month(
        Transaction(id=33, user_id="user1", name="Grocery", amount=75.0, date="2024-02-15")
    )
