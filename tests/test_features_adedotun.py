# test features
import pytest

from recur_scan.features_adedotun import (
    compute_recurring_inputs_at,  # Add missing import
    get_amount_uniqueness_score_at,
    get_days_since_last_occurrence_at,
    get_interval_histogram,
    get_interval_variance_coefficient,
    get_is_always_recurring_at,
    get_is_communication_or_energy_at,
    get_is_insurance_at,
    get_is_phone_at,
    get_is_utility_at,
    get_n_transactions_same_amount_at,
    get_n_transactions_same_amount_chris,
    get_new_features,
    get_percent_transactions_same_amount_chris,
    get_percent_transactions_same_amount_tolerant,
    get_same_amount_count_at,
    get_similar_amount_count_at,
    get_user_vendor_occurrence_count_at,
    get_vendor_occurrence_count_at,
    is_known_recurring_company,
    is_price_trending,
    is_recurring_allowance_at,
    is_recurring_based_on_99,
    is_recurring_core_at,
    is_subscription_amount,
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


def test_get_vendor_occurrence_count_at(transactions):
    """Test get_vendor_occurrence_count_at for counting vendor occurrences."""
    transaction = transactions[0]  # Allstate Insurance
    assert get_vendor_occurrence_count_at(transaction, transactions) == 2
    transaction = transactions[3]  # Netflix
    assert get_vendor_occurrence_count_at(transaction, transactions) == 2
    transaction = transactions[2]  # Duke Energy
    assert get_vendor_occurrence_count_at(transaction, transactions) == 1


def test_get_user_vendor_occurrence_count_at(transactions):
    """Test get_user_vendor_occurrence_count_at for user-specific vendor counts."""
    transaction = transactions[0]  # Allstate Insurance, user1
    assert get_user_vendor_occurrence_count_at(transaction, transactions) == 2
    transaction = transactions[3]  # Netflix, user1
    assert get_user_vendor_occurrence_count_at(transaction, transactions) == 2
    transaction = transactions[2]  # Duke Energy, user1
    assert get_user_vendor_occurrence_count_at(transaction, transactions) == 1


def test_get_same_amount_count_at(transactions):
    """Test get_same_amount_count_at for counting transactions with same amount."""
    transaction = transactions[0]  # Allstate Insurance, 100
    assert get_same_amount_count_at(transaction, transactions) == 2
    transaction = transactions[3]  # Netflix, 15.99
    assert get_same_amount_count_at(transaction, transactions) == 2
    transaction = transactions[2]  # Duke Energy, 200
    assert get_same_amount_count_at(transaction, transactions) == 1


def test_get_similar_amount_count_at(transactions):
    """Test get_similar_amount_count_at for counting transactions with similar amounts."""
    transaction = Transaction(id=8, user_id="user1", name="Netflix", amount=15.50, date="2024-01-01")
    assert get_similar_amount_count_at(transaction, transactions) == 2  # Within 5% of 15.99
    transaction = transactions[0]  # Allstate Insurance, 100
    assert get_similar_amount_count_at(transaction, transactions) == 2
    transaction = transactions[2]  # Duke Energy, 200
    assert get_similar_amount_count_at(transaction, transactions) == 1


def test_get_days_since_last_occurrence_at(transactions):
    """Test get_days_since_last_occurrence_at for days since last vendor transaction."""
    transaction = transactions[5]  # Allstate Insurance, 2024-02-01
    assert get_days_since_last_occurrence_at(transaction, transactions) == 31
    transaction = transactions[1]  # AT&T, 2024-01-01
    assert get_days_since_last_occurrence_at(transaction, transactions) == 5 * 365
    transaction = transactions[3]  # Netflix, 2024-03-01
    assert get_days_since_last_occurrence_at(transaction, transactions) == 5 * 365


def test_is_recurring_based_on_99(transactions):
    """Test is_recurring_based_on_99 for detecting .99-ending recurring transactions."""
    transaction = transactions[3]  # Netflix, 15.99, two occurrences
    assert is_recurring_based_on_99(transaction, transactions)
    transaction = transactions[0]  # Allstate Insurance, 100, not .99
    assert not is_recurring_based_on_99(transaction, transactions)


def test_get_interval_variance_coefficient(transactions):
    """Test get_interval_variance_coefficient for interval consistency."""
    transaction = transactions[3]  # Netflix, two transactions
    assert abs(get_interval_variance_coefficient(transaction, transactions) - 0.1) < 0.1  # Low variance
    transaction = transactions[2]  # Duke Energy, single transaction
    assert get_interval_variance_coefficient(transaction, transactions) == 1.0


def test_is_known_recurring_company(transactions):
    """Test is_known_recurring_company for known recurring vendors."""
    transaction = transactions[3]  # Netflix
    assert is_known_recurring_company(transaction, transactions)
    transaction = transactions[2]  # Duke Energy
    assert not is_known_recurring_company(transaction, transactions)


def test_is_price_trending(transactions):
    """Test is_price_trending for stable or trending amounts."""
    transaction = transactions[3]  # Netflix, stable
    assert is_price_trending(transaction, transactions)
    transaction = transactions[2]  # Duke Energy, single transaction
    assert not is_price_trending(transaction, transactions)


def test_get_n_transactions_same_amount_chris(transactions):
    """Test get_n_transactions_same_amount_chris for counting similar amounts."""
    transaction = transactions[3]  # Netflix, 15.99
    assert get_n_transactions_same_amount_chris(transaction, transactions, "Netflix") == 2
    transaction = transactions[2]  # Duke Energy, 200
    assert get_n_transactions_same_amount_chris(transaction, transactions, "Duke Energy") == 1


def test_get_percent_transactions_same_amount_chris(transactions):
    """Test get_percent_transactions_same_amount_chris for percentage of similar amounts."""
    transaction = transactions[3]  # Netflix, 15.99
    assert get_percent_transactions_same_amount_chris(transaction, transactions, "Netflix") == 100.0
    transaction = transactions[2]  # Duke Energy, 200
    assert get_percent_transactions_same_amount_chris(transaction, transactions, "Duke Energy") == 100.0


def test_is_subscription_amount():
    """Test is_subscription_amount for common subscription amounts."""
    assert is_subscription_amount(14.99)  # Common subscription price
    assert is_subscription_amount(10.00)
    assert not is_subscription_amount(15.99)  # Adjust based on function behavior
    assert not is_subscription_amount(17.23)


def test_get_new_features(transactions):
    """Test get_new_features for returning all feature values."""
    features = get_new_features(transactions[3], transactions)  # Netflix
    assert features["is_known_recurring"] is True
    assert features["is_one_time_vendor"] is False
    assert features["vendor_occurrence_count"] == 2
    assert features["same_amount_count"] == 2
    assert features["is_weekend"] is False
    assert features["is_entertainment"] is False
    assert features["is_recurring_based_on_99_at"] is True
    assert features["amount_variability_score_refine"] < 2.5


def test_get_amount_uniqueness_score_at(transactions):
    """Test get_amount_uniqueness_score_at for calculating amount uniqueness."""
    transaction = transactions[3]  # Netflix, 15.99
    assert get_amount_uniqueness_score_at(transaction, transactions) == 0.0  # 2/2 similar
    transaction = transactions[2]  # Duke Energy, 200
    assert get_amount_uniqueness_score_at(transaction, transactions) == 0.0  # 1/1 similar, self-match


def test_get_interval_histogram(transactions):
    """Test get_interval_histogram for periodicity score."""
    transaction = transactions[3]  # Netflix
    score = get_interval_histogram(transaction, transactions)
    assert 0.0 <= score <= 1.0
    assert score == 0.0  # Only one other matching transaction after filtering, no intervals
