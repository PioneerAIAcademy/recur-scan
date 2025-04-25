# test features

import pytest

from recur_scan.features_yoloye import (
    get_delayed_annual,
    get_delayed_fortnightly,
    get_delayed_monthly,
    get_delayed_quarterly,
    get_delayed_semi_annual,
    get_delayed_weekly,
    get_early_annual,
    get_early_fortnightly,
    get_early_monthly,
    get_early_quarterly,
    get_early_semi_annual,
    get_early_weekly,
    get_n_transactions_delayed,
    get_n_transactions_early,
)
from recur_scan.transactions import Transaction


@pytest.fixture
def sample_transaction():
    return Transaction(
        id=0,
        user_id="user",
        date="2023-01-01",
        amount=100.0,
        name="Test",
    )


@pytest.fixture
def delayed_transactions():
    # Base date: 2023-01-01
    return [
        # Weekly delayed (7+1 days)
        Transaction(
            id=0,
            user_id="user",
            date="2023-01-08",
            amount=100.0,
            name="Test",
        ),
        # Fortnightly delayed (14+2 days)
        Transaction(
            id=1,
            user_id="user",
            date="2023-01-16",
            amount=100.0,
            name="Test",
        ),
        # Monthly delayed (30+3 days)
        Transaction(
            id=2,
            user_id="user",
            date="2023-02-03",
            amount=100.0,
            name="Test",
        ),
        # Quarterly delayed (90+5 days)
        Transaction(
            id=3,
            user_id="user",
            date="2023-04-06",
            amount=100.0,
            name="Test",
        ),
        # Semi-annual delayed (180+8 days)
        Transaction(
            id=4,
            user_id="user",
            date="2023-07-07",
            amount=100.0,
            name="Test",
        ),
        # Annual delayed (365+10 days)
        Transaction(
            id=5,
            user_id="user",
            date="2024-01-11",
            amount=100.0,
            name="Test",
        ),
    ]


@pytest.fixture
def early_transactions():
    # Base date: 2023-01-01
    return [
        # Weekly early (7-1 days)
        Transaction(
            id=0,
            user_id="user",
            date="2023-01-06",
            amount=100.0,
            name="Test",
        ),
        # Fortnightly early (14-2 days)
        Transaction(
            id=1,
            user_id="user",
            date="2023-01-12",
            amount=100.0,
            name="Test",
        ),
        # Monthly early (30-3 days)
        Transaction(
            id=2,
            user_id="user",
            date="2023-01-27",
            amount=100.0,
            name="Test",
        ),
        # Quarterly early (90-5 days)
        Transaction(
            id=3,
            user_id="user",
            date="2023-03-27",
            amount=100.0,
            name="Test",
        ),
        # Semi-annual early (180-8 days)
        Transaction(
            id=4,
            user_id="user",
            date="2023-06-23",
            amount=100.0,
            name="Test",
        ),
        # Annual early (365-10 days)
        Transaction(
            id=5,
            user_id="user",
            date="2023-12-22",
            amount=100.0,
            name="Test",
        ),
    ]


def test_get_n_transactions_delayed(sample_transaction, delayed_transactions):
    # Test with monthly interval (30 days) and max_delay of 5
    result = get_n_transactions_delayed(sample_transaction, delayed_transactions, expected_interval=30, max_delay=5)
    # Only one transaction should match (the monthly delayed one at 33 days)
    assert result == 1

    # Test with empty transactions list
    assert get_n_transactions_delayed(sample_transaction, [], 30, 5) == 0

    # Test with transaction outside delay window
    far_future = Transaction(
        id=6,
        user_id="user",
        date="2023-02-10",  # 40 days after base (beyond 30+5)
        amount=100.0,
        name="Test",
    )
    assert get_n_transactions_delayed(sample_transaction, [far_future], expected_interval=30, max_delay=5) == 0


def test_get_delayed_weekly(sample_transaction, delayed_transactions):
    # Weekly transaction is 8 days after base (7+1), should be detected
    result = get_delayed_weekly(sample_transaction, delayed_transactions)
    assert result == 1

    # Test with empty transactions list
    assert get_delayed_weekly(sample_transaction, []) == 0


def test_get_delayed_fortnightly(sample_transaction, delayed_transactions):
    # Fortnightly transaction is 16 days after base (14+2), should be detected
    result = get_delayed_fortnightly(sample_transaction, delayed_transactions)
    assert result == 1

    # Test with empty transactions list
    assert get_delayed_fortnightly(sample_transaction, []) == 0


def test_get_delayed_monthly(sample_transaction, delayed_transactions):
    # Monthly transaction is 33 days after base (30+3), should be detected
    result = get_delayed_monthly(sample_transaction, delayed_transactions)
    assert result == 1

    # Test with empty transactions list
    assert get_delayed_monthly(sample_transaction, []) == 0


def test_get_delayed_quarterly(sample_transaction, delayed_transactions):
    # Quarterly transaction is 95 days after base (90+5), should be detected
    result = get_delayed_quarterly(sample_transaction, delayed_transactions)
    assert result == 1

    # Test with empty transactions list
    assert get_delayed_quarterly(sample_transaction, []) == 0


def test_get_delayed_semi_annual(sample_transaction, delayed_transactions):
    # Semi-annual transaction is 188 days after base (180+8), should be detected
    result = get_delayed_semi_annual(sample_transaction, delayed_transactions)
    assert result == 1

    # Test with empty transactions list
    assert get_delayed_semi_annual(sample_transaction, []) == 0


