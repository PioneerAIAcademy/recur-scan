import pytest

from recur_scan.features_samuel import (
    get_amount_above_mean,
    get_amount_decimal_places,
    get_amount_difference_from_mode,
    get_amount_equal_previous,
    get_amount_round,
    get_average_days_between_transactions,
    get_contains_subscription_keywords,
    get_days_since_last_transaction,
    get_days_until_next_transaction,
    get_has_digits_in_name,
    get_is_first_half_month,
    get_is_fixed_amount,
    get_is_last_day_of_week,
    get_is_month_end,
    get_most_common_amount,
    get_name_length,
    get_name_token_count,
    get_transaction_amount_percentile,
    get_transaction_count_last_90_days,
    get_transaction_date_is_first,
    get_transaction_date_is_last,
    get_transaction_day,
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
    # The current implementation checks against the immediate previous transaction
    # regardless of amount, so we'll adjust our expectations
    assert get_amount_equal_previous(sample_transactions[1], sample_transactions) is True  # matches [0]
    assert get_amount_equal_previous(sample_transactions[2], sample_transactions) is False  # doesn't match [1]
    assert get_amount_equal_previous(sample_transactions[3], sample_transactions) is False  # doesn't match [2]


def test_get_name_token_count(sample_transactions):
    assert get_name_token_count(sample_transactions[0]) == 1


def test_get_has_digits_in_name(sample_transactions):
    transaction_with_digits = Transaction(id=5, user_id="user1", name="Spotify 2024", amount=10.0, date="2024-01-01")
    assert get_has_digits_in_name(transaction_with_digits) is True
    assert get_has_digits_in_name(sample_transactions[0]) is False


def test_get_average_days_between_transactions(sample_transactions):
    result = get_average_days_between_transactions(sample_transactions[0], sample_transactions)
    assert round(result, 2) == 20.0  # (30 + 29 + 1) / 3 = 20.0 days


def test_get_transaction_count_last_90_days(sample_transactions):
    # Current implementation includes the current transaction in the count
    assert get_transaction_count_last_90_days(sample_transactions[3], sample_transactions) == 4
    assert get_transaction_count_last_90_days(sample_transactions[1], sample_transactions) == 2


def test_get_is_last_day_of_week():
    sunday_txn = Transaction(
        id=1,
        user_id="user1",
        name="Spotify",
        amount=10,
        date="2024-03-24",  # Sunday
    )
    monday_txn = Transaction(
        id=2,
        user_id="user1",
        name="Spotify",
        amount=10,
        date="2024-03-25",  # Monday
    )
    assert get_is_last_day_of_week(sunday_txn) is True
    assert get_is_last_day_of_week(monday_txn) is False


def test_get_amount_round():
    txn1 = Transaction(id=1, user_id="user1", name="Spotify", amount=10.0, date="2024-01-01")
    txn2 = Transaction(id=2, user_id="user1", name="Spotify", amount=10.55, date="2024-01-01")
    assert get_amount_round(txn1) is True
    assert get_amount_round(txn2) is False


def test_get_amount_decimal_places():
    txn1 = Transaction(id=1, user_id="user1", name="Spotify", amount=10.99, date="2024-01-01")
    txn2 = Transaction(id=2, user_id="user1", name="Spotify", amount=10.0, date="2024-01-01")
    assert get_amount_decimal_places(txn1) == 2
    assert get_amount_decimal_places(txn2) == 1


def test_get_contains_subscription_keywords():
    sub_txn = Transaction(id=1, user_id="user1", name="Spotify Monthly Subscription", amount=10, date="2024-01-01")
    non_sub_txn = Transaction(id=2, user_id="user1", name="Random Store", amount=10, date="2024-01-01")
    assert get_contains_subscription_keywords(sub_txn) is True
    assert get_contains_subscription_keywords(non_sub_txn) is False


def test_get_is_fixed_amount():
    txns = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.0, date="2024-02-01"),
    ]
    assert get_is_fixed_amount(txns[0], txns) is True


def test_get_name_length():
    txn = Transaction(id=1, user_id="user1", name="Spotify Premium", amount=10, date="2024-01-01")
    assert get_name_length(txn) == len("Spotify Premium")


def test_get_most_common_amount(sample_transactions):
    assert get_most_common_amount(sample_transactions[0], sample_transactions) == 10.0


def test_get_amount_difference_from_mode(sample_transactions):
    assert get_amount_difference_from_mode(sample_transactions[2], sample_transactions) == 2.0


def test_get_transaction_date_is_first(sample_transactions):
    assert get_transaction_date_is_first(sample_transactions[0], sample_transactions) is True


def test_get_transaction_date_is_last(sample_transactions):
    assert get_transaction_date_is_last(sample_transactions[3], sample_transactions) is True


def test_get_transaction_name_word_frequency(sample_transactions):
    freq = get_transaction_name_word_frequency(sample_transactions[0], sample_transactions)
    assert 0 <= freq <= 1


def test_get_transaction_amount_percentile(sample_transactions):
    percentile = get_transaction_amount_percentile(sample_transactions[2], sample_transactions)
    assert 0 <= percentile <= 1


def test_get_transaction_name_is_upper():
    txn_upper = Transaction(id=1, user_id="user1", name="SPOTIFY", amount=10, date="2024-01-01")
    txn_mixed = Transaction(id=2, user_id="user1", name="Spotify Premium", amount=10, date="2024-01-01")
    assert get_transaction_name_is_upper(txn_upper) is True
    assert get_transaction_name_is_upper(txn_mixed) is False


def test_get_transaction_name_is_title_case():
    txn_title = Transaction(id=1, user_id="user1", name="Spotify Premium", amount=10, date="2024-01-01")
    txn_lower = Transaction(id=2, user_id="user1", name="spotify premium", amount=10, date="2024-01-01")
    assert get_transaction_name_is_title_case(txn_title) is True
    assert get_transaction_name_is_title_case(txn_lower) is False


def test_get_days_since_last_transaction(sample_transactions):
    assert get_days_since_last_transaction(sample_transactions[1], sample_transactions) == 30


def test_get_days_until_next_transaction(sample_transactions):
    assert get_days_until_next_transaction(sample_transactions[1], sample_transactions) == 29
