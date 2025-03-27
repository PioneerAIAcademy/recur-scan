import pytest

from recur_scan.features import (
    classify_subscription_tier,
    count_transactions_by_amount,
    get_amount_features,
    get_ends_in_99,
    get_is_always_recurring,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_monthly_spending_trend,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
    get_recurrence_patterns,
    get_recurring_consistency_score,
    get_refund_features,
    get_user_behavior_features,
    validate_recurring_transaction,
)
from recur_scan.transactions import Transaction


@pytest.fixture
def sample_transactions():
    """Fixture providing test transactions for various test cases."""
    return [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.49, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.49, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.49, date="2024-03-01"),
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"),
        Transaction(id=5, user_id="user1", name="Spotify", amount=9.99, date="2024-02-15"),
        Transaction(id=6, user_id="user1", name="AT&T", amount=100.00, date="2024-01-01"),
        Transaction(id=7, user_id="user1", name="AT&T", amount=100.00, date="2024-01-16"),
        Transaction(id=8, user_id="user1", name="Duke Energy", amount=75.00, date="2024-01-05"),
        Transaction(id=9, user_id="user1", name="Allstate Insurance", amount=150.00, date="2024-01-10"),
        Transaction(id=10, user_id="user1", name="Random Charge", amount=2.99, date="2024-01-20"),
        Transaction(id=11, user_id="user1", name="Netflix", amount=-15.49, date="2024-01-05"),  # Refund
    ]


def test_count_transactions_by_amount(sample_transactions):
    """Test counting transactions with same amount."""
    count, pct = count_transactions_by_amount(sample_transactions[0], sample_transactions)
    assert count == 3  # Three Netflix transactions at 15.49
    assert pct == 3 / 11


def test_get_recurrence_patterns(sample_transactions):
    """Test detection of recurrence patterns."""
    patterns = get_recurrence_patterns(sample_transactions[0], sample_transactions)
    assert patterns["is_monthly"] == 1
    assert 27 <= patterns["avg_days_between"] <= 31
    assert patterns["recurrence_score"] > 0.5


def test_get_recurring_consistency_score(sample_transactions):
    """Test calculation of recurring consistency score."""
    score = get_recurring_consistency_score(sample_transactions[0], sample_transactions)
    assert 0.7 <= score["recurring_consistency_score"] <= 1.0  # Should be high for consistent monthly payments


def test_validate_recurring_transaction(sample_transactions):
    """Test validation of recurring transactions."""
    assert validate_recurring_transaction(sample_transactions[0])  # Netflix is known recurring
    assert not validate_recurring_transaction(sample_transactions[9])  # Random charge is not


def test_classify_subscription_tier(sample_transactions):
    """Test classification of subscription tiers."""
    assert classify_subscription_tier(sample_transactions[0]) == "Standard"  # Netflix 15.49
    assert classify_subscription_tier(sample_transactions[3]) == "Individual"  # Spotify 9.99
    assert classify_subscription_tier(sample_transactions[9]) == "Unknown"  # Not a subscription


def test_get_amount_features(sample_transactions):
    """Test extraction of amount features."""
    features = get_amount_features(sample_transactions[0], sample_transactions)
    assert features["is_fixed_amount_recurring"] == 1  # Netflix amount is fixed
    assert features["amount_fluctuation"] == 0.0
    assert features["price_cluster"] == 0  # Should be in first cluster


def test_get_user_behavior_features(sample_transactions):
    """Test extraction of user behavior features."""
    features = get_user_behavior_features(sample_transactions[0], sample_transactions)
    assert features["user_avg_spent"] > 0
    assert features["user_total_spent"] > 0
    assert features["user_subscription_count"] >= 2  # At least Netflix and Spotify


def test_get_refund_features(sample_transactions):
    """Test extraction of refund features."""
    features = get_refund_features(sample_transactions[0], sample_transactions)
    assert features["refund_rate"] == 1 / 11
    assert features["avg_refund_time_lag"] == 4  # Jan 1 to Jan 5


def test_get_monthly_spending_trend(sample_transactions):
    """Test calculation of monthly spending trend."""
    features = get_monthly_spending_trend(sample_transactions[0], sample_transactions)
    assert features["monthly_spending_trend"] > 0  # Should be sum of all January transactions


