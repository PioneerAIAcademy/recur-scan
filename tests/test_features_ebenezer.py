from statistics import stdev

import pytest

from recur_scan.features_ebenezer import (
    get_avg_amount_same_day_of_week,
    get_avg_amount_same_month,
    get_avg_amount_same_name,
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
    """Test that get_n_transactions_same_name returns the correct number of transactions with the same name."""
    assert get_n_transactions_same_name(transactions[0], transactions) == 3
    assert get_n_transactions_same_name(transactions[3], transactions) == 2


def test_get_percent_transactions_same_name(transactions) -> None:
    """Test that get_percent_transactions_same_name returns the correct percentage of transactions with the same
    name."""
    assert pytest.approx(get_percent_transactions_same_name(transactions[0], transactions)) == 3 / 5
    assert pytest.approx(get_percent_transactions_same_name(transactions[3], transactions)) == 2 / 5


def test_get_avg_amount_same_name(transactions) -> None:
    """Test that get_avg_amount_same_name returns the correct average amount of transactions with the same name."""
    assert pytest.approx(get_avg_amount_same_name(transactions[0], transactions)) == (100 + 100 + 200) / 3
    assert pytest.approx(get_avg_amount_same_name(transactions[3], transactions)) == (300 + 300) / 2


def test_get_std_amount_same_name(transactions) -> None:
    """Test that get_std_amount_same_name returns the correct standard deviation of amounts for transactions with the
    same name."""
    assert pytest.approx(get_std_amount_same_name(transactions[0], transactions)) == stdev([100, 100, 200])
    assert pytest.approx(get_std_amount_same_name(transactions[3], transactions)) == stdev([300, 300])


def test_get_n_transactions_same_month(transactions) -> None:
    """Test that get_n_transactions_same_month returns the correct number of transactions in the same month."""
    assert get_n_transactions_same_month(transactions[0], transactions) == 3
    assert get_n_transactions_same_month(transactions[3], transactions) == 2


def test_get_percent_transactions_same_month(transactions) -> None:
    """Test that get_percent_transactions_same_month returns the correct percentage of transactions in the same
    month."""
    assert pytest.approx(get_percent_transactions_same_month(transactions[0], transactions)) == 3 / 5
    assert pytest.approx(get_percent_transactions_same_month(transactions[3], transactions)) == 2 / 5


def test_get_avg_amount_same_month(transactions) -> None:
    """Test that get_avg_amount_same_month returns the correct average amount of transactions in the same month."""
    assert pytest.approx(get_avg_amount_same_month(transactions[0], transactions)) == (100 + 100 + 200) / 3
    assert pytest.approx(get_avg_amount_same_month(transactions[3], transactions)) == (300 + 300) / 2


def test_get_std_amount_same_month(transactions) -> None:
    """Test that get_std_amount_same_month returns the correct standard deviation of amounts for transactions in the
    same month."""
    assert pytest.approx(get_std_amount_same_month(transactions[0], transactions)) == stdev([100, 100, 200])
    assert pytest.approx(get_std_amount_same_month(transactions[3], transactions)) == stdev([300, 300])


def test_get_n_transactions_same_user_id(transactions) -> None:
    """Test that get_n_transactions_same_user_id returns the correct number of transactions with the same user_id."""
    assert get_n_transactions_same_user_id(transactions[0], transactions) == 3
    assert get_n_transactions_same_user_id(transactions[3], transactions) == 2


def test_get_percent_transactions_same_user_id(transactions) -> None:
    """Test that get_percent_transactions_same_user_id returns the correct percentage of transactions with the same
    user_id."""
    assert pytest.approx(get_percent_transactions_same_user_id(transactions[0], transactions)) == 3 / 5
    assert pytest.approx(get_percent_transactions_same_user_id(transactions[3], transactions)) == 2 / 5


def test_get_percent_transactions_same_day_of_week(transactions) -> None:
    """Test that get_percent_transactions_same_day_of_week returns the correct percentage of transactions on the same
    day of the week."""
    assert (
        pytest.approx(get_percent_transactions_same_day_of_week(transactions[0], transactions)) == 1 / 5
    )  # Corrected expected value
    assert (
        pytest.approx(get_percent_transactions_same_day_of_week(transactions[2], transactions)) == 1 / 5
    )  # Corrected expected value


def test_get_avg_amount_same_day_of_week(transactions) -> None:
    """Test that get_avg_amount_same_day_of_week returns the correct average amount of transactions on the same day of
    the week."""
    assert pytest.approx(get_avg_amount_same_day_of_week(transactions[0], transactions)) == (100 + 100) / 2
    assert pytest.approx(get_avg_amount_same_day_of_week(transactions[2], transactions)) == 200


def test_get_std_amount_same_day_of_week(transactions) -> None:
    """Test that get_std_amount_same_day_of_week returns the correct standard deviation of amounts for transactions on
    the same day of the week."""
    assert pytest.approx(get_std_amount_same_day_of_week(transactions[0], transactions)) == stdev([100, 100])
    assert pytest.approx(get_std_amount_same_day_of_week(transactions[2], transactions)) == 0.0


def test_get_n_transactions_within_amount_range(transactions) -> None:
    """Test that get_n_transactions_within_amount_range returns the correct number of transactions within a certain
    amount range."""
    assert get_n_transactions_within_amount_range(transactions[0], transactions, 0.1) == 2
    assert get_n_transactions_within_amount_range(transactions[2], transactions, 0.1) == 1


def test_get_percent_transactions_within_amount_range(transactions) -> None:
    """Test that get_percent_transactions_within_amount_range returns the correct percentage of transactions within a
    certain amount range."""
    assert pytest.approx(get_percent_transactions_within_amount_range(transactions[0], transactions, 0.1)) == 2 / 5
    assert pytest.approx(get_percent_transactions_within_amount_range(transactions[2], transactions, 0.1)) == 1 / 5


if __name__ == "_main_":
    pytest.main()
