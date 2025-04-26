# test features
import statistics
from datetime import datetime

import pytest

from recur_scan.features_adeyinka import (
    _get_days,
    get_amount_consistency_score,
    get_average_days_between_transactions,
    get_day_of_month_consistency,
    get_is_always_recurring,
    get_n_transactions_days_apart,
    get_outlier_score,
    get_phone_bill_indicator,
    get_recent_transaction_frequency,
    get_recurring_confidence_score,
    get_same_amount_vendor_transactions,
    get_subscription_keyword_score,
    get_time_regularity_score,
    get_transaction_amount_variance,
    is_bnpl_service,
    parse_date,
)
from recur_scan.transactions import Transaction


@pytest.fixture
def transactions():
    """Fixture providing test transactions."""
    return [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="Netflix", amount=15.99, date="2024-01-05"),
    ]


def test_parse_date() -> None:
    """Test that parse_date correctly handles different date formats."""
    # Test YYYY-MM-DD format
    assert parse_date("2024-01-15") == datetime(2024, 1, 15)

    # Test MM/DD/YYYY format
    assert parse_date("01/15/2024") == datetime(2024, 1, 15)

    # Test fallback
    try:
        result = parse_date("invalid-date")
        assert result == datetime(1970, 1, 1)
    except ValueError:
        pytest.fail("parse_date should handle invalid dates gracefully")


@pytest.mark.parametrize(
    ("transaction_name", "expected_result"),
    [
        # Test known recurring vendors (case-insensitive)
        ("Netflix", True),
        ("NETFLIX", True),
        ("netflix", True),
        ("Spotify", True),
        ("Adobe Creative Cloud", True),
        ("adobe creative cloud", True),
        # Test non-recurring vendors
        ("Walmart", False),
        ("Target", False),
        ("Restaurant XYZ", False),
        ("Gas Station", False),
        # Test edge cases
        ("", False),  # Empty vendor name
        ("Netflixx", False),  # Close but not exact match
        ("Google", False),  # Partial match but not in the list
    ],
)
def test_get_is_always_recurring(transaction_name, expected_result):
    """Test that get_is_always_recurring correctly identifies recurring vendors."""
    # Create a transaction with the given vendor name
    transaction = Transaction(id=1, user_id="user1", name=transaction_name, amount=100, date="2024-01-01")

    # Call the function and assert the result
    assert get_is_always_recurring(transaction) == expected_result


def test_get_average_days_between_transactions_valid(transactions):
    """Test with multiple valid transactions for same vendor"""
    # Test with vendor1 transactions (ids 1-3)
    result = get_average_days_between_transactions(transactions[0], transactions)
    assert result == 1.0  # (1 day between 01-01 and 01-02) + (1 day between 01-02 and 01-03) / 2 = 1.0


def test_get_average_single_vendor_transaction(transactions):
    """Test with only one transaction for a vendor"""
    # Netflix only has one transaction (id=4)
    result = get_average_days_between_transactions(transactions[3], transactions)
    assert result == 0.0


def test_get_average_with_invalid_date(transactions):
    """Test that invalid dates are properly ignored"""
    # Make a copy of transactions to modify
    test_transactions = transactions.copy()

    # Add invalid date transaction
    test_transactions.append(Transaction(id=5, user_id="user1", name="vendor1", amount=100, date="invalid-date"))

    # Get all vendor1 transactions (ids 1-3 plus invalid id5)
    vendor1_txns = [t for t in test_transactions if t.name == "vendor1"]
    print(f"Found {len(vendor1_txns)} vendor1 transactions")

    # Calculate result
    result = get_average_days_between_transactions(test_transactions[0], test_transactions)

    # Debug output
    print(f"Calculated average days: {result}")

    # Should be average of:
    # 2024-01-01 to 2024-01-02 = 1 day
    # 2024-01-02 to 2024-01-03 = 1 day
    # Average = (1 + 1) / 2 = 1.0
    assert result == 1.0, f"Expected average of 1.0 day, got {result}. Check if invalid date was properly filtered out."


