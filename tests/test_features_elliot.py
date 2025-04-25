import pytest

from recur_scan.features_elliot import (
    get_is_always_recurring,
    get_is_near_same_amount,
    get_transaction_similarity,
    is_auto_pay,
    is_membership,
    is_price_trending,
    is_recurring_based_on_99,
    is_split_transaction,
    is_utility_bill,
    is_weekday_transaction,
)
from recur_scan.transactions import Transaction


@pytest.fixture
def transactions():
    """Fixture providing test transactions."""
    return [
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03"),
        Transaction(id=5, user_id="user1", name="Netflix", amount=15.99, date="2024-01-04"),
        Transaction(id=6, user_id="user1", name="AutoPay Subscription", amount=50, date="2024-01-05"),
        Transaction(id=7, user_id="user1", name="Gym Membership", amount=30, date="2024-01-06"),
    ]


def test_is_utility_bill(transactions) -> None:
    """Test is_utility_bill."""
    assert is_utility_bill(transactions[2])  # Assuming transactions[2] is a utility bill
    assert not is_utility_bill(transactions[3])  # Assuming transactions[3] is NOT a utility bill


def test_get_is_near_same_amount(transactions) -> None:
    """Test get_is_near_same_amount."""
    assert get_is_near_same_amount(transactions[0], transactions)
    assert not get_is_near_same_amount(transactions[3], transactions)


def test_get_is_always_recurring(transactions) -> None:
    """Test get_is_always_recurring."""
    assert get_is_always_recurring(transactions[4])
    assert not get_is_always_recurring(transactions[3])


def test_is_auto_pay(transactions) -> None:
    """Test is_auto_pay."""
    assert is_auto_pay(transactions[5])
    assert not is_auto_pay(transactions[0])


def test_is_membership(transactions) -> None:
    """Test is_membership."""
    assert is_membership(transactions[6])
    assert not is_membership(transactions[0])


def test_is_recurring_based_on_99(transactions):
    """Test the is_recurring_based_on_99 function."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Spotify", amount=9.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Spotify", amount=9.99, date="2024-01-08"),  # 7 days later
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"),  # 7 days later
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-02-14"),  # 30 days later
        Transaction(id=5, user_id="user1", name="Netflix", amount=14.99, date="2024-01-01"),  # Different vendor
        Transaction(id=6, user_id="user1", name="Spotify", amount=9.99, date="2024-03-14"),  # 30 days later
        Transaction(id=7, user_id="user1", name="Spotify", amount=10.00, date="2024-04-14"),  # Not ending in .99
    ]

    # Case 1: Transaction follows the recurring pattern (7-day interval, at least 3 occurrences)
    assert is_recurring_based_on_99(transactions[0], transactions)

    # Case 2: Different vendor, should return False
    assert not is_recurring_based_on_99(transactions[4], transactions)

    # Case 3: Amount does not end in .99, should return False
    assert not is_recurring_based_on_99(transactions[6], transactions)

    # Case 4: Only two transactions exist with .99, should return False
    small_list = transactions[:2]  # Only two transactions
    assert not is_recurring_based_on_99(transactions[1], small_list)

    # Case 5: Transaction is in a valid 30-day recurring pattern
    assert is_recurring_based_on_99(transactions[5], transactions)

    # Case 6: Transaction is in a valid 30-day recurring pattern
    assert is_recurring_based_on_99(transactions[3], transactions)


# New tests


@pytest.fixture
def new_transactions():
    """Fixture providing new test transactions."""
    return [
        Transaction(id=1, user_id="user1", name="Spotify", amount=9.99, date="2024-03-18"),  # Monday
        Transaction(id=2, user_id="user1", name="Spotify Premium", amount=9.99, date="2024-03-19"),  # Tuesday
        Transaction(id=3, user_id="user1", name="Spotify US", amount=9.99, date="2024-03-20"),  # Wednesday
        Transaction(id=4, user_id="user1", name="Amazon Prime", amount=14.99, date="2024-03-21"),  # Thursday
        Transaction(id=5, user_id="user1", name="Netflix", amount=15.99, date="2024-03-22"),  # Friday
        Transaction(id=6, user_id="user1", name="Spotify", amount=10.99, date="2024-03-23"),  # Saturday
        Transaction(id=7, user_id="user1", name="Spotify", amount=11.99, date="2024-03-24"),  # Sunday
    ]


def test_get_transaction_similarity(new_transactions):
    """Test get_transaction_similarity function."""
    # Check similarity between slightly different names
    score = get_transaction_similarity(new_transactions[0], new_transactions)
    assert score > 50  # Adjusted similarity threshold

    # Different vendor should have low similarity
    score = get_transaction_similarity(new_transactions[4], new_transactions)
    assert score < 50  # Netflix should not match Spotify


def test_is_weekday_transaction(new_transactions):
    """Test is_weekday_transaction function."""
    assert is_weekday_transaction(new_transactions[0]) is True  # Monday
    assert is_weekday_transaction(new_transactions[4]) is True  # Friday
    assert is_weekday_transaction(new_transactions[5]) is False  # Saturday
    assert is_weekday_transaction(new_transactions[6]) is False  # Sunday


def test_is_price_trending(new_transactions):
    """Test is_price_trending function."""
    assert (
        is_price_trending(new_transactions[0], new_transactions, threshold=15) is True
    )  # Small increase within 15% threshold
    assert (
        is_price_trending(new_transactions[0], new_transactions, threshold=5) is False
    )  # Larger increase, exceeds 5% threshold


def test_is_split_transaction():
    """Test is_split_transaction function."""
    all_transactions = [
        Transaction(id=1, user_id="user1", name="Laptop Payment", amount=1000, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Laptop Payment", amount=500, date="2024-01-10"),
        Transaction(id=3, user_id="user1", name="Laptop Payment", amount=500, date="2024-01-20"),
        Transaction(id=4, user_id="user1", name="Amazon", amount=100, date="2024-02-01"),
    ]

    assert is_split_transaction(all_transactions[0], all_transactions) is True  # Two smaller related transactions
    assert is_split_transaction(all_transactions[3], all_transactions) is False  # No split transactions
