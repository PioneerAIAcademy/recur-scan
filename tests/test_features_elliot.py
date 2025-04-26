# %%
# configure the script
from datetime import datetime

import pytest

from recur_scan.features_elliot import (
    _to_txn_dict,
    calculate_merchant_diversity,
    calculate_weekday_consistency,
    detect_duplicates,
    detect_spending_anomalies,
    detect_split_payments,
    get_is_always_recurring,
    get_is_near_same_amount,
    is_auto_pay,
    is_membership,
    is_recurring_based_on_99,
    is_utility_bill,
    organize_transactions_by_user_company,
)
from recur_scan.transactions import Transaction


# %%
# configure the script
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
        Transaction(id=8, user_id="user1", name="Amazon", amount=50, date="2024-01-01"),
        Transaction(id=9, user_id="user1", name="Amazon", amount=75, date="2024-01-02"),
        Transaction(id=10, user_id="user1", name="Netflix", amount=20, date="2024-01-03"),
        Transaction(id=11, user_id="user2", name="Amazon", amount=30, date="2024-01-01"),
        Transaction(id=12, user_id="user2", name="Spotify", amount=9.99, date="2024-01-05"),
    ]


# %%
# configure the script
def test_is_utility_bill(transactions) -> None:
    """Test is_utility_bill."""
    assert is_utility_bill(transactions[2])  # Assuming transactions[2] is a utility bill
    assert not is_utility_bill(transactions[3])  # Assuming transactions[3] is NOT a utility bill


# %%
# configure the script
def test_get_is_near_same_amount(transactions) -> None:
    """Test get_is_near_same_amount."""
    assert get_is_near_same_amount(transactions[0], transactions)
    assert not get_is_near_same_amount(transactions[3], transactions)


# %%
# configure the script
def test_get_is_always_recurring(transactions) -> None:
    """Test get_is_always_recurring."""
    assert get_is_always_recurring(transactions[4])
    assert not get_is_always_recurring(transactions[3])


# %%
# configure the script
def test_is_auto_pay(transactions) -> None:
    """Test is_auto_pay."""
    assert is_auto_pay(transactions[5])
    assert not is_auto_pay(transactions[0])


# %%
# configure the script
def test_is_membership(transactions) -> None:
    """Test is_membership."""
    assert is_membership(transactions[6])
    assert not is_membership(transactions[0])


# %%
# configure the script
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

# %%
# configure the script


@pytest.fixture
def sample_transactions():
    """Fixture providing sample transaction dicts."""
    return [
        {"user_id": "user1", "merchant": "Amazon", "amount": 50.0, "date": "2024-01-01"},
        {"user_id": "user1", "merchant": "Netflix", "amount": 20.0, "date": "2024-01-03"},
        {"user_id": "user2", "merchant": "Amazon", "amount": 30.0, "date": "2024-01-01"},
        {"user_id": "user1", "merchant": "Amazon", "amount": 25.0, "date": "2024-01-01"},
    ]


# %%
# configure the script
def test_organize_transactions_by_user_company(sample_transactions):
    result = organize_transactions_by_user_company(sample_transactions)
    # user1, amazon on 2024-01-01 should have both 50.0 and 25.0
    assert result["user1"]["amazon"][datetime(2024, 1, 1)] == [50.0, 25.0]
    # user1, netflix on 2024-01-03
    assert result["user1"]["netflix"][datetime(2024, 1, 3)] == [20.0]
    # user2, amazon on 2024-01-01
    assert result["user2"]["amazon"][datetime(2024, 1, 1)] == [30.0]


# %%
# configure the script
def test_detect_duplicates():
    txns = [
        {"user_id": "u1", "merchant": "A", "amount": 10, "date": "2024-01-01"},
        {"user_id": "u1", "merchant": "A", "amount": 10, "date": "2024-01-01"},
        {"user_id": "u2", "merchant": "B", "amount": 20, "date": "2024-01-02"},
    ]
    duplicates = detect_duplicates(txns)
    assert len(duplicates) == 1


# %%
# configure the script
def test_detect_split_payments():
    txns = [
        {"merchant": "Amazon", "amount": 50.00, "date": "2024-01-01"},
        {"merchant": "Amazon", "amount": 49.95, "date": "2024-01-02"},
        {"merchant": "Netflix", "amount": 100.00, "date": "2024-01-01"},
    ]
    splits = detect_split_payments(txns, tolerance=0.1)
    assert any(pair[0]["amount"] == 50.0 and pair[1]["amount"] == 49.95 for pair in splits)


# %%
# configure the script
def test_detect_spending_anomalies():
    txns = [
        {"merchant": "A", "amount": 100},
        {"merchant": "B", "amount": 500},
        {"merchant": "C", "amount": 100},
    ]
    anomalies = detect_spending_anomalies(txns)
    assert "B" in anomalies


# %%
# configure the script
def test_calculate_weekday_consistency():
    txns = [
        {"date": "2024-04-01"},  # Monday
        {"date": "2024-04-01"},  # Monday
        {"date": "2024-04-02"},  # Tuesday
    ]
    result = calculate_weekday_consistency(txns)
    assert result == pytest.approx(2 / 3)


# %%
# configure the script
def test_calculate_merchant_diversity():
    txns = [
        {"merchant": "A"},
        {"merchant": "B"},
        {"merchant": "A"},
        {"merchant": "C"},
    ]
    result = calculate_merchant_diversity(txns)
    assert result == pytest.approx(0.75)


# %%
# configure the script
def test_to_txn_dict_with_dict():
    txn_dict = {
        "user_id": "u1",
        "name": "store",
        "amount": 100.0,
        "date": "2023-04-01",
    }
    result = _to_txn_dict(txn_dict)
    assert result == {
        "user_id": "u1",  # <--- MUST expect user_id now
        "merchant": "store",
        "amount": 100.0,
        "date": "2023-04-01",
    }


# %%
# configure the script
def test_to_txn_dict_with_transaction_obj():
    txn = Transaction(id=1, user_id="u1", name="store", amount=100.0, date="2023-04-01")
    result = _to_txn_dict(txn)
    assert result == {
        "user_id": "u1",  # <--- MUST expect user_id now
        "merchant": "store",
        "amount": 100.0,
        "date": "2023-04-01",
    }


# %%
# configure the script
def test_to_txn_dict_raises_on_invalid_input():
    with pytest.raises(TypeError):
        _to_txn_dict(object())  # type: ignore[arg-type]


# %%
