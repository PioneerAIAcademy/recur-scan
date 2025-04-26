import os
import sys
from statistics import stdev

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


import pytest

from recur_scan.features_ebenezer import (
    get_avg_amount_same_day_of_week,
    get_avg_amount_same_month,
    get_avg_amount_same_name,
    get_avg_time_between_transactions,
    get_day_of_week,
    get_is_monthly,
    get_is_recurring,
    get_is_weekend,
    get_is_weekly,
    get_keyword_match,
    get_median_amount_same_name,
    get_n_transactions_same_month,
    get_n_transactions_same_name,
    get_n_transactions_same_user_id,
    get_n_transactions_within_amount_range,
    get_percent_transactions_same_day_of_week,
    get_percent_transactions_same_month,
    get_percent_transactions_same_name,
    get_percent_transactions_same_user_id,
    get_percent_transactions_within_amount_range,
    get_std_amount_same_day_of_week,
    get_std_amount_same_month,
    get_std_amount_same_name,
)
from recur_scan.transactions import Transaction

# Sample transaction data
sample_transactions = [
    Transaction(id=1, user_id=1, name="Amazon Prime", amount=12.99, date="2025-04-01"),
    Transaction(id=2, user_id=1, name="Amazon Prime", amount=12.99, date="2025-04-08"),
    Transaction(id=3, user_id=1, name="Amazon Prime", amount=12.99, date="2025-04-15"),
    Transaction(id=4, user_id=1, name="Netflix", amount=15.99, date="2025-04-01"),
]


def test_get_is_weekly():
    transaction = sample_transactions[0]
    result = get_is_weekly(transaction, sample_transactions)
    assert result == 1  # Weekly pattern detected


def test_get_is_monthly():
    transaction = sample_transactions[0]
    result = get_is_monthly(transaction, sample_transactions)
    assert result == 0  # Not a monthly pattern


def test_get_keyword_match():
    transaction = sample_transactions[0]
    result = get_keyword_match(transaction)
    assert result == 0  # "Amazon Prime" contains "subscription"


@pytest.fixture
def transactions():
    """Fixture providing test transactions."""
    return [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user2", name="vendor2", amount=300, date="2024-02-01"),
        Transaction(id=5, user_id="user2", name="vendor2", amount=300, date="2024-02-02"),
    ]


def test_get_n_transactions_same_name(transactions) -> None:
    """Test that get_n_transactions_same_name returns the correct
    number of transactions with the same name."""
    assert get_n_transactions_same_name(transactions[0], transactions) == 3
    assert get_n_transactions_same_name(transactions[3], transactions) == 2


def test_get_percent_transactions_same_name(transactions) -> None:
    """Test that get_percent_transactions_same_name returns the
    correct percentage of transactions with the same name."""
    assert pytest.approx(get_percent_transactions_same_name(transactions[0], transactions)) == 3 / 5
    assert pytest.approx(get_percent_transactions_same_name(transactions[3], transactions)) == 2 / 5


def test_get_avg_amount_same_name(transactions) -> None:
    """Test that get_avg_amount_same_name returns the correct
    average amount of transactions with the same name."""
    assert pytest.approx(get_avg_amount_same_name(transactions[0], transactions)) == (100 + 100 + 200) / 3
    assert pytest.approx(get_avg_amount_same_name(transactions[3], transactions)) == (300 + 300) / 2


def test_get_std_amount_same_name(transactions) -> None:
    """Test that get_std_amount_same_name returns the correct standard deviation of
    amounts for transactions with the same name."""
    assert pytest.approx(get_std_amount_same_name(transactions[0], transactions)) == stdev([100, 100, 200])
    assert pytest.approx(get_std_amount_same_name(transactions[3], transactions)) == stdev([300, 300])


def test_get_n_transactions_same_month(transactions) -> None:
    """Test that get_n_transactions_same_month returns
      the correct number of transactions
    in the same month."""
    assert get_n_transactions_same_month(transactions[0], transactions) == 3
    assert get_n_transactions_same_month(transactions[3], transactions) == 2


def test_get_percent_transactions_same_month(transactions) -> None:
    """Test that get_percent_transactions_same_month returns the correct percentage
    of transactions in the same month."""
    assert pytest.approx(get_percent_transactions_same_month(transactions[0], transactions)) == 3 / 5
    assert pytest.approx(get_percent_transactions_same_month(transactions[3], transactions)) == 2 / 5


def test_get_avg_amount_same_month(transactions) -> None:
    """Test that get_avg_amount_same_month returns
    the correct average amount of
    transactions in the same month."""
    assert pytest.approx(get_avg_amount_same_month(transactions[0], transactions)) == (100 + 100 + 200) / 3
    assert pytest.approx(get_avg_amount_same_month(transactions[3], transactions)) == (300 + 300) / 2


