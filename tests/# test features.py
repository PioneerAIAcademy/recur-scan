# test features
import pytest

from recur_scan.features import (
    get_ends_in_99,
    get_ends_in_99_at,
    get_is_always_recurring,
    get_is_always_recurring_at,
    get_is_communication_or_energy_at,
    get_is_insurance,
    get_is_insurance_at,
    get_is_phone,
    get_is_phone_at,
    get_is_utility,
    get_is_utility_at,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_percent_transactions_same_amount,
    is_recurring_allowance_at,
    is_recurring_core_at,
    normalize_vendor_name_at,
    preprocess_transactions_at,
)
from recur_scan.transactions import Transaction


@pytest.fixture
def transactions():
    """Fixture providing test transactions."""
    return [
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"),
        Transaction(id=5, user_id="user1", name="Netflix", amount=15.99, date="2024-04-01"),
        Transaction(id=6, user_id="user1", name="Allstate Insurance", amount=100, date="2024-02-01"),
        Transaction(id=7, user_id="user1", name="T-Mobile", amount=75.99, date="2024-01-15"),
    ]


def test_get_n_transactions_same_amount(transactions) -> None:
    """Test that get_n_transactions_same_amount returns the correct number of transactions with the same amount."""
    assert get_n_transactions_same_amount(transactions[0], transactions) == 3  # Three 100s
    assert get_n_transactions_same_amount(transactions[2], transactions) == 1  # One 200


def test_get_percent_transactions_same_amount(transactions) -> None:
    """Test that get_percent_transactions_same_amount returns correct percentage."""
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 3 / 7  # 3 out of 7


def test_get_ends_in_99(transactions) -> None:
    """Test that get_ends_in_99 returns True for amounts ending in 99."""
    assert not get_ends_in_99(transactions[0])  # 100
    assert get_ends_in_99(transactions[3])  # 15.99
    assert get_ends_in_99(transactions[6])  # 75.99


def test_get_n_transactions_same_day(transactions) -> None:
    """Test that get_n_transactions_same_day returns the correct number of transactions on the same day of month."""
    assert get_n_transactions_same_day(transactions[0], transactions, 0) == 2  # Two on day 1 (Allstate and AT&T)
    assert get_n_transactions_same_day(transactions[0], transactions, 1) == 3  # Includes day 2 transaction
    assert get_n_transactions_same_day(transactions[2], transactions, 0) == 1  # One on day 2


def test_get_n_transactions_days_apart() -> None:
    """Test get_n_transactions_days_apart."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),  # Reference
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),  # 1 day (should not match)
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),  # 13 days (14-1)
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),  # 14 days (exact)
        Transaction(id=5, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),  # 15 days (14+1)
    ]
    # With 0 variance, only exact multiples
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 0) == 1  # Only Jan 15

    # With 1 day variance, should match Jan 14, 15, and 16 (3 transactions)
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 1) == 3


def test_get_is_insurance(transactions) -> None:
    """Test get_is_insurance."""
    assert get_is_insurance(transactions[0])  # "Allstate Insurance"
    assert not get_is_insurance(transactions[1])  # "AT&T"


def test_get_is_phone(transactions) -> None:
    """Test get_is_phone."""
    assert get_is_phone(transactions[1])  # "AT&T"
    assert get_is_phone(transactions[6])  # "T-Mobile"
    assert not get_is_phone(transactions[2])  # "Duke Energy"


def test_get_is_utility(transactions) -> None:
    """Test get_is_utility."""
    assert get_is_utility(transactions[2])  # "Duke Energy"
    assert not get_is_utility(transactions[3])  # "Netflix"


def test_get_is_always_recurring(transactions) -> None:
    """Test get_is_always_recurring."""
    assert not get_is_always_recurring(transactions[0])  # "Allstate Insurance"
    assert get_is_always_recurring(transactions[3])  # "Netflix"
    assert get_is_always_recurring(transactions[6])  # "T-Mobile"


def test_get_ends_in_99_at(transactions) -> None:
    """Test that get_ends_in_99_at returns True for amounts ending in 99."""
    assert not get_ends_in_99_at(transactions[0])  # 100
    assert get_ends_in_99_at(transactions[3])  # 15.99
    assert get_ends_in_99_at(transactions[6])  # 75.99


def test_get_is_insurance_at(transactions) -> None:
    """Test get_is_insurance_at."""
    assert get_is_insurance_at(transactions[0])  # "Allstate Insurance"
    assert not get_is_insurance_at(transactions[1])  # "AT&T"


def test_get_is_phone_at(transactions) -> None:
    """Test get_is_phone_at."""
    assert get_is_phone_at(transactions[1])  # "AT&T"
    assert get_is_phone_at(transactions[6])  # "T-Mobile"
    assert not get_is_phone_at(transactions[2])  # "Duke Energy"


def test_get_is_utility_at(transactions) -> None:
    """Test get_is_utility_at."""
    assert get_is_utility_at(transactions[2])  # "Duke Energy"
    assert not get_is_utility_at(transactions[3])  # "Netflix"


def test_get_is_communication_or_energy_at(transactions) -> None:
    """Test get_is_communication_or_energy_at."""
    assert get_is_communication_or_energy_at(transactions[1])  # "AT&T" is phone
    assert get_is_communication_or_energy_at(transactions[2])  # "Duke Energy" is utility
    assert get_is_communication_or_energy_at(transactions[6])  # "T-Mobile" is phone
    assert not get_is_communication_or_energy_at(transactions[0])  # "Allstate Insurance"


def test_get_is_always_recurring_at(transactions) -> None:
    """Test get_is_always_recurring_at."""
    assert not get_is_always_recurring_at(transactions[0])  # "Allstate Insurance"
    assert get_is_always_recurring_at(transactions[3])  # "Netflix"
    assert get_is_always_recurring_at(transactions[6])  # "T-Mobile"


def test_normalize_vendor_name_at() -> None:
    """Test normalize_vendor_name_at."""
    assert normalize_vendor_name_at("AT&T Wireless") == "at&t"
    assert normalize_vendor_name_at("Netflix.com") == "netflix"
    assert normalize_vendor_name_at("Random Store") == "randomstore"


def test_is_recurring_core_at(transactions) -> None:
    """Test is_recurring_core_at for monthly recurrence."""
    preprocessed = preprocess_transactions_at(transactions)
    vendor_txns = preprocessed["by_vendor"][normalize_vendor_name_at("Netflix")]
    assert is_recurring_core_at(
        transactions[3], vendor_txns, preprocessed, interval=30, variance=4, min_occurrences=2
    )  # Netflix monthly
    vendor_txns = preprocessed["by_vendor"][normalize_vendor_name_at("Allstate Insurance")]
    assert is_recurring_core_at(
        transactions[0], vendor_txns, preprocessed, interval=30, variance=4, min_occurrences=2
    )  # Allstate recurring


def test_is_recurring_allowance_at(transactions) -> None:
    """Test is_recurring_allowance_at for monthly recurrence with tolerance."""
    assert is_recurring_allowance_at(
        transactions[3], transactions, expected_interval=30, allowance=2, min_occurrences=2
    )  # Netflix monthly
    assert is_recurring_allowance_at(
        transactions[0], transactions, expected_interval=30, allowance=2, min_occurrences=2
    )  # Allstate recurring
