import pandas as pd
import pytest

from recur_scan.features_elliot import (
    amount_similarity,
    amount_variability_ratio,
    get_is_always_recurring,
    get_is_near_same_amount,
    get_time_regularity_score,
    get_transaction_amount_variance,
    get_transaction_similarity,
    is_auto_pay,
    is_membership,
    is_price_trending,
    is_recurring_based_on_99,
    is_split_transaction,
    is_utility_bill,
    is_weekday_transaction,
    most_common_interval,
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

    # NEW FEATURES TESTS

    def test_get_time_regularity_score():
        """Test get_time_regularity_score function."""
        txns = [
            {"name": "Spotify", "date": "2024-01-01"},
            {"name": "Spotify", "date": "2024-01-08"},  # 7 days later
            {"name": "Spotify", "date": "2024-01-15"},  # 7 days later
            {"name": "Netflix", "date": "2024-01-01"},  # Different vendor
        ]
        txn = {"name": "Spotify", "date": "2024-01-01"}

        # Case 1: Regular intervals (7 days)
        assert get_time_regularity_score(txn, txns) > 0.5

        # Case 2: Irregular intervals
        irregular_txns = [
            {"name": "Spotify", "date": "2024-01-01"},
            {"name": "Spotify", "date": "2024-01-10"},  # 9 days later
            {"name": "Spotify", "date": "2024-01-20"},  # 10 days later
        ]
        assert get_time_regularity_score(txn, irregular_txns) < 0.5

        # Case 3: Not enough transactions
        small_txns = [{"name": "Spotify", "date": "2024-01-01"}]
        assert get_time_regularity_score(txn, small_txns) == 0.0

    def test_get_transaction_amount_variance():
        """Test get_transaction_amount_variance function."""
        txns = [
            {"name": "Spotify", "amount": 9.99},
            {"name": "Spotify", "amount": 10.99},
            {"name": "Spotify", "amount": 11.99},
            {"name": "Netflix", "amount": 15.99},  # Different vendor
        ]
        txn = {"name": "Spotify", "amount": 9.99}

        # Case 1: Variance exists
        assert get_transaction_amount_variance(txn, txns) > 0.0

        # Case 2: No variance (all amounts are the same)
        uniform_txns = [
            {"name": "Spotify", "amount": 9.99},
            {"name": "Spotify", "amount": 9.99},
            {"name": "Spotify", "amount": 9.99},
        ]
        assert get_transaction_amount_variance(txn, uniform_txns) == 0.0

        # Case 3: Not enough transactions
        small_txns = [{"name": "Spotify", "amount": 9.99}]
        assert get_transaction_amount_variance(txn, small_txns) == 0.0

    def test_most_common_interval():
        """Test most_common_interval function."""
        data = {
            "date": ["2024-01-01", "2024-01-08", "2024-01-15", "2024-01-22"],  # 7-day intervals
            "amount": [9.99, 9.99, 9.99, 9.99],
        }
        df = pd.DataFrame(data)

        # Case 1: Regular intervals
        assert most_common_interval(df) == 7

        # Case 2: Irregular intervals
        data_irregular = {
            "date": ["2024-01-01", "2024-01-10", "2024-01-20"],  # 9 and 10-day intervals
            "amount": [9.99, 9.99, 9.99],
        }
        df_irregular = pd.DataFrame(data_irregular)
        assert most_common_interval(df_irregular) == 9

        # Case 3: Single transaction
        data_single = {"date": ["2024-01-01"], "amount": [9.99]}
        df_single = pd.DataFrame(data_single)
        assert most_common_interval(df_single) == 0

    def test_amount_variability_ratio():
        """Test amount_variability_ratio function."""
        data = {"amount": [9.99, 10.99, 11.99, 12.99]}
        df = pd.DataFrame(data)

        # Case 1: Variability exists
        assert amount_variability_ratio(df) > 0.0

        # Case 2: No variability (all amounts are the same)
        data_uniform = {"amount": [9.99, 9.99, 9.99]}
        df_uniform = pd.DataFrame(data_uniform)
        assert amount_variability_ratio(df_uniform) == 0.0

        # Case 3: Empty DataFrame
        df_empty = pd.DataFrame({"amount": []})
        assert amount_variability_ratio(df_empty) == 0.0

    def test_amount_similarity():
        """Test amount_similarity function."""
        data = {"amount": [9.99, 10.00, 10.01, 10.02]}  # Close to the mean
        df = pd.DataFrame(data)

        # Case 1: High similarity
        assert amount_similarity(df, tolerance=0.1) > 0.75

        # Case 2: Low similarity
        data_dissimilar = {"amount": [9.99, 20.00, 30.00, 40.00]}  # Far from the mean
        df_dissimilar = pd.DataFrame(data_dissimilar)
        assert amount_similarity(df_dissimilar, tolerance=0.1) < 0.5

        # Case 3: Empty DataFrame
        df_empty = pd.DataFrame({"amount": []})
        assert amount_similarity(df_empty) == 0.0

    def parse_date(date_str):
        """Parse a date string into a datetime object."""
        from datetime import datetime

        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%m/%d/%Y")
            except ValueError:
                try:
                    return datetime.strptime(date_str, "%B %d, %Y")
                except ValueError:
                    return None

    def test_parse_date():
        """Test parse_date function."""
        from datetime import datetime

        # Valid date strings
        assert parse_date("2024-01-01") == datetime(2024, 1, 1)
        assert parse_date("01/01/2024") == datetime(2024, 1, 1)
        assert parse_date("January 1, 2024") == datetime(2024, 1, 1)

        # Invalid date strings
        assert parse_date("invalid-date") is None
        assert parse_date("") is None
        assert parse_date(None) is None
