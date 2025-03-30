from datetime import datetime

import numpy as np
import pytest

from recur_scan.features_tife import (
    get_amount_cluster_count,
    get_amount_range,
    get_amount_relative_change,
    get_amount_stability_score,
    get_amount_variability,
    get_days_since_last_same_amount,
    get_dominant_interval_strength,
    get_interval_consistency,
    get_interval_histogram,
    get_interval_mode,
    get_merchant_amount_signature,
    get_merchant_name_frequency,
    get_near_amount_consistency,
    get_normalized_interval_consistency,
    get_transaction_count,
    get_transaction_density,
    get_transaction_frequency,
)
from recur_scan.transactions import Transaction


@pytest.fixture
def transactions():
    """Fixture providing test transactions with varied amounts, dates, and merchants."""
    return [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100.0, date="2024-01-15"),  # 14 days
        Transaction(id=3, user_id="user1", name="vendor1", amount=105.0, date="2024-02-01"),  # 17 days
        Transaction(id=4, user_id="user1", name="vendor1", amount=200.0, date="2024-03-01"),  # 29 days
        Transaction(id=5, user_id="user1", name="vendor2", amount=100.0, date="2024-03-15"),  # 14 days
    ]


@pytest.fixture
def empty_transactions():
    """Fixture providing an empty transaction list."""
    return []


@pytest.fixture
def single_transaction():
    """Fixture providing a single transaction."""
    return [Transaction(id=1, user_id="user1", name="vendor1", amount=100.0, date="2024-01-01")]


def test_get_transaction_frequency(transactions, empty_transactions, single_transaction) -> None:
    """Test that get_transaction_frequency calculates the average interval correctly."""
    assert pytest.approx(get_transaction_frequency(transactions)) == (14 + 17 + 29 + 14) / 4  # 18.5
    assert get_transaction_frequency(empty_transactions) == 0.0
    assert get_transaction_frequency(single_transaction) == 0.0


def test_get_interval_consistency(transactions, empty_transactions, single_transaction) -> None:
    """Test that get_interval_consistency calculates the standard deviation of intervals."""
    intervals = [14, 17, 29, 14]
    expected_std = np.std(intervals)
    assert pytest.approx(get_interval_consistency(transactions)) == expected_std
    assert get_interval_consistency(empty_transactions) == 0.0
    assert get_interval_consistency(single_transaction) == 0.0


def test_get_amount_variability(transactions, empty_transactions) -> None:
    """Test that get_amount_variability calculates the coefficient of variation."""
    amounts = [100.0, 100.0, 105.0, 200.0, 100.0]
    mean = np.mean(amounts)
    std = np.std(amounts)
    expected_cv = std / mean
    assert pytest.approx(get_amount_variability(transactions)) == expected_cv
    assert get_amount_variability(empty_transactions) == 0.0


def test_get_amount_range(transactions, empty_transactions) -> None:
    """Test that get_amount_range calculates the range of amounts."""
    assert get_amount_range(transactions) == 200.0 - 100.0  # 100
    assert get_amount_range(empty_transactions) == 0.0


def test_get_transaction_count(transactions, empty_transactions) -> None:
    """Test that get_transaction_count returns the total number of transactions."""
    assert get_transaction_count(transactions) == 5
    assert get_transaction_count(empty_transactions) == 0


def test_get_interval_mode(transactions, empty_transactions, single_transaction) -> None:
    """Test that get_interval_mode returns the most common interval."""
    assert get_interval_mode(transactions) == 14  # 14 appears twice
    assert get_interval_mode(empty_transactions) == 0.0
    assert get_interval_mode(single_transaction) == 0.0


def test_get_normalized_interval_consistency(transactions, empty_transactions, single_transaction) -> None:
    """Test that get_normalized_interval_consistency normalizes the standard deviation."""
    intervals = [14, 17, 29, 14]
    mean = np.mean(intervals)
    std = np.std(intervals)
    expected_normalized = std / mean
    assert pytest.approx(get_normalized_interval_consistency(transactions)) == expected_normalized
    assert get_normalized_interval_consistency(empty_transactions) == 0.0
    assert get_normalized_interval_consistency(single_transaction) == 0.0


def test_get_days_since_last_same_amount(transactions) -> None:
    """Test that get_days_since_last_same_amount calculates days since the last identical amount."""
    assert get_days_since_last_same_amount(transactions[1], transactions) == 14  # 2024-01-15 - 2024-01-01
    assert get_days_since_last_same_amount(transactions[0], transactions) == -1.0  # No prior same amount