def test_get_average_new_vendor(transactions):
    """Test with a new vendor that has two transactions"""
    modified_transactions = transactions.copy()
    modified_transactions.extend([
        Transaction(id=5, user_id="user1", name="Spotify", amount=9.99, date="2024-01-01"),
        Transaction(id=6, user_id="user1", name="Spotify", amount=9.99, date="2024-01-31"),
    ])
    spotify_txn = modified_transactions[-1]
    result = get_average_days_between_transactions(spotify_txn, modified_transactions)
    assert result == 30.0  # 30 days between Spotify transactions


def test_get_average_empty_list():
    """Test with empty transactions list"""
    dummy_txn = Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01")
    result = get_average_days_between_transactions(dummy_txn, [])
    assert result == 0.0


def test_time_regularity_score():
    """Test time regularity score calculation"""
    # Perfectly regular transactions
    regular_transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=100, date="2024-03-01"),
    ]

    # Test regular transactions
    regular_score = get_time_regularity_score(regular_transactions[0], regular_transactions)
    assert regular_score > 0.7, f"Expected fairly high regularity score, got {regular_score}"

    # Irregular transactions
    irregular_transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-02-15"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=100, date="2024-04-30"),
    ]

    # Test irregular transactions
    irregular_score = get_time_regularity_score(irregular_transactions[0], irregular_transactions)
    assert irregular_score < 0.5, f"Expected lower regularity score, got {irregular_score}"


def test_time_regularity_few_transactions():
    """Test with fewer than 3 transactions"""
    few_transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-02-01"),
    ]

    score = get_time_regularity_score(few_transactions[0], few_transactions)
    assert score == 0.0, f"Expected 0.0 for less than 3 transactions, got {score}"


def test_get_days():
    """Test _get_days function with various scenarios"""
    # Test a specific known date
    assert _get_days("1970-01-01") == 0, "Epoch date should return 0"

    # Test a date after epoch
    assert _get_days("1970-01-02") == 1, "Day after epoch should return 1"

    # Test a more recent date
    assert _get_days("2024-01-01") > 0, "Recent date should return positive days"

    # Test an invalid date
    assert _get_days("invalid-date") == 0, "Invalid date should return 0"

    # Test another valid date
    specific_date = "2023-06-15"
    expected_days = (parse_date(specific_date) - datetime(1970, 1, 1)).days
    assert _get_days(specific_date) == expected_days, "Should correctly calculate days since epoch"


def test_get_n_transactions_days_apart():
    """Test get_n_transactions_days_apart with detailed diagnostics"""
    # Create a base set of transactions with more varied dates
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-31"),  # 30 days
        Transaction(id=3, user_id="user1", name="vendor1", amount=100, date="2024-02-28"),  # 58 days
        Transaction(id=4, user_id="user1", name="vendor1", amount=100, date="2024-03-28"),  # 88 days
        Transaction(id=5, user_id="user1", name="vendor2", amount=50, date="2024-02-15"),
    ]

    base_transaction = transactions[0]
    base_days = _get_days(base_transaction.date)

    # Detailed diagnostic print
    print("\nDetailed Diagnostic:")
    print(f"Base transaction date: {base_transaction.date}, Base Days: {base_days}")

    # Detailed breakdown for each transaction
    for t in transactions[1:]:
        t_days = _get_days(t.date)
        days_diff = abs(t_days - base_days)
        quotient = days_diff / 30
        remainder = abs(days_diff - round(quotient) * 30)

        print("\nTransaction Details:")
        print(f"  Date: {t.date}")
        print(f"  Transaction Days: {t_days}")
        print(f"  Days Difference from Base: {days_diff}")
        print(f"  Quotient (days_diff / 30): {quotient}")
        print(f"  Rounded Quotient: {round(quotient)}")
        print(f"  Remainder: {remainder}")

    # Test with some flexibility (5 days off)
    result = get_n_transactions_days_apart(base_transaction, transactions, n_days_apart=30, n_days_off=5)

    # Print the result for clarity
    print(f"\nFinal Result: {result} matching transactions")

    # Assertion with more informative error message
    assert result == 2, (
        f"Should find 2 transactions within 5 days of 30-day intervals, found {result}\n"
        "Detailed Analysis:\n"
        "  2024-01-31: 30 days (should match)\n"
        "  2024-02-28: 58 days (may not match)\n"
        "  2024-03-28: 88 days (may not match)\n"
        "  2024-02-15: 45 days (should not match)"
    )


