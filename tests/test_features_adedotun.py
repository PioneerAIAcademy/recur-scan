# test features
import pytest

from recur_scan.features_adedotun import (
    compute_recurring_inputs_at,  # Add missing import
    get_is_always_recurring_at,
    get_is_communication_or_energy_at,
    get_is_insurance_at,
    get_is_phone_at,
    get_is_utility_at,
    get_n_transactions_same_amount_at,
    get_percent_transactions_same_amount_tolerant,
    is_recurring_allowance_at,
    is_recurring_core_at,
    normalize_vendor_name,  # Add import
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
    ]


def test_get_n_transactions_same_amount_at() -> None:
    """Test that get_n_transactions_same_amount_at returns the correct number of transactions with the same amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert get_n_transactions_same_amount_at(transactions[0], transactions) == 2
    assert get_n_transactions_same_amount_at(transactions[2], transactions) == 1


def test_get_percent_transactions_same_amount_tolerant() -> None:
    """
    Test that get_percent_transactions_same_amount_tolerant_at returns the correct percentage of transactions
    with the same amount.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=101, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=110, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
    ]
    assert get_percent_transactions_same_amount_tolerant(transactions[0], transactions) == 0.5


def test_get_is_insurance_at() -> None:
    """Test get_is_insurance_at."""
    assert get_is_insurance_at(
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01")
    )
    assert not get_is_insurance_at(Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"))


def test_get_is_phone_at() -> None:
    """Test get_is_phone_at."""
    assert get_is_phone_at(Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"))
    assert not get_is_phone_at(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))


def test_get_is_utility_at() -> None:
    """Test get_is_utility_at."""
    assert get_is_utility_at(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))
    assert not get_is_utility_at(
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03")
    )


def test_get_is_always_recurring_at() -> None:
    """Test get_is_always_recurring_at."""
    assert get_is_always_recurring_at(Transaction(id=1, user_id="user1", name="netflix", amount=100, date="2024-01-01"))
    assert not get_is_always_recurring_at(
        Transaction(id=2, user_id="user1", name="walmart", amount=100, date="2024-01-01")
    )


def test_get_is_communication_or_energy_at() -> None:
    """Test get_is_communication_or_energy_at."""
    assert get_is_communication_or_energy_at(
        Transaction(id=1, user_id="user1", name="AT&T", amount=100, date="2024-01-01")
    )
    assert get_is_communication_or_energy_at(
        Transaction(id=2, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02")
    )
    assert not get_is_communication_or_energy_at(
        Transaction(id=3, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01")
    )


def test_normalize_vendor_name_at() -> None:
    """Test normalize_vendor_name_at."""
    assert normalize_vendor_name_at("AT&T Wireless") == "at&t"
    assert normalize_vendor_name_at("Netflix.com") == "netflix"
    assert normalize_vendor_name_at("Random Store") == "randomstore"


def test_is_recurring_core_at() -> None:
    """Test is_recurring_core_at for monthly recurrence."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01"),
        Transaction(id=4, user_id="user1", name="Allstate Insurance", amount=100, date="2024-02-01"),
    ]
    preprocessed = preprocess_transactions_at(transactions)
    vendor_txns_netflix = preprocessed["by_vendor"][normalize_vendor_name_at("Netflix")]
    assert is_recurring_core_at(
        transactions[0], vendor_txns_netflix, preprocessed, interval=30, variance=4, min_occurrences=2
    )
    vendor_txns_allstate = preprocessed["by_vendor"][normalize_vendor_name_at("Allstate Insurance")]
    assert is_recurring_core_at(
        transactions[2], vendor_txns_allstate, preprocessed, interval=30, variance=4, min_occurrences=2
    )


def test_is_recurring_allowance_at() -> None:
    """Test is_recurring_allowance_at for monthly recurrence with tolerance."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01"),
        Transaction(id=4, user_id="user1", name="Allstate Insurance", amount=100, date="2024-02-01"),
    ]
    assert is_recurring_allowance_at(
        transactions[0], transactions, expected_interval=30, allowance=2, min_occurrences=2
    )
    assert is_recurring_allowance_at(
        transactions[2], transactions, expected_interval=30, allowance=2, min_occurrences=2
    )


def test_preprocess_transactions_at() -> None:
    """Test preprocess_transactions_at for correct grouping and date parsing."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user2", name="Netflix", amount=15.99, date="2024-01-01"),
    ]
    preprocessed = preprocess_transactions_at(transactions)
    assert len(preprocessed["by_vendor"]["netflix"]) == 3
    assert len(preprocessed["by_user_vendor"][("user1", "netflix")]) == 2
    assert preprocessed["date_objects"][transactions[0]].day == 1


def test_normalize_vendor_name() -> None:
    """Test that normalize_vendor_name correctly normalizes vendor names."""
    assert normalize_vendor_name("AT&T Wireless") == "at&t"
    assert normalize_vendor_name("Netflix.com") == "netflix"
    assert normalize_vendor_name("Random Store") == "randomstore"


def test_compute_recurring_inputs_at() -> None:
    """Test compute_recurring_inputs_at for correct grouping and date parsing."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
    ]
    vendor_txns, user_vendor_txns, preprocessed = compute_recurring_inputs_at(transactions[0], transactions)
    assert len(vendor_txns) == 2
    assert len(user_vendor_txns) == 2
    assert "by_vendor" in preprocessed
    assert "netflix" in preprocessed["by_vendor"]