def test_get_is_always_recurring(sample_transactions):
    """Test identification of always-recurring vendors."""
    assert get_is_always_recurring(sample_transactions[0])  # Netflix is always recurring
    assert not get_is_always_recurring(sample_transactions[9])  # Random charge is not


def test_get_is_insurance(sample_transactions):
    """Test identification of insurance payments."""
    assert get_is_insurance(sample_transactions[8])  # Allstate is insurance
    assert not get_is_insurance(sample_transactions[0])  # Netflix is not


def test_get_is_phone(sample_transactions):
    """Test identification of phone payments."""
    assert get_is_phone(sample_transactions[5])  # AT&T is phone
    assert not get_is_phone(sample_transactions[0])  # Netflix is not


def test_get_is_utility(sample_transactions):
    """Test identification of utility payments."""
    assert get_is_utility(sample_transactions[7])  # Duke Energy is utility
    assert not get_is_utility(sample_transactions[0])  # Netflix is not


def test_get_n_transactions_days_apart(sample_transactions):
    """Test counting transactions days apart."""
    # AT&T transactions are 15 days apart (Jan 1 and Jan 16)
    assert get_n_transactions_days_apart(sample_transactions[5], sample_transactions, 14, 1) >= 1


def test_get_n_transactions_same_day(sample_transactions):
    """Test counting transactions on same day."""
    # Netflix and AT&T both on Jan 1
    assert get_n_transactions_same_day(sample_transactions[0], sample_transactions, 0) == 2


def test_get_ends_in_99(sample_transactions):
    """Test detection of amounts ending in .99."""
    assert get_ends_in_99(sample_transactions[3])  # Spotify 9.99
    assert not get_ends_in_99(sample_transactions[0])  # Netflix 15.49


def test_get_n_transactions_same_amount(sample_transactions):
    """Test counting transactions with same amount."""
    assert get_n_transactions_same_amount(sample_transactions[0], sample_transactions) == 3  # 3 Netflix at 15.49


def test_get_percent_transactions_same_amount(sample_transactions):
    """Test percentage of transactions with same amount."""
    pct = get_percent_transactions_same_amount(sample_transactions[0], sample_transactions)
    assert pytest.approx(pct) == 3 / 11  # 3 out of 11 transactions
    
def test_get_n_transactions_same_amount() -> None:
    """Test that get_n_transactions_same_amount returns the correct number of transactions with the same amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert get_n_transactions_same_amount(transactions[0], transactions) == 2
    assert get_n_transactions_same_amount(transactions[2], transactions) == 1


def test_get_percent_transactions_same_amount() -> None:
    """
    Test that get_percent_transactions_same_amount returns correct percentage.
    Tests that the function calculates the right percentage of transactions with matching amounts.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 2 / 4


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


def test_get_n_transactions_same_day() -> None:
    """Test that get_n_transactions_same_day returns the correct number of transactions on the same day."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert get_n_transactions_same_day(transactions[0], transactions, 0) == 2
    assert get_n_transactions_same_day(transactions[0], transactions, 1) == 3
    assert get_n_transactions_same_day(transactions[2], transactions, 0) == 1


def test_get_pct_transactions_same_day() -> None:
    """Test that get_pct_transactions_same_day returns the correct percentage of transactions on the same day."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert get_pct_transactions_same_day(transactions[0], transactions, 0) == 2 / 4


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


def test_get_pct_transactions_days_apart() -> None:
    """Test get_pct_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_pct_transactions_days_apart(transactions[0], transactions, 14, 0) == 2 / 7
    assert get_pct_transactions_days_apart(transactions[0], transactions, 14, 1) == 4 / 7


def test_get_is_insurance() -> None:
    """Test get_is_insurance."""
    assert get_is_insurance(
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01")
    )
    assert not get_is_insurance(Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"))


def test_get_is_phone() -> None:
    """Test get_is_phone."""
    assert get_is_phone(Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"))
    assert not get_is_phone(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))


def test_get_is_utility() -> None:
    """Test get_is_utility."""
    assert get_is_utility(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))
    assert not get_is_utility(
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03")
    )


def test_get_is_always_recurring() -> None:
    """Test get_is_always_recurring."""
    assert get_is_always_recurring(Transaction(id=1, user_id="user1", name="netflix", amount=100, date="2024-01-01"))
    assert not get_is_always_recurring(
        Transaction(id=2, user_id="user1", name="walmart", amount=100, date="2024-01-01")
    )
