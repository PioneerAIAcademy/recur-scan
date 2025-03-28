# test features
import pytest

from recur_scan.features import (
    get_average_transaction_amount,
    # get_day_of_week,
    get_ends_in_99,
    get_is_always_recurring,
    get_is_biweekly,
    get_is_fixed_amount,
    get_is_high_frequency_vendor,
    get_is_insurance,
    # get_is_large_amount,
    get_is_monthly,
    get_is_phone,
    get_is_quarterly,
    get_is_recurring_vendor,
    # get_is_recurring_based_on_frequency,
    get_is_round_amount,
    get_is_same_day_of_month,
    get_is_small_amount,
    get_is_subscription_based,
    get_is_utility,
    get_is_weekend_transaction,
    get_is_weekly,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
    get_recurring_interval_score,
    get_transaction_frequency,
    # get_quarter_of_year,
    # get_time_of_month,
    # get_transaction_gap_stats,
    get_vendor_amount_variance,
    # get_vendor_name_similarity,
    # get_vendor_popularity,
    get_vendor_transaction_count,
)
from recur_scan.transactions import Transaction


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


# started adding my features here


def test_get_is_weekly() -> None:
    """Test get_is_weekly."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-01-08"),
        Transaction(id=3, user_id="user1", name="name1", amount=10, date="2024-01-15"),
    ]
    assert get_is_weekly(transactions[0], transactions)
    assert not get_is_weekly(transactions[0], [transactions[0]])


def test_get_is_monthly() -> None:
    """Test get_is_monthly."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=10, date="2024-03-01"),
    ]
    assert get_is_monthly(transactions[0], transactions)
    assert not get_is_monthly(transactions[0], [transactions[0]])


def test_get_is_biweekly() -> None:
    """Test get_is_biweekly."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-01-15"),
        Transaction(id=3, user_id="user1", name="name1", amount=10, date="2024-01-29"),
    ]
    assert get_is_biweekly(transactions[0], transactions)
    assert not get_is_biweekly(transactions[0], [transactions[0]])


def test_get_vendor_transaction_count() -> None:
    """Test get_vendor_transaction_count."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=20, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name2", amount=30, date="2024-01-03"),
    ]
    assert get_vendor_transaction_count(transactions[0], transactions) == 2
    assert get_vendor_transaction_count(transactions[2], transactions) == 1


def test_get_vendor_amount_variance() -> None:
    """Test get_vendor_amount_variance."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=20, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=30, date="2024-01-03"),
    ]
    assert pytest.approx(get_vendor_amount_variance(transactions[0], transactions)) == 66.6667


def test_get_is_round_amount() -> None:
    """Test get_is_round_amount."""
    assert get_is_round_amount(Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"))
    assert not get_is_round_amount(Transaction(id=2, user_id="user1", name="name1", amount=10.99, date="2024-01-02"))


def test_get_is_small_amount() -> None:
    """Test get_is_small_amount."""
    assert get_is_small_amount(Transaction(id=1, user_id="user1", name="name1", amount=5, date="2024-01-01"))
    assert not get_is_small_amount(Transaction(id=2, user_id="user1", name="name1", amount=15, date="2024-01-02"))


def test_get_transaction_frequency() -> None:
    """Test get_transaction_frequency."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-01-08"),
        Transaction(id=3, user_id="user1", name="name1", amount=10, date="2024-01-15"),
    ]
    assert pytest.approx(get_transaction_frequency(transactions[0], transactions)) == 7.0

    transactions_single = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
    ]
    assert get_transaction_frequency(transactions_single[0], transactions_single) == 0.0


def test_get_is_quarterly() -> None:
    """Test get_is_quarterly."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-04-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=10, date="2024-07-01"),
    ]
    assert get_is_quarterly(transactions[0], transactions)
    assert not get_is_quarterly(transactions[0], [transactions[0]])


def test_get_average_transaction_amount() -> None:
    """Test get_average_transaction_amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=20, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=30, date="2024-01-03"),
    ]
    assert pytest.approx(get_average_transaction_amount(transactions[0], transactions)) == 20.0

    transactions_empty = []
    assert (
        get_average_transaction_amount(
            Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
            transactions_empty,
        )
        == 0.0
    )


def test_get_is_subscription_based() -> None:
    """Test get_is_subscription_based."""
    assert get_is_subscription_based(
        Transaction(
            id=1,
            user_id="user1",
            name="Netflix Subscription",
            amount=10,
            date="2024-01-01",
        )
    )
    assert not get_is_subscription_based(
        Transaction(
            id=2,
            user_id="user1",
            name="Grocery Store",
            amount=50,
            date="2024-01-02",
        )
    )


def test_get_is_recurring_vendor() -> None:
    """Test get_is_recurring_vendor."""
    assert get_is_recurring_vendor(
        Transaction(
            id=1,
            user_id="user1",
            name="Netflix",
            amount=10,
            date="2024-01-01",
        )
    )
    assert not get_is_recurring_vendor(
        Transaction(
            id=2,
            user_id="user1",
            name="Grocery Store",
            amount=50,
            date="2024-01-02",
        )
    )


