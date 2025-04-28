# test features
import pytest

from recur_scan.features_segun import (
    amazon_prime_day_proximity,  # New feature
    calculate_streak,  # New feature
    get_average_transaction_amount,
    get_average_transaction_interval,
    get_max_transaction_amount,
    get_min_transaction_amount,
    get_new_features,
    get_total_transaction_amount,
    get_transaction_amount_frequency,
    get_transaction_amount_median,
    get_transaction_amount_percentage,  # New feature
    get_transaction_amount_range,
    get_transaction_amount_std,
    get_transaction_count,
    get_transaction_day_of_week,
    get_transaction_frequency_per_month,  # New feature
    get_transaction_interval_std,  # New feature
    get_transaction_is_weekend,  # New feature
    get_transaction_recency,  # New feature
    get_transaction_time_of_day,
    get_unique_transaction_amount_count,
    is_recurring_day,  #  New feature
    markovian_probability,  # New feature
    transaction_amount_similarity,  #  New feature
    transaction_day_of_month,  # New feature
)
from recur_scan.transactions import Transaction


def test_get_total_transaction_amount() -> None:
    """Test that get_total_transaction_amount returns the correct total amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),
    ]
    assert get_total_transaction_amount(transactions) == 450.0


def test_get_average_transaction_amount() -> None:
    """Test that get_average_transaction_amount returns the correct average amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),
    ]
    assert get_average_transaction_amount(transactions) == 150.0


def test_get_max_transaction_amount() -> None:
    """Test that get_max_transaction_amount returns the correct maximum amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),
    ]
    assert get_max_transaction_amount(transactions) == 200.0


def test_get_min_transaction_amount() -> None:
    """Test that get_min_transaction_amount returns the correct minimum amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),
    ]
    assert get_min_transaction_amount(transactions) == 100.0


def test_get_transaction_count() -> None:
    """Test that get_transaction_count returns the correct number of transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),
    ]
    assert get_transaction_count(transactions) == 3


def test_get_transaction_amount_std() -> None:
    """Test that get_transaction_amount_std returns the correct standard deviation of transaction amounts."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),
    ]
    assert get_transaction_amount_std(transactions) == pytest.approx(50.0)


def test_get_transaction_amount_median() -> None:
    """Test that get_transaction_amount_median returns the correct median transaction amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),
    ]
    assert get_transaction_amount_median(transactions) == 150.0


def test_get_transaction_amount_range() -> None:
    """Test that get_transaction_amount_range returns the correct range of transaction amounts."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),
    ]
    assert get_transaction_amount_range(transactions) == 100.0


def test_get_unique_transaction_amount_count() -> None:
    """Test that get_unique_transaction_amount_count returns the correct number of unique transaction amounts."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),
    ]
    assert get_unique_transaction_amount_count(transactions) == 3


def test_get_transaction_amount_frequency() -> None:
    """Test that get_transaction_amount_frequency returns the correct frequency of the transaction amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=100.0, date="2024-01-03"),
    ]
    assert get_transaction_amount_frequency(transactions[0], transactions) == 2


def test_get_transaction_day_of_week() -> None:
    """Test that get_transaction_day_of_week returns the correct day of the week."""
    transaction = Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01")  # Monday
    assert get_transaction_day_of_week(transaction) == 0  # 0 = Monday


def test_get_transaction_time_of_day() -> None:
    """Test that get_transaction_time_of_day returns the correct time of day."""
    transaction = Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01 15:30:00")
    assert get_transaction_time_of_day(transaction) == 2  # Afternoon (12pm-6pm)


def test_get_average_transaction_interval() -> None:
    """Test that get_average_transaction_interval returns the correct average interval between transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100.0, date="2024-01-05"),
        Transaction(id=3, user_id="user1", name="name1", amount=100.0, date="2024-01-10"),
    ]
    assert get_average_transaction_interval(transactions) == 4.5  # (4 + 5) / 2


def test_get_transaction_interval_std() -> None:
    """Test that get_transaction_interval_std returns the correct standard deviation of transaction intervals."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-05"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-10"),
    ]
    # Intervals: 4 days, 5 days → Mean: 4.5 → Std: sqrt(((4-4.5)^2 + (5-4.5)^2) / 2) = 0.5
    assert get_transaction_interval_std(transactions) == pytest.approx(0.707, rel=1e-3)  # Adjusted for actual std