def test_get_amount_cluster_count(transactions, empty_transactions, single_transaction) -> None:
    """Test that get_amount_cluster_count counts clusters with interval filtering."""
    # 100.0 and 105.0 within 5%, counting instances where interval > 5 days
    # 100.0 at 01-15, 105.0 at 02-01, 100.0 at 03-15
    assert get_amount_cluster_count(transactions[0], transactions) == 3
    assert get_amount_cluster_count(transactions[0], empty_transactions) == 0
    assert get_amount_cluster_count(transactions[0], single_transaction) == 0


def test_get_amount_relative_change(transactions) -> None:
    """Test that get_amount_relative_change calculates the relative change from the previous transaction."""
    assert pytest.approx(get_amount_relative_change(transactions[1], transactions)) == 0.0  # 100.0 -> 100.0
    assert pytest.approx(get_amount_relative_change(transactions[2], transactions)) == 0.05  # 100.0 -> 105.0
    assert get_amount_relative_change(transactions[0], transactions) == 0.0  # No prior


def test_get_merchant_name_frequency(transactions) -> None:
    """Test that get_merchant_name_frequency counts transactions with the same merchant."""
    assert get_merchant_name_frequency(transactions[0], transactions) == 4  # vendor1 has 4
    assert get_merchant_name_frequency(transactions[4], transactions) == 1  # vendor2 has 1


def test_get_interval_histogram(transactions, empty_transactions, single_transaction) -> None:
    """Test that get_interval_histogram calculates biweekly and monthly proportions."""
    hist = get_interval_histogram(transactions)
    assert pytest.approx(hist["biweekly"]) == 2 / 4  # 14, 14 out of [14, 17, 29, 14]
    assert pytest.approx(hist["monthly"]) == 1 / 4  # 29 out of [14, 17, 29, 14]
    assert get_interval_histogram(empty_transactions) == {"biweekly": 0.0, "monthly": 0.0}
    assert get_interval_histogram(single_transaction) == {"biweekly": 0.0, "monthly": 0.0}


def test_get_amount_stability_score(transactions, empty_transactions) -> None:
    """Test that get_amount_stability_score calculates the proportion within one standard deviation."""
    amounts = [100.0, 100.0, 105.0, 200.0, 100.0]
    mean = np.mean(amounts)
    std = np.std(amounts)
    expected_score = sum(1 for a in amounts if abs(a - mean) <= std) / len(amounts)
    assert pytest.approx(get_amount_stability_score(transactions)) == expected_score
    assert get_amount_stability_score(empty_transactions) == 0.0


def test_get_dominant_interval_strength(transactions, empty_transactions, single_transaction) -> None:
    """Test that get_dominant_interval_strength measures the strength of the dominant interval."""
    assert pytest.approx(get_dominant_interval_strength(transactions)) == 2 / 4  # 14 is dominant
    assert get_dominant_interval_strength(empty_transactions) == 0.0
    assert get_dominant_interval_strength(single_transaction) == 0.0


def test_get_near_amount_consistency(transactions, empty_transactions) -> None:
    """Test that get_near_amount_consistency calculates the proportion of near-amount transactions."""
    assert (
        pytest.approx(get_near_amount_consistency(transactions[0], transactions)) == 4 / 5
    )  # 100, 100, 105, 100 within 5%
    assert get_near_amount_consistency(transactions[0], empty_transactions) == 0.0


def test_get_merchant_amount_signature(transactions, empty_transactions) -> None:
    """Test that get_merchant_amount_signature calculates the signature for the merchant."""
    # vendor1: [100, 100, 105, 200], 3 within 5% of 100
    assert pytest.approx(get_merchant_amount_signature(transactions[0], transactions)) == 3 / 4
    assert get_merchant_amount_signature(transactions[4], transactions) == 1.0  # vendor2: [100]
    assert get_merchant_amount_signature(transactions[0], empty_transactions) == 0.0


def test_get_transaction_density(transactions, empty_transactions, single_transaction) -> None:
    """Test that get_transaction_density calculates transactions per day."""
    dates = [
        datetime(2024, 1, 1),
        datetime(2024, 1, 15),
        datetime(2024, 2, 1),
        datetime(2024, 3, 1),
        datetime(2024, 3, 15),
    ]
    time_span = (dates[-1] - dates[0]).days  # 74 days
    assert pytest.approx(get_transaction_density(transactions)) == len(transactions) / time_span
    assert get_transaction_density(empty_transactions) == 0.0
    assert get_transaction_density(single_transaction) == 0.0