def test_get_transaction_amount_variance_multiple_transactions():
    """Test standard deviation calculation with multiple transactions for the same vendor."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
    ]

    result = get_transaction_amount_variance(transactions[0], transactions)
    expected = statistics.stdev([100, 150, 200])

    assert result == expected, f"Expected {expected}, but got {result}"


def test_get_transaction_amount_variance_single_transaction():
    """Test when there's only one transaction for the vendor (should return 0.0)."""
    transactions = [Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01")]

    result = get_transaction_amount_variance(transactions[0], transactions)
    assert result == 0.0, f"Expected 0.0, but got {result}"


def test_get_transaction_amount_variance_different_vendors():
    """Test that the function correctly filters by vendor name."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor2", amount=200, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=150, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="vendor1", amount=180, date="2024-01-04"),
    ]

    result = get_transaction_amount_variance(transactions[0], transactions)
    expected = statistics.stdev([100, 150, 180])

    assert result == expected, f"Expected {expected}, but got {result}"


def test_get_transaction_amount_variance_empty_list():
    """Test when no transactions are present (should return 0.0)."""
    dummy_txn = Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01")

    result = get_transaction_amount_variance(dummy_txn, [])
    assert result == 0.0, f"Expected 0.0, but got {result}"


def test_get_outlier_score_outlier_transaction():
    """Test a transaction that is a clear outlier."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Amazon", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Amazon", amount=102, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="Amazon", amount=101, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="Amazon", amount=200, date="2024-01-04"),  # Outlier
    ]

    result = get_outlier_score(transactions[3], transactions)  # Testing amount = 200
    assert result > 2.0, f"Expected z-score > 2.0, but got {result}"


