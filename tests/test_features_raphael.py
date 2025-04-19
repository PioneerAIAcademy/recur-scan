# test features_raphael.py

from recur_scan.features_raphael import (
    get_amount_variation,
    get_description_pattern,
    get_has_irregular_spike,
    get_has_trial_period,
    get_is_common_subscription_amount,
    get_is_first_of_month,
    get_is_fixed_interval,
    get_is_seasonal,
    get_is_similar_name,
    # New feature imports
    get_is_weekday_consistent,
    get_is_weekend_transaction,
    get_n_transactions_days_apart,
    get_n_transactions_same_day,
    get_new_features,
    get_occurs_same_week,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
)
from recur_scan.transactions import Transaction


# ===== Existing Test Cases (Unchanged) =====
def test_get_n_transactions_same_day() -> None:
    """Test that get_n_transactions_same_day returns the correct number of transactions on the same day."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),  # Same day
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-01-02"),  # +1 day
        Transaction(id=4, user_id="user1", name="Netflix", amount=15.99, date="2024-01-31"),  # Month boundary case
        Transaction(id=5, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"),
    ]

    # Exact same day matches (no tolerance)
    assert get_n_transactions_same_day(transactions[0], transactions, 0) == 2  # Only Jan 1 transactions

    # With 1 day tolerance
    assert get_n_transactions_same_day(transactions[0], transactions, 1) == 3  # Jan 1, Jan 2

    # Month boundary case with 1 day tolerance (Jan 31 and Feb 1)
    jan31 = Transaction(id=6, user_id="user1", name="Rent", amount=1200.0, date="2024-01-31")
    feb1 = Transaction(id=7, user_id="user1", name="Rent", amount=1200.0, date="2024-02-01")
    assert get_n_transactions_same_day(jan31, [jan31, feb1], 1) == 2


def test_get_pct_transactions_same_day() -> None:
    """Test that get_pct_transactions_same_day returns the correct percentage of transactions on the same day."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"),
    ]
    assert get_pct_transactions_same_day(transactions[0], transactions, 0) == 2 / 3


def test_get_n_transactions_days_apart() -> None:
    """Test get_n_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-31"),
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"),
    ]
    assert get_n_transactions_days_apart(transactions[0], transactions, 30, 0) == 1
    assert get_n_transactions_days_apart(transactions[0], transactions, 30, 1) == 2


def test_get_pct_transactions_days_apart() -> None:
    """Test get_pct_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-31"),
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-02-01"),
    ]
    assert get_pct_transactions_days_apart(transactions[0], transactions, 30, 0) == 1 / 3
    assert get_pct_transactions_days_apart(transactions[0], transactions, 30, 1) == 2 / 3


def test_get_is_common_subscription_amount() -> None:
    """Test that get_is_common_subscription_amount correctly identifies subscription amounts."""
    assert get_is_common_subscription_amount(
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01")
    )
    assert not get_is_common_subscription_amount(
        Transaction(id=2, user_id="user1", name="Unknown Service", amount=27.5, date="2024-01-01")
    )


def test_get_is_first_of_month() -> None:
    """Test get_is_first_of_month."""
    assert get_is_first_of_month(Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"))
    assert not get_is_first_of_month(Transaction(id=2, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"))


def test_get_is_fixed_interval() -> None:
    """Test get_is_fixed_interval."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"),
    ]
    assert get_is_fixed_interval(
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"), transactions
    )
    assert not get_is_fixed_interval(
        Transaction(id=2, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"), transactions
    )


def test_get_is_similar_name() -> None:
    """Test get_is_similar_name."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix Premium", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
    ]
    assert get_is_similar_name(transactions[0], transactions)
    assert not get_is_similar_name(
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"), transactions
    )


def test_get_has_irregular_spike() -> None:
    """Test get_has_irregular_spike."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-31"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=50.99, date="2024-02-01"),
    ]
    assert get_has_irregular_spike(
        Transaction(id=3, user_id="user1", name="Netflix", amount=150.99, date="2024-03-01"), transactions
    )
    assert not get_has_irregular_spike(
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"), transactions
    )


def test_get_occurs_same_week() -> None:
    """Test get_occurs_same_week."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Salary", amount=3000.0, date="2024-01-05"),  # First Friday
        Transaction(id=2, user_id="user1", name="Salary", amount=3000.0, date="2024-02-02"),  # First Friday
    ]
    assert get_occurs_same_week(
        Transaction(id=3, user_id="user1", name="Salary", amount=3000.0, date="2024-03-01"), transactions
    )
    assert not get_occurs_same_week(
        Transaction(id=4, user_id="user1", name="Bonus", amount=500.0, date="2024-01-15"), transactions
    )