def test_get_delayed_annual(sample_transaction, delayed_transactions):
    # Annual transaction is 375 days after base (365+10), should be detected
    result = get_delayed_annual(sample_transaction, delayed_transactions)
    assert result == 1

    # Test with empty transactions list
    assert get_delayed_annual(sample_transaction, []) == 0


def test_get_n_transactions_early(sample_transaction, early_transactions):
    # Test with monthly interval (30 days) and max_early of 5
    result = get_n_transactions_early(sample_transaction, early_transactions, expected_interval=30, max_early=5)
    # Only one transaction should match (the monthly early one at 27 days)
    assert result == 1

    # Test with empty transactions list
    assert get_n_transactions_early(sample_transaction, [], 30, 5) == 0

    # Test with transaction outside early window
    too_close = Transaction(
        id=6,
        user_id="user",
        date="2023-01-24",  # 23 days after base (before 30-5)
        amount=100.0,
        name="Test",
    )
    assert get_n_transactions_early(sample_transaction, [too_close], expected_interval=30, max_early=5) == 0


def test_get_early_weekly(sample_transaction, early_transactions):
    # Weekly transaction is 6 days after base (7-1), should be detected
    result = get_early_weekly(sample_transaction, early_transactions)
    assert result == 1

    # Test with empty transactions list
    assert get_early_weekly(sample_transaction, []) == 0


def test_get_early_fortnightly(sample_transaction):
    # Note: This function uses get_n_transactions_days_apart in the implementation
    # which has different behavior than get_n_transactions_early

    # Create a transaction that would match with get_n_transactions_days_apart
    # For days_apart=14, days_off=3, we need a transaction that's either:
    # - 11-14 days apart (14-3 to 14)
    # - 14-17 days apart (14 to 14+3)
    # - or any multiple of 14 ±3 days
    matching_tx = Transaction(
        id=6,
        user_id="user",
        date="2023-01-13",  # 12 days after base (within 14±3)
        amount=100.0,
        name="Test",
    )

    result = get_early_fortnightly(sample_transaction, [matching_tx])
    assert result == 1

    # Test with empty transactions list
    assert get_early_fortnightly(sample_transaction, []) == 0


def test_get_early_monthly(sample_transaction):
    # Note: This function uses get_n_transactions_days_apart in the implementation

    # Create a transaction that would match with get_n_transactions_days_apart
    # For days_apart=30, days_off=5, we need a transaction that's either:
    # - 25-30 days apart (30-5 to 30)
    # - 30-35 days apart (30 to 30+5)
    # - or any multiple of 30 ±5 days
    matching_tx = Transaction(
        id=6,
        user_id="user",
        date="2023-01-28",  # 27 days after base (within 30±5)
        amount=100.0,
        name="Test",
    )

    result = get_early_monthly(sample_transaction, [matching_tx])
    assert result == 1

    # Test with empty transactions list
    assert get_early_monthly(sample_transaction, []) == 0


def test_get_early_quarterly(sample_transaction):
    # Note: This function uses get_n_transactions_days_apart in the implementation

    # Create a transaction that would match with get_n_transactions_days_apart
    # For days_apart=90, days_off=7, we need a transaction that's either:
    # - 83-90 days apart (90-7 to 90)
    # - 90-97 days apart (90 to 90+7)
    # - or any multiple of 90 ±7 days
    matching_tx = Transaction(
        id=6,
        user_id="user",
        date="2023-03-28",  # 86 days after base (within 90±7)
        amount=100.0,
        name="Test",
    )

    result = get_early_quarterly(sample_transaction, [matching_tx])
    assert result == 1

    # Test with empty transactions list
    assert get_early_quarterly(sample_transaction, []) == 0


def test_get_early_semi_annual(sample_transaction):
    # Note: This function uses get_n_transactions_days_apart in the implementation

    # Create a transaction that would match with get_n_transactions_days_apart
    # For days_apart=180, days_off=10, we need a transaction that's either:
    # - 170-180 days apart (180-10 to 180)
    # - 180-190 days apart (180 to 180+10)
    # - or any multiple of 180 ±10 days
    matching_tx = Transaction(
        id=6,
        user_id="user",
        date="2023-06-25",  # 175 days after base (within 180±10)
        amount=100.0,
        name="Test",
    )

    result = get_early_semi_annual(sample_transaction, [matching_tx])
    assert result == 1

    # Test with empty transactions list
    assert get_early_semi_annual(sample_transaction, []) == 0


def test_get_early_annual(sample_transaction):
    # Note: This function uses get_n_transactions_days_apart in the implementation

    # Create a transaction that would match with get_n_transactions_days_apart
    # For days_apart=365, days_off=15, we need a transaction that's either:
    # - 350-365 days apart (365-15 to 365)
    # - 365-380 days apart (365 to 365+15)
    # - or any multiple of 365 ±15 days
    matching_tx = Transaction(
        id=6,
        user_id="user",
        date="2023-12-20",  # 353 days after base (within 365±15)
        amount=100.0,
        name="Test",
    )

    result = get_early_annual(sample_transaction, [matching_tx])
    assert result == 1

    # Test with empty transactions list
    assert get_early_annual(sample_transaction, []) == 0