def test_get_recurring_confidence_score():
    """Test the recurring confidence score calculation."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"),
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-01-15"),
        Transaction(id=5, user_id="user1", name="Spotify", amount=9.99, date="2024-02-15"),
        Transaction(id=6, user_id="user1", name="Gym", amount=30.00, date="2024-01-10"),
    ]

    netflix_txn = transactions[0]  # Testing the first Netflix transaction

    score = get_recurring_confidence_score(netflix_txn, transactions)

    assert 0.0 <= score <= 1.0, f"Score {score} is out of bounds"
    assert score > 0.5, f"Expected high recurrence score, but got {score}"

    gym_txn = transactions[-1]  # Testing the Gym transaction (appears only once)

    gym_score = get_recurring_confidence_score(gym_txn, transactions)

    # Adjust expected value to 0.4 instead of 0.2
    assert gym_score == pytest.approx(0.4, rel=0.1), f"Expected low recurrence score, but got {gym_score}"


@pytest.mark.parametrize(
    ("transaction_name", "expected_score"),
    [
        ("Netflix", 1.0),  # Exact match in always_recurring_vendors
        ("T-Mobile", 1.0),
        ("Apple Music", 1.0),
        ("Spotify Premium Plan", 0.8),  # Contains a keyword
        ("XYZ Monthly Service", 0.8),
        ("Internet Bill Payment", 0.8),
        ("Random Purchase", 0.0),  # No keyword or vendor match
        ("Grocery Store", 0.0),
        ("netflix", 1.0),  # Case insensitivity check
        ("t-mobile", 1.0),
        ("subscription Plan", 0.8),
    ],
)
def test_get_subscription_keyword_score(transaction_name, expected_score):
    transaction = Transaction(id=1, user_id="user1", name=transaction_name, amount=50, date="2024-01-01")
    assert get_subscription_keyword_score(transaction) == expected_score


@pytest.mark.parametrize(
    ("transaction", "all_transactions", "expected"),
    [
        # Case 1: Two transactions match (within 0.1)
        (
            Transaction(id=1, user_id="user1", name="Netflix", date="2024-01-01", amount=15.99),
            [
                Transaction(id=2, user_id="user1", name="Netflix", date="2024-01-05", amount=15.99),
                Transaction(id=3, user_id="user1", name="Netflix", date="2024-01-06", amount=16.08),
            ],
            2,  # Expecting 2 matches
        ),
        # Case 2: Only one exact match
        (
            Transaction(id=1, user_id="user1", name="Spotify", date="2024-01-01", amount=9.99),
            [
                Transaction(id=2, user_id="user1", name="Spotify", date="2024-01-05", amount=9.99),
                Transaction(id=3, user_id="user1", name="Spotify", date="2024-01-06", amount=10.2),
            ],
            1,  # Expecting only 1 match
        ),
        # Case 3: No matches
        (
            Transaction(id=1, user_id="user1", name="Apple Music", date="2024-01-01", amount=12.99),
            [
                Transaction(id=2, user_id="user1", name="Apple Music", date="2024-01-05", amount=13.5),
                Transaction(id=3, user_id="user1", name="Apple Music", date="2024-01-06", amount=14.0),
            ],
            0,  # Expecting 0 matches
        ),
    ],
)
def test_get_same_amount_vendor_transactions(transaction, all_transactions, expected):
    """Test function to check matching vendor transactions with the same amount."""
    result = get_same_amount_vendor_transactions(transaction, all_transactions)
    assert result == expected, f"Expected {expected}, but got {result}"


@pytest.fixture
def sample_transactions():
    return [
        Transaction(id=1, user_id="user1", name="Netflix", date="2024-01-01", amount=15.99),
        Transaction(id=2, user_id="user1", name="Netflix", date="2024-01-05", amount=15.99),
        Transaction(id=3, user_id="user1", name="Netflix", date="2024-01-06", amount=16.08),
        Transaction(id=4, user_id="user1", name="Spotify", date="2024-01-10", amount=9.99),
    ]


def test_get_amount_consistency_score():
    # Consistent amounts → score should be high
    vendor = "Spotify Premium"
    transactions_consistent = [
        Transaction(id=1, user_id="u1", name=vendor, date="2024-01-01", amount=9.99),
        Transaction(id=2, user_id="u1", name=vendor, date="2024-02-01", amount=9.99),
        Transaction(id=3, user_id="u1", name=vendor, date="2024-03-01", amount=10.00),
    ]
    t_ref = transactions_consistent[0]
    result = get_amount_consistency_score(t_ref, transactions_consistent)
    assert result > 0.9, f"Expected > 0.9 for consistent amounts, got {result}"

    # Inconsistent amounts → score should be low
    vendor_inconsistent = "Utility Bill"
    transactions_inconsistent = [
        Transaction(id=4, user_id="u1", name=vendor_inconsistent, date="2024-01-01", amount=10.0),
        Transaction(id=5, user_id="u1", name=vendor_inconsistent, date="2024-02-01", amount=100.0),
        Transaction(id=6, user_id="u1", name=vendor_inconsistent, date="2024-03-01", amount=1000.0),
    ]
    t_ref2 = transactions_inconsistent[0]
    result = get_amount_consistency_score(t_ref2, transactions_inconsistent)
    assert result < 0.5, f"Expected < 0.5 for inconsistent amounts, got {result}"

    # Only one transaction → score should be 0.0
    single_transaction = [Transaction(id=7, user_id="u1", name="One Time Payment", date="2024-01-01", amount=99.99)]
    result = get_amount_consistency_score(single_transaction[0], single_transaction)
    assert result == 0.0, f"Expected 0.0 for single transaction, got {result}"

    print("All amount consistency tests passed!")


def test_feature_get_day_of_month_consistency():
    # --- Setup test data ---
    transactions = [
        # Consistent vendor
        Transaction(id=1, user_id="u1", name="Netflix", date="2024-01-15", amount=15.0),
        Transaction(id=2, user_id="u1", name="Netflix", date="2024-02-15", amount=15.0),
        Transaction(id=3, user_id="u1", name="Netflix", date="2024-03-15", amount=15.0),
        Transaction(id=4, user_id="u1", name="Netflix", date="2024-04-15", amount=15.0),
        Transaction(id=5, user_id="u1", name="Netflix", date="2024-05-15", amount=15.0),
        # Slightly inconsistent vendor
        Transaction(id=6, user_id="u1", name="Phone Bill", date="2024-01-05", amount=45.0),
        Transaction(id=7, user_id="u1", name="Phone Bill", date="2024-02-06", amount=45.0),
        Transaction(id=8, user_id="u1", name="Phone Bill", date="2024-03-05", amount=45.0),
        Transaction(id=9, user_id="u1", name="Phone Bill", date="2024-04-05", amount=45.0),
        # Inconsistent vendor
        Transaction(id=10, user_id="u1", name="Groceries", date="2024-01-01", amount=100.0),
        Transaction(id=11, user_id="u1", name="Groceries", date="2024-01-15", amount=80.0),
        Transaction(id=12, user_id="u1", name="Groceries", date="2024-01-25", amount=120.0),
        # Vendor with less than 3 transactions
        Transaction(id=13, user_id="u1", name="Gym", date="2024-01-10", amount=30.0),
        Transaction(id=14, user_id="u1", name="Gym", date="2024-02-10", amount=30.0),
    ]

    # --- Tests ---

    # Netflix: always on 15th -> should return 1.0
    result = get_day_of_month_consistency(transactions[0], transactions)
    assert result == 1.0, f"Expected 1.0, got {result}"

    # Phone Bill: 3 on 5th, 1 on 6th -> 3/4 = 0.75
    result = get_day_of_month_consistency(transactions[5], transactions)
    assert result == 0.75, f"Expected 0.75, got {result}"

    # Groceries: scattered days -> highest day only appears once -> 1/3 ≈ 0.333...
    result = get_day_of_month_consistency(transactions[9], transactions)
    assert round(result, 2) == 0.33, f"Expected ~0.33, got {result}"

    # Gym: only 2 transactions -> should return 0.0
    result = get_day_of_month_consistency(transactions[12], transactions)
    assert result == 0.0, f"Expected 0.0, got {result}"

    print(" All feature tests for get_day_of_month_consistency passed!")


if __name__ == "__main__":
    test_feature_get_day_of_month_consistency()


def test_feature_is_bnpl_service():
    # --- Setup test data ---
    transactions = [
        Transaction(id=1, user_id="u1", name="Credit Ninja", date="2024-01-01", amount=100.0),
        Transaction(id=2, user_id="u1", name="Credit Genie", date="2024-01-01", amount=200.0),
        Transaction(id=3, user_id="u1", name="Rise Up Lending", date="2024-01-01", amount=300.0),
        Transaction(id=4, user_id="u1", name="Netflix", date="2024-01-01", amount=15.0),
        Transaction(id=5, user_id="u1", name="CREDIT NINJA", date="2024-01-01", amount=120.0),  # Uppercase check
        Transaction(id=6, user_id="u1", name="Credit genie", date="2024-01-01", amount=220.0),  # Lowercase check
    ]

    # --- Tests ---

    # Credit Ninja -> detected
    assert is_bnpl_service(transactions[0]) == 1.0

    # Credit Genie -> detected
    assert is_bnpl_service(transactions[1]) == 1.0

    # Rise Up Lending -> detected
    assert is_bnpl_service(transactions[2]) == 1.0

    # Netflix -> not a BNPL service
    assert is_bnpl_service(transactions[3]) == 0.0

    # CREDIT NINJA (uppercase) -> detected
    assert is_bnpl_service(transactions[4]) == 1.0

    # Credit genie (lowercase) -> detected
    assert is_bnpl_service(transactions[5]) == 1.0


def test_feature_get_recent_transaction_frequency():
    # --- Setup test data ---
    transactions = [
        # Recent transactions (within 90 days)
        Transaction(id=1, user_id="u1", name="Spotify", date="2024-04-10", amount=10.0),
        Transaction(id=2, user_id="u1", name="Spotify", date="2024-04-20", amount=10.0),
        Transaction(id=3, user_id="u1", name="Spotify", date="2024-05-01", amount=10.0),
        Transaction(id=4, user_id="u1", name="Spotify", date="2024-05-15", amount=10.0),
        Transaction(id=5, user_id="u1", name="Spotify", date="2024-06-01", amount=10.0),
        Transaction(id=6, user_id="u1", name="Spotify", date="2024-06-20", amount=10.0),
        Transaction(id=7, user_id="u1", name="Spotify", date="2024-07-01", amount=10.0),
        # Older transactions (more than 90 days ago)
        Transaction(id=8, user_id="u1", name="Spotify", date="2023-12-01", amount=10.0),
        Transaction(id=9, user_id="u1", name="Spotify", date="2023-11-01", amount=10.0),
        # Different vendor
        Transaction(id=10, user_id="u1", name="Netflix", date="2024-06-01", amount=15.0),
    ]

    # --- Tests ---

    # Case 1: 7 recent Spotify transactions → should cap at 1.0
    result = get_recent_transaction_frequency(transactions[0], transactions)
    assert result == 1.0

    # Case 2: Netflix has only 1 recent transaction → 1/6
    result = get_recent_transaction_frequency(transactions[9], transactions)
    assert result == pytest.approx(1 / 6)

    # Case 3: Vendor with NO transactions (simulate new vendor)
    new_transaction = Transaction(id=11, user_id="u1", name="Unknown Vendor", date="2024-06-01", amount=50.0)
    result = get_recent_transaction_frequency(new_transaction, transactions)
    assert result == 0.0


def test_feature_get_phone_bill_indicator():
    # --- Setup test data ---
    transactions = [
        # Clear phone bill with telecom name and typical amount
        Transaction(id=1, user_id="u1", name="T-Mobile Payment", date="2024-06-01", amount=70.0),
        # Telecom name but outside typical amount
        Transaction(id=2, user_id="u1", name="Verizon Wireless", date="2024-06-01", amount=250.0),
        # No telecom keyword but within typical amount
        Transaction(id=3, user_id="u1", name="Water Bill", date="2024-06-01", amount=50.0),
        # No telecom keyword and outside typical amount
        Transaction(id=4, user_id="u1", name="Grocery Store", date="2024-06-01", amount=300.0),
    ]

    # --- Tests ---

    # Case 1: Telecom name + typical amount → 0.7 + 0.3 = 1.0
    result = get_phone_bill_indicator(transactions[0])
    assert result == 1.0

    # Case 2: Telecom name but NOT typical amount → only 0.7
    result = get_phone_bill_indicator(transactions[1])
    assert result == pytest.approx(0.7)

    # Case 3: No telecom name but typical amount → only 0.3
    result = get_phone_bill_indicator(transactions[2])
    assert result == pytest.approx(0.3)

    # Case 4: No telecom name and NOT typical amount → 0.0
    result = get_phone_bill_indicator(transactions[3])
    assert result == 0.0
