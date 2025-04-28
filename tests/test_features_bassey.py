# test features

from recur_scan.features_bassey import (
    get_days_since_last_transaction_bassey,
    get_is_frequent_merchant_bassey,
    get_is_gym_membership,
    get_is_high_value_transaction_bassey,
    get_is_merchant_recurring_bassey,
    get_is_same_day_multiple_transactions_bassey,
    get_is_streaming_service,
    get_is_subscription,
    get_is_weekend_transaction_bassey,
    get_monthly_spending_average_bassey,
)
from recur_scan.transactions import Transaction


def test_get_is_subscription() -> None:
    """Test get_is_subscription."""
    assert get_is_subscription(
        Transaction(id=1, user_id="user1", name="Monthly Subscription", amount=10, date="2024-01-01")
    )
    assert not get_is_subscription(
        Transaction(id=2, user_id="user1", name="One-time Purchase", amount=50, date="2024-01-01")
    )


def test_get_is_streaming_service() -> None:
    """Test get_is_streaming_service."""
    assert get_is_streaming_service(Transaction(id=1, user_id="user1", name="Netflix", amount=15, date="2024-01-01"))
    assert not get_is_streaming_service(
        Transaction(id=2, user_id="user1", name="Walmart", amount=100, date="2024-01-01")
    )


def test_get_is_gym_membership() -> None:
    """Test get_is_gym_membership."""
    assert get_is_gym_membership(
        Transaction(id=1, user_id="user1", name="Planet Fitness Membership", amount=30, date="2024-01-01")
    )
    assert not get_is_gym_membership(
        Transaction(id=2, user_id="user1", name="Amazon Purchase", amount=200, date="2024-01-01")
    )


# Test cases for only the new features


def test_get_is_recurring_apple_bassey() -> None:
    """Test get_is_recurring_apple_bassey."""
    assert get_is_subscription(
        Transaction(id=1, user_id="user1", name="Apple Subscription", amount=10, date="2024-01-01")
    )
    assert not get_is_subscription(
        Transaction(id=2, user_id="user1", name="One-time Apple Purchase", amount=50, date="2024-01-01")
    )


def test_get_is_weekly_recurring_apple_bassey() -> None:
    """Test get_is_weekly_recurring_apple_bassey."""
    assert get_is_subscription(
        Transaction(id=1, user_id="user1", name="Weekly Apple Subscription", amount=10, date="2024-01-01")
    )
    assert not get_is_subscription(
        Transaction(id=2, user_id="user1", name="One-time Apple Purchase", amount=50, date="2024-01-01")
    )


def test_get_is_high_value_transaction_bassey() -> None:
    """Test get_is_high_value_transaction_bassey."""
    assert get_is_high_value_transaction_bassey(
        Transaction(id=1, user_id="user1", name="Purchase", amount=150, date="2024-01-01")
    )
    assert not get_is_high_value_transaction_bassey(
        Transaction(id=2, user_id="user1", name="Purchase", amount=50, date="2024-01-01")
    )


def test_get_is_frequent_merchant_bassey() -> None:
    """Test get_is_frequent_merchant_bassey."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Amazon", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Amazon", amount=50, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="Amazon", amount=30, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="Amazon", amount=20, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="Amazon", amount=10, date="2024-01-05"),
    ]
    assert get_is_frequent_merchant_bassey(transactions[0], transactions)
    assert not get_is_frequent_merchant_bassey(
        Transaction(id=6, user_id="user1", name="Walmart", amount=50, date="2024-01-01"), transactions
    )


def test_get_is_weekend_transaction_bassey() -> None:
    """Test get_is_weekend_transaction_bassey."""
    assert get_is_weekend_transaction_bassey(
        Transaction(id=1, user_id="user1", name="Purchase", amount=100, date="2024-01-06")
    )  # Saturday
    assert not get_is_weekend_transaction_bassey(
        Transaction(id=2, user_id="user1", name="Purchase", amount=50, date="2024-01-03")
    )  # Wednesday


def test_get_monthly_spending_average_bassey() -> None:
    """Test get_monthly_spending_average_bassey."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Purchase", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Purchase", amount=50, date="2024-01-15"),
        Transaction(id=3, user_id="user1", name="Purchase", amount=150, date="2024-01-20"),
    ]
    assert get_monthly_spending_average_bassey(transactions[0], transactions) == 100.0


def test_get_is_merchant_recurring_bassey() -> None:
    """Test get_is_merchant_recurring_bassey."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Amazon", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Amazon", amount=50, date="2024-02-01"),
    ]
    assert get_is_merchant_recurring_bassey(transactions[0], transactions)
    assert not get_is_merchant_recurring_bassey(
        Transaction(id=3, user_id="user1", name="Walmart", amount=50, date="2024-01-01"), transactions
    )


def test_get_days_since_last_transaction_bassey() -> None:
    """Test get_days_since_last_transaction_bassey."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Purchase", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Purchase", amount=50, date="2024-01-10"),
    ]
    assert get_days_since_last_transaction_bassey(transactions[1], transactions) == 9
    assert get_days_since_last_transaction_bassey(transactions[0], transactions) == -1  # No previous transaction


def test_get_is_same_day_multiple_transactions_bassey() -> None:
    """Test get_is_same_day_multiple_transactions_bassey."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Purchase", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Purchase", amount=50, date="2024-01-01"),
    ]
    assert get_is_same_day_multiple_transactions_bassey(transactions[0], transactions)
    assert not get_is_same_day_multiple_transactions_bassey(
        Transaction(id=3, user_id="user1", name="Purchase", amount=50, date="2024-01-02"), transactions
    )
