# test features

from recur_scan.features_bassey import (
    get_is_gym_membership,
    get_is_streaming_service,
    get_is_subscription,
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