# ===== New Test Cases for Additional Features =====
def test_get_is_weekday_consistent() -> None:
    """Test get_is_weekday_consistent."""
    # Monday transactions
    monday_txns = [
        Transaction(id=1, user_id="user1", name="Gym", amount=50.0, date="2024-01-01"),  # Monday
        Transaction(id=2, user_id="user1", name="Gym", amount=50.0, date="2024-01-08"),  # Monday
    ]
    # Mixed weekday transactions
    mixed_txns = [
        Transaction(id=3, user_id="user1", name="Yoga", amount=30.0, date="2024-01-01"),  # Monday
        Transaction(id=4, user_id="user1", name="Yoga", amount=30.0, date="2024-01-03"),  # Wednesday
    ]

    assert get_is_weekday_consistent(monday_txns[0], monday_txns)
    assert not get_is_weekday_consistent(mixed_txns[0], mixed_txns)


def test_get_is_seasonal() -> None:
    """Test get_is_seasonal."""
    annual_txns = [
        Transaction(id=1, user_id="user1", name="Insurance", amount=500.0, date="2023-01-15"),
        Transaction(id=2, user_id="user1", name="Insurance", amount=500.0, date="2024-01-16"),
    ]
    monthly_txns = [
        Transaction(id=3, user_id="user1", name="Rent", amount=1200.0, date="2024-01-01"),
        Transaction(id=4, user_id="user1", name="Rent", amount=1200.0, date="2024-02-01"),
    ]

    assert get_is_seasonal(annual_txns[1], annual_txns)
    assert not get_is_seasonal(monthly_txns[1], monthly_txns)


def test_get_amount_variation() -> None:
    """Test get_amount_variation."""
    stable_txns = [
        Transaction(id=1, user_id="user1", name="Utility", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Utility", amount=105.0, date="2024-02-01"),
    ]
    variable_txns = [
        Transaction(id=3, user_id="user1", name="Electric", amount=80.0, date="2024-01-01"),
        Transaction(id=4, user_id="user1", name="Electric", amount=120.0, date="2024-02-01"),
    ]

    assert 0 < get_amount_variation(stable_txns[0], stable_txns) < 10
    assert get_amount_variation(variable_txns[0], variable_txns) >= 20


def test_get_has_trial_period() -> None:
    """Test get_has_trial_period."""
    trial_txns = [
        Transaction(id=1, user_id="user1", name="Service", amount=0.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Service", amount=9.99, date="2024-02-01"),
    ]
    regular_txns = [
        Transaction(id=3, user_id="user1", name="Subscription", amount=9.99, date="2024-01-01"),
        Transaction(id=4, user_id="user1", name="Subscription", amount=9.99, date="2024-02-01"),
    ]

    assert get_has_trial_period(trial_txns[1], trial_txns)
    assert not get_has_trial_period(regular_txns[1], regular_txns)


def test_get_description_pattern() -> None:
    """Test get_description_pattern."""
    assert (
        get_description_pattern(Transaction(id=1, user_id="user1", name="ACH Payment", amount=100, date="2024-01-01"))
        == "ach"
    )
    assert (
        get_description_pattern(
            Transaction(id=2, user_id="user1", name="Autopay Electric", amount=100, date="2024-01-01")
        )
        == "auto"
    )
    assert (
        get_description_pattern(Transaction(id=3, user_id="user1", name="Invoice #123", amount=100, date="2024-01-01"))
        == "invoice"
    )
    assert (
        get_description_pattern(Transaction(id=4, user_id="user1", name="Grocery Store", amount=50, date="2024-01-01"))
        == "other"
    )


def test_get_is_weekend_transaction() -> None:
    """Test get_is_weekend_transaction."""
    assert get_is_weekend_transaction(
        Transaction(id=1, user_id="user1", name="Weekend", amount=50, date="2024-01-06")
    )  # Saturday
    assert not get_is_weekend_transaction(
        Transaction(id=2, user_id="user1", name="Weekday", amount=50, date="2024-01-01")
    )  # Monday


def test_get_new_features() -> None:
    """Test get_new_features with validation for only new features."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=9.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=9.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="ACH Rent Payment", amount=1200.0, date="2024-01-01"),
        Transaction(id=4, user_id="user1", name="ACH Rent Payment", amount=1200.0, date="2024-02-01"),
        Transaction(id=5, user_id="user1", name="Trial Service", amount=0.0, date="2024-01-01"),
        Transaction(id=6, user_id="user1", name="Trial Service", amount=14.99, date="2024-02-01"),
    ]

    # Test Netflix transaction (monthly subscription)
    netflix_features = get_new_features(transactions[1], transactions)
    assert "is_weekday_consistent" in netflix_features
    assert "is_seasonal" in netflix_features
    assert "amount_variation_pct" in netflix_features
    assert "had_trial_period" in netflix_features
    assert "description_pattern" in netflix_features
    assert "is_weekend_transaction" in netflix_features
    assert "n_days_apart_30" in netflix_features
    assert "pct_days_apart_30" in netflix_features