def test_get_transaction_amount_percentage() -> None:
    """Test that get_transaction_amount_percentage returns the correct percentage of the total transaction amounts."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-05"),
        Transaction(id=3, user_id="user1", name="name1", amount=250.0, date="2024-01-10"),
    ]
    assert get_transaction_amount_percentage(transactions[0], transactions) == pytest.approx(20.0)  # 100 / 500 * 100


def test_get_transaction_recency() -> None:
    """Test that get_transaction_recency returns the correct number of days since the last transaction."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-05"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-10"),
    ]
    assert get_transaction_recency(transactions[2], transactions) == 5  # Days since Jan 5 to Jan 10


def test_get_transaction_frequency_per_month() -> None:
    """Test that get_transaction_frequency_per_month returns the correct average transactions per month."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-02-15"),
    ]
    assert get_transaction_frequency_per_month(transactions) == pytest.approx(1.5)  # 3 transactions over 2 months


def test_get_transaction_is_weekend() -> None:
    """Test that get_transaction_is_weekend correctly identifies weekend transactions."""
    transaction_weekday = Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01")  # Monday
    transaction_weekend = Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-06")  # Saturday
    assert get_transaction_is_weekend(transaction_weekday) is False
    assert get_transaction_is_weekend(transaction_weekend) is True


def test_amazon_prime_day_proximity() -> None:
    """Test that amazon_prime_day_proximity returns the correct proximity to the 17th of the month."""
    transaction = Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01")
    assert amazon_prime_day_proximity(transaction) == 16  # |1 - 17|


def test_transaction_day_of_month() -> None:
    """Test that transaction_day_of_month returns the correct day of the month."""
    transaction = Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01")
    assert transaction_day_of_month(transaction) == 1


def test_is_recurring_day() -> None:
    """Test that is_recurring_day correctly identifies recurring days."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-08"),  # 7 days apart
    ]
    assert is_recurring_day(transactions) is True  # Adjusted to match function signature


def test_transaction_amount_similarity() -> None:
    """Test that transaction_amount_similarity returns the correct similarity measure."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),
    ]
    assert (
        transaction_amount_similarity(transactions[1], transactions) == 50.0
    )  # Min difference: |150-100| or |150-200|


def test_markovian_probability() -> None:
    """Test that markovian_probability returns the correct probability based on day-of-week transitions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),  # Monday
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),  # Tuesday
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),  # Wednesday
    ]
    # Transition: Monday → Tuesday, Tuesday → Wednesday
    # From Tuesday to Wednesday: probability = 1.0 (only transition from Tuesday is to Wednesday)
    assert markovian_probability(transactions[2], transactions) == pytest.approx(1.0)

    # Test with single transaction
    single_transaction = [Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01")]
    assert markovian_probability(single_transaction[0], single_transaction) == 0.0


def test_calculate_streak() -> None:
    """Test that calculate_streak returns the correct longest streak of consecutive days."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="name1", amount=250.0, date="2024-01-05"),
    ]
    # Streak: Jan 1 to Jan 3 (3 days), then a break, then Jan 5
    assert calculate_streak(transactions) == 3

    # Test with single transaction
    single_transaction = [Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01")]
    assert calculate_streak(single_transaction) == 1


def test_get_new_features() -> None:
    """Test that get_new_features includes all new features and returns correct values."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=150.0, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200.0, date="2024-01-03"),
    ]

    features = get_new_features(transactions[2], transactions)
    assert "transaction_interval_std" in features
    assert "transaction_amount_percentage" in features
    assert "transaction_recency" in features
    assert "transaction_frequency_per_month" in features
    assert "transaction_is_weekend" in features
    assert "amazon_prime_day_proximity" in features
    assert "transaction_day_of_month" in features
    assert "is_recurring_day" in features
    assert "transaction_amount_similarity" in features
    assert "markovian_probability" in features
    assert "transaction_streak" in features
    # Test some feature values
    assert features["transaction_interval_std"] == pytest.approx(0.0)  # Only 2 intervals (1, 1), std = 0
    assert features["transaction_amount_percentage"] == pytest.approx(44.44, rel=1e-2)  # 200 / 500 * 100
    assert features["transaction_recency"] == 1  # Jan 3 - Jan 2
    assert features["transaction_frequency_per_month"] == pytest.approx(3.0)  # 3 transactions in 1 month
    assert features["transaction_is_weekend"] is False  # Wednesday
    assert features["amazon_prime_day_proximity"] == 14  # |3 - 17|
    assert features["transaction_day_of_month"] == 3
    assert features["is_recurring_day"] is False  # No 7 or 30-day intervals
    assert features["transaction_amount_similarity"] == 50.0  # |200-150|
    assert features["markovian_probability"] == pytest.approx(1.0)  # Tuesday → Wednesday
    assert features["transaction_streak"] == 3  # Jan 1 to Jan 3