def test_get_is_fixed_amount() -> None:
    """Test get_is_fixed_amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-01-08"),
    ]
    assert get_is_fixed_amount(transactions[0], transactions)

    transactions_varied = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=20, date="2024-01-08"),
    ]
    assert not get_is_fixed_amount(transactions_varied[0], transactions_varied)


def test_get_recurring_interval_score() -> None:
    """Test get_recurring_interval_score."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-01-08"),
        Transaction(id=3, user_id="user1", name="name1", amount=10, date="2024-01-15"),
    ]
    assert pytest.approx(get_recurring_interval_score(transactions[0], transactions)) == 0.0

    transactions_varied = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-01-10"),
        Transaction(id=3, user_id="user1", name="name1", amount=10, date="2024-01-20"),
    ]
    assert get_recurring_interval_score(transactions_varied[0], transactions_varied) > 0.0


def test_get_is_weekend_transaction() -> None:
    """Test get_is_weekend_transaction."""
    assert get_is_weekend_transaction(
        Transaction(
            id=1,
            user_id="user1",
            name="name1",
            amount=10,
            date="2024-01-06",
        )
    )  # Sunday
    assert not get_is_weekend_transaction(
        Transaction(
            id=2,
            user_id="user1",
            name="name1",
            amount=10,
            date="2024-01-05",
        )
    )  # Friday


def test_get_is_high_frequency_vendor() -> None:
    """Test get_is_high_frequency_vendor."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=10, date="2024-01-03"),
    ]
    assert get_is_high_frequency_vendor(transactions[0], transactions)

    transactions_low_frequency = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-01-15"),
    ]
    assert not get_is_high_frequency_vendor(transactions_low_frequency[0], transactions_low_frequency)


def test_get_is_same_day_of_month() -> None:
    """Test get_is_same_day_of_month."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=10, date="2024-03-01"),
    ]
    assert get_is_same_day_of_month(transactions[0], transactions)

    transactions_varied_days = [
        Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-02-02"),
    ]
    assert not get_is_same_day_of_month(transactions_varied_days[0], transactions_varied_days)


# Commenting out less important features and their tests

# def test_get_vendor_name_similarity() -> None:
#     """Test get_vendor_name_similarity."""
#     transactions = [
#         Transaction(id=1, user_id="user1", name="7-Eleven", amount=10, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="7 Eleven", amount=20, date="2024-01-02"),
#         Transaction(id=3, user_id="user1", name="Walmart", amount=30, date="2024-01-03"),
#     ]
#     assert pytest.approx(get_vendor_name_similarity(transactions[0], transactions)) == 1.0

# def test_get_vendor_popularity() -> None:
#     """Test get_vendor_popularity."""
#     transactions = [
#         Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user2", name="name1", amount=100, date="2024-01-02"),
#         Transaction(id=3, user_id="user3", name="name1", amount=100, date="2024-01-03"),
#     ]
#     assert get_vendor_popularity(transactions[0], transactions) == 3

# def test_get_time_of_month() -> None:
#     """Test get_time_of_month."""
#     transaction_early = Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-05")
#     transaction_mid = Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-15")
#     transaction_late = Transaction(id=3, user_id="user1", name="name1", amount=100, date="2024-01-25")
#     assert get_time_of_month(transaction_early) == "early"
#     assert get_time_of_month(transaction_mid) == "mid"
#     assert get_time_of_month(transaction_late) == "late"

# def test_get_quarter_of_year() -> None:
#     """Test get_quarter_of_year."""
#     transaction_q1 = Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01")
#     transaction_q2 = Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-04-01")
#     transaction_q3 = Transaction(id=3, user_id="user1", name="name1", amount=100, date="2024-07-01")
#     transaction_q4 = Transaction(id=4, user_id="user1", name="name1", amount=100, date="2024-10-01")
#     assert get_quarter_of_year(transaction_q1) == 1
#     assert get_quarter_of_year(transaction_q2) == 2
#     assert get_quarter_of_year(transaction_q3) == 3
#     assert get_quarter_of_year(transaction_q4) == 4

# def test_get_day_of_week() -> None:
#     """Test get_day_of_week."""
#     transaction = Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01")  # Monday
#     assert get_day_of_week(transaction) == 0

# def test_get_is_large_amount() -> None:
#     """Test get_is_large_amount."""
#     assert get_is_large_amount(Transaction(id=1, user_id="user1", name="name1", amount=150, date="2024-01-01"))
#     assert not get_is_large_amount(Transaction(id=2, user_id="user1", name="name1", amount=50, date="2024-01-02"))

# def test_get_is_recurring_based_on_frequency() -> None:
#     """Test get_is_recurring_based_on_frequency."""
#     transactions = [
#         Transaction(id=1, user_id="user1", name="name1", amount=10, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="name1", amount=10, date="2024-01-08"),
#         Transaction(id=3, user_id="user1", name="name1", amount=10, date="2024-01-15"),
#         Transaction(id=4, user_id="user1", name="name1", amount=10, date="2024-01-22"),
#     ]
#     assert get_is_recurring_based_on_frequency(transactions[0], transactions)
#     assert not get_is_recurring_based_on_frequency(transactions[0], [transactions[0]])
