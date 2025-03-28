import pytest

from recur_scan.features import (
    get_ends_in_99,
    get_features,
    get_is_always_recurring,
    get_is_insurance,
    get_is_near_same_amount,
    get_is_phone,
    get_is_utility,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
    is_auto_pay,
    is_membership,
    #    is_price_trending,  # Removed as it is an unknown import symbol
    is_recurring_based_on_99,
    is_split_transaction,
    is_utility_bill,
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


def test_get_n_transactions_days_apart(transactions) -> None:
    """Test get_n_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=5, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=6, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=7, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 0) == 1
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 1) == 3


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
    assert get_is_utility(transactions[2])
    assert not get_is_utility(transactions[3])


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


def test_get_features(transactions) -> None:
    """Test get_features."""
    features = get_features(transactions[0], transactions)
    assert features["n_transactions_same_amount"] == 2
    assert pytest.approx(features["percent_transactions_same_amount"]) == 2 / 7
    assert not features["ends_in_99"]
    assert features["amount"] == 100
    assert features["same_day_exact"] == 2
    assert features["same_day_off_by_1"] == 3
    assert features["same_day_off_by_2"] == 4
    assert features["7_days_apart_exact"] == 0
    assert features["14_days_apart_exact"] == 0
    assert features["30_days_apart_exact"] == 0
    assert features["90_days_apart_exact"] == 0
    assert features["is_insurance"]
    assert not features["is_utility"]
    assert not features["is_phone"]
    assert not features["is_always_recurring"]
    assert not features["is_auto_pay"]
    assert not features["is_membership"]


def test_is_recurring_based_on_99(transactions):
    """Test the is_recurring_based_on_99 function."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Spotify", amount=9.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Spotify", amount=9.99, date="2024-01-08"),
        Transaction(id=3, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"),
        Transaction(id=4, user_id="user1", name="Netflix", amount=14.99, date="2024-01-01"),
    ]
    assert is_recurring_based_on_99(transactions[0], transactions) is True
    assert is_recurring_based_on_99(transactions[3], transactions) is False


def test_is_split_transaction():
    """Test is_split_transaction function."""
    all_transactions = [
        Transaction(id=1, user_id="user1", name="Laptop Payment", amount=1000, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Laptop Payment", amount=500, date="2024-01-10"),
        Transaction(id=3, user_id="user1", name="Laptop Payment", amount=500, date="2024-01-20"),
        Transaction(id=4, user_id="user1", name="Amazon", amount=100, date="2024-02-01"),
    ]
    assert is_split_transaction(all_transactions[0], all_transactions) is True
    assert is_split_transaction(all_transactions[3], all_transactions) is False


def test_is_utility_bill(transactions):
    """Test is_utility_bill function."""
    assert is_utility_bill(transactions[2]) is True
    assert is_utility_bill(transactions[3]) is False
    assert get_is_utility(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))
    assert not get_is_utility(
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03")
    )


# End of tests
