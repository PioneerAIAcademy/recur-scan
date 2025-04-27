import pytest

from recur_scan.features_samuel import (
    get_amount_above_mean,
    get_amount_decimal_places,
    get_amount_difference_from_mode,
    get_amount_equal_previous,
    get_amount_round,
    get_amount_std_dev,
    get_average_days_between_transactions,
    get_contains_subscription_keywords,
    get_days_since_last_transaction,
    get_days_until_next_transaction,
    get_has_digits_in_name,
    get_is_always_recurring,
    get_is_first_half_month,
    get_is_fixed_amount,
    get_is_last_day_of_week,
    get_is_month_end,
    get_is_weekend_transaction,
    get_median_transaction_amount,
    get_most_common_amount,
    get_name_length,
    get_name_token_count,
    get_transaction_amount_percentile,
    get_transaction_count_last_90_days,
    get_transaction_date_is_first,
    get_transaction_date_is_last,
    get_transaction_day,
    get_transaction_frequency,
    get_transaction_month,
    get_transaction_name_is_title_case,
    get_transaction_name_is_upper,
    get_transaction_name_word_frequency,
    get_transaction_weekday,
    get_transaction_year,
)
from recur_scan.transactions import Transaction


@pytest.fixture
def sample_transactions():
    return [
        Transaction(id=1, user_id="user1", name="Spotify", amount=10.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Spotify", amount=10.0, date="2024-01-31"),
        Transaction(id=3, user_id="user1", name="Spotify", amount=12.0, date="2024-02-29"),
        Transaction(id=4, user_id="user1", name="Spotify", amount=10.0, date="2024-03-01"),
    ]


def test_get_transaction_day(sample_transactions):
    assert get_transaction_day(sample_transactions[0]) == 1


def test_get_transaction_weekday(sample_transactions):
    assert get_transaction_weekday(sample_transactions[0]) == 0  # Monday


def test_get_transaction_month(sample_transactions):
    assert get_transaction_month(sample_transactions[1]) == 1


def test_get_transaction_year(sample_transactions):
    assert get_transaction_year(sample_transactions[2]) == 2024


def test_get_is_first_half_month(sample_transactions):
    assert get_is_first_half_month(sample_transactions[0]) is True
    assert get_is_first_half_month(sample_transactions[1]) is False


def test_get_is_month_end(sample_transactions):
    assert get_is_month_end(sample_transactions[1]) is True
    assert get_is_month_end(sample_transactions[0]) is False


def test_get_amount_above_mean(sample_transactions):
    assert get_amount_above_mean(sample_transactions[2], sample_transactions) is True
    assert get_amount_above_mean(sample_transactions[0], sample_transactions) is False


def test_get_amount_equal_previous(sample_transactions):
    assert get_amount_equal_previous(sample_transactions[1], sample_transactions) is True
    assert get_amount_equal_previous(sample_transactions[2], sample_transactions) is False
    assert get_amount_equal_previous(sample_transactions[3], sample_transactions) is False


def test_get_name_token_count(sample_transactions):
    assert get_name_token_count(sample_transactions[0]) == 1


def test_get_has_digits_in_name(sample_transactions):
    txn = Transaction(id=5, user_id="user1", name="Netflix 2024", amount=15.0, date="2024-04-01")
    assert get_has_digits_in_name(txn) is True
    assert get_has_digits_in_name(sample_transactions[0]) is False


def test_get_average_days_between_transactions(sample_transactions):
    assert get_average_days_between_transactions(sample_transactions[0], sample_transactions) > 0


def test_get_transaction_count_last_90_days(sample_transactions):
    assert get_transaction_count_last_90_days(sample_transactions[3], sample_transactions) >= 1


def test_get_is_last_day_of_week():
    txn = Transaction(id=6, user_id="user1", name="Spotify", amount=10.0, date="2024-03-31")  # Sunday
    assert get_is_last_day_of_week(txn) is True


def test_get_amount_round(sample_transactions):
    assert get_amount_round(sample_transactions[0]) is True


def test_get_amount_decimal_places(sample_transactions):
    txn = Transaction(id=7, user_id="user1", name="Spotify", amount=10.55, date="2024-04-01")
    assert get_amount_decimal_places(txn) == 2
    assert get_amount_decimal_places(sample_transactions[0]) == 1  # 10.0


def test_get_contains_subscription_keywords(sample_transactions):
    txn = Transaction(id=8, user_id="user1", name="Spotify Monthly", amount=10.0, date="2024-04-01")
    assert get_contains_subscription_keywords(txn) is True
    assert get_contains_subscription_keywords(sample_transactions[0]) is False


def test_get_is_fixed_amount(sample_transactions):
    assert get_is_fixed_amount(sample_transactions[0], sample_transactions) is False


def test_get_name_length(sample_transactions):
    assert get_name_length(sample_transactions[0]) == len("Spotify")


def test_get_most_common_amount(sample_transactions):
    assert get_most_common_amount(sample_transactions[0], sample_transactions) == 10.0


def test_get_amount_difference_from_mode(sample_transactions):
    assert get_amount_difference_from_mode(sample_transactions[2], sample_transactions) == 2.0


def test_get_transaction_date_is_first(sample_transactions):
    assert get_transaction_date_is_first(sample_transactions[0], sample_transactions) is True
    assert get_transaction_date_is_first(sample_transactions[1], sample_transactions) is False


def test_get_transaction_date_is_last(sample_transactions):
    assert get_transaction_date_is_last(sample_transactions[3], sample_transactions) is True
    assert get_transaction_date_is_last(sample_transactions[2], sample_transactions) is False


def test_get_transaction_name_word_frequency(sample_transactions):
    assert get_transaction_name_word_frequency(sample_transactions[0], sample_transactions) > 0


def test_get_transaction_amount_percentile(sample_transactions):
    assert 0.0 <= get_transaction_amount_percentile(sample_transactions[0], sample_transactions) <= 1.0


def test_get_transaction_name_is_upper(sample_transactions):
    txn = Transaction(id=9, user_id="user1", name="SPOTIFY", amount=10.0, date="2024-04-01")
    assert get_transaction_name_is_upper(txn) is True
    assert get_transaction_name_is_upper(sample_transactions[0]) is False


def test_get_transaction_name_is_title_case(sample_transactions):
    assert get_transaction_name_is_title_case(sample_transactions[0]) is True
    txn = Transaction(id=10, user_id="user1", name="spotify", amount=10.0, date="2024-04-01")
    assert get_transaction_name_is_title_case(txn) is False


def test_get_days_since_last_transaction(sample_transactions):
    assert get_days_since_last_transaction(sample_transactions[3], sample_transactions) >= 0


def test_get_days_until_next_transaction(sample_transactions):
    assert get_days_until_next_transaction(sample_transactions[0], sample_transactions) >= 0


def test_get_is_always_recurring(sample_transactions):
    # Pass a single transaction instead of the entire list
    assert isinstance(get_is_always_recurring(sample_transactions[0]), bool)
    assert isinstance(get_is_always_recurring(sample_transactions[1]), bool)
    assert isinstance(get_is_always_recurring(sample_transactions[2]), bool)


def test_get_transaction_frequency(sample_transactions):
    freq = get_transaction_frequency(sample_transactions[0], sample_transactions)
    assert freq is not None
    assert freq >= 0


def test_get_amount_std_dev(sample_transactions):
    std_dev = get_amount_std_dev(sample_transactions[0], sample_transactions)
    assert std_dev >= 0


def test_get_median_transaction_amount(sample_transactions):
    median = get_median_transaction_amount(sample_transactions[0], sample_transactions)
    assert median >= 0


def test_get_is_weekend_transaction():
    txn_weekend = Transaction(id=11, user_id="user1", name="Spotify", amount=10.0, date="2024-03-30")  # Saturday
    txn_weekday = Transaction(id=12, user_id="user1", name="Spotify", amount=10.0, date="2024-04-01")  # Monday
    assert get_is_weekend_transaction(txn_weekend) is True
    assert get_is_weekend_transaction(txn_weekday) is False