def test_get_std_amount_same_month(transactions) -> None:
    """Test that get_std_amount_same_month returns the correct standard
    deviation of amounts for transactions in the same month."""
    assert pytest.approx(get_std_amount_same_month(transactions[0], transactions)) == stdev([100, 100, 200])
    assert pytest.approx(get_std_amount_same_month(transactions[3], transactions)) == stdev([300, 300])


def test_get_n_transactions_same_user_id(transactions) -> None:
    """Test that get_n_transactions_same_user_id returns the correct
    number of transactions with the same user_id."""
    assert get_n_transactions_same_user_id(transactions[0], transactions) == 3
    assert get_n_transactions_same_user_id(transactions[3], transactions) == 2


def test_get_percent_transactions_same_user_id(transactions) -> None:
    """Test that get_percent_transactions_same_user_id returns the
    correct percentage of transactions with the same user_id."""
    assert pytest.approx(get_percent_transactions_same_user_id(transactions[0], transactions)) == 3 / 5
    assert pytest.approx(get_percent_transactions_same_user_id(transactions[3], transactions)) == 2 / 5


def test_get_percent_transactions_same_day_of_week(transactions) -> None:
    """Test that get_percent_transactions_same_day_of_week returns
    the correct percentage of transactions on the same day of the week."""
    assert pytest.approx(get_percent_transactions_same_day_of_week(transactions[0], transactions)) == 1 / 5
    assert pytest.approx(get_percent_transactions_same_day_of_week(transactions[2], transactions)) == 1 / 5


def test_get_avg_amount_same_day_of_week(transactions) -> None:
    """Test that get_avg_amount_same_day_of_week returns the
    correct average amount of transactions on the same day of the week."""
    assert pytest.approx(get_avg_amount_same_day_of_week(transactions[0], transactions)) == (100 + 100) / 2
    assert pytest.approx(get_avg_amount_same_day_of_week(transactions[2], transactions)) == 200


def test_get_std_amount_same_day_of_week(transactions) -> None:
    """Test that get_std_amount_same_day_of_week returns the correct standard
    deviation of amounts for transactions on the same day of the week."""
    assert pytest.approx(get_std_amount_same_day_of_week(transactions[0], transactions)) == stdev([100, 100])
    assert pytest.approx(get_std_amount_same_day_of_week(transactions[2], transactions)) == 0.0


def test_get_n_transactions_within_amount_range(transactions) -> None:
    """Test that get_n_transactions_within_amount_range returns the correct
    number of transactions within a certain amount range."""
    assert get_n_transactions_within_amount_range(transactions[0], transactions, 0.1) == 2
    assert get_n_transactions_within_amount_range(transactions[2], transactions, 0.1) == 1


def test_get_percent_transactions_within_amount_range(transactions) -> None:
    """Test that get_percent_transactions_within_amount_range returns
    the correct percentage of transactions within a certain amount range."""
    assert pytest.approx(get_percent_transactions_within_amount_range(transactions[0], transactions, 0.1)) == 2 / 5
    assert pytest.approx(get_percent_transactions_within_amount_range(transactions[2], transactions, 0.1)) == 1 / 5


def test_get_avg_time_between_transactions(transactions) -> None:
    """Test that get_avg_time_between_transactions returns the correct average time between transactions."""
    result = get_avg_time_between_transactions(transactions[0], transactions)
    assert pytest.approx(result) == 1.0  # Assuming 1 day between transactions


def test_get_is_recurring(transactions) -> None:
    """Test that get_is_recurring correctly identifies recurring transactions."""
    result = get_is_recurring(transactions[0], transactions)
    assert result == 1  # Assuming the transaction is recurring


def test_get_median_amount_same_name(transactions) -> None:
    """Test that get_median_amount_same_name returns the correct median amount for transactions with the same name."""
    result = get_median_amount_same_name(transactions[0], transactions)
    assert pytest.approx(result) == 100  # Assuming the median is 100


def test_get_day_of_week(transactions) -> None:
    """Test that get_day_of_week returns the correct day of the week for a transaction."""
    result = get_day_of_week(transactions[0])
    assert result == 0  # Assuming the transaction occurred on a Monday


def test_get_is_weekend(transactions) -> None:
    """Test that get_is_weekend correctly identifies if a transaction occurred on a weekend."""
    result = get_is_weekend(transactions[0])
    assert result == 0  # Assuming the transaction did not occur on a weekend


if __name__ == "__main__":
    pytest.main()
