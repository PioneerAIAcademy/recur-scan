from recur_scan.features_original import (
    get_ends_in_99,
    get_is_always_recurring,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
)
from recur_scan.features_praise import (
    amount_ends_in_00,
    amount_ends_in_99,
    # calculate_amount_to_income_ratio,
    calculate_markovian_probability,
    calculate_streaks,
    # compare_recent_to_historical_average,
    # detect_seasonality,
    get_average_transaction_amount,
    get_avg_days_between_same_merchant_amount,
    get_days_since_last_same_merchant_amount,
    get_ewma_interval_deviation,
    get_fourier_periodicity_score,
    get_hurst_exponent,
    get_interval_variance_coefficient,
    get_max_transaction_amount,
    get_min_transaction_amount,
    get_most_frequent_names,
    get_n_transactions_same_merchant_amount,
    get_percent_transactions_same_merchant_amount,
    get_stddev_days_between_same_merchant_amount,
    # get_transaction_amount_trend,
    has_consistent_reference_codes,
    has_incrementing_numbers,
    is_expected_transaction_date,
    is_recurring,
    is_recurring_merchant,
    # is_recurring_through_past_transactions,
)
from recur_scan.transactions import Transaction


# Helper function to create transactions
def create_transaction(id, user_id, name, date, amount):
    return Transaction(id=id, user_id=user_id, name=name, date=date, amount=amount)


def test_get_n_transactions_same_amount() -> None:
    """Test that get_n_transactions_same_amount returns the correct number of transactions with the same amount."""
    transactions = [
        create_transaction(1, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(2, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(3, "user1", "name1", "2024-01-02", 200.0),
        create_transaction(4, "user1", "name1", "2024-01-03", 2.99),
    ]
    assert get_n_transactions_same_amount(transactions[0], transactions) == 2
    assert get_n_transactions_same_amount(transactions[2], transactions) == 1


def test_get_percent_transactions_same_amount() -> None:
    """Test that get_percent_transactions_same_amount returns correct percentage."""
    transactions = [
        create_transaction(1, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(2, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(3, "user1", "name1", "2024-01-02", 200.0),
        create_transaction(4, "user1", "name1", "2024-01-03", 2.99),
    ]
    assert get_percent_transactions_same_amount(transactions[0], transactions) == 0.5  # 2/4


def test_is_recurring_merchant() -> None:
    """Test that is_recurring_merchant returns True for recurring merchants."""
    transaction = create_transaction(1, "user1", "Google Play", "2023-01-01", 10.00)
    assert is_recurring_merchant(transaction)
    transaction = create_transaction(2, "user1", "Local Store", "2023-01-02", 9.99)
    assert not is_recurring_merchant(transaction)


def test_get_avg_days_between_same_merchant_amount() -> None:
    """Test get_avg_days_between_same_merchant_amount returns correct average days."""
    transactions = [
        create_transaction(1, "user1", "VendorA", "2023-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2023-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2023-01-15", 100.0),
    ]
    transaction = transactions[0]
    assert get_avg_days_between_same_merchant_amount(transaction, transactions) == 7.0


def test_get_is_always_recurring() -> None:
    """Test get_is_always_recurring identifies recurring vendors."""
    transaction = create_transaction(1, "user1", "Netflix", "2024-01-01", 15.99)
    assert get_is_always_recurring(transaction)
    transaction = create_transaction(2, "user1", "Local Store", "2024-01-02", 9.99)
    assert not get_is_always_recurring(transaction)


def test_get_is_utility() -> None:
    """Test get_is_utility identifies utility payments."""
    transaction = create_transaction(1, "user1", "Electric Utility", "2024-01-01", 75.0)
    assert get_is_utility(transaction)
    transaction = create_transaction(2, "user1", "Restaurant", "2024-01-02", 30.0)
    assert not get_is_utility(transaction)


def test_get_is_phone() -> None:
    """Test get_is_phone identifies phone payments."""
    transaction = create_transaction(1, "user1", "AT&T Wireless", "2024-01-01", 60.0)
    assert get_is_phone(transaction)
    transaction = create_transaction(2, "user1", "Coffee Shop", "2024-01-02", 5.0)
    assert not get_is_phone(transaction)


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


def test_get_n_transactions_same_day() -> None:
    """Test get_n_transactions_same_day counts transactions on same day of month."""
    transactions = [
        create_transaction(1, "user1", "Netflix", "2024-01-01", 15.99),
        create_transaction(2, "user1", "Netflix", "2024-02-01", 15.99),
        create_transaction(3, "user1", "Netflix", "2024-03-03", 15.99),
    ]
    transaction = transactions[0]
    assert get_n_transactions_same_day(transaction, transactions, 1) == 2


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


def test_get_pct_transactions_same_day() -> None:
    """Test get_pct_transactions_same_day calculates correct percentage."""
    transactions = [
        create_transaction(1, "user1", "Netflix", "2024-01-01", 15.99),
        create_transaction(2, "user1", "Netflix", "2024-02-01", 15.99),
        create_transaction(3, "user1", "Netflix", "2024-03-03", 15.99),
    ]
    transaction = transactions[0]
    assert get_pct_transactions_same_day(transaction, transactions, 1) == 2 / 3


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


def test_get_average_transaction_amount() -> None:
    """Test get_average_transaction_amount calculates correct average."""
    transactions = [
        create_transaction(1, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(2, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(3, "user1", "name1", "2024-01-02", 200.0),
        create_transaction(4, "user1", "name1", "2024-01-03", 2.99),
    ]
    # (100 + 100 + 200 + 2.99) / 4 = 100.7475 ≈ 100.75
    assert round(get_average_transaction_amount(transactions), 2) == 100.75


def test_get_max_transaction_amount() -> None:
    """Test get_max_transaction_amount identifies maximum amount."""
    transactions = [
        create_transaction(1, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(2, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(3, "user1", "name1", "2024-01-02", 200.0),
        create_transaction(4, "user1", "name1", "2024-01-03", 2.99),
    ]
    assert get_max_transaction_amount(transactions) == 200.0


def test_get_min_transaction_amount() -> None:
    """Test get_min_transaction_amount identifies minimum amount."""
    transactions = [
        create_transaction(1, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(2, "user1", "name1", "2024-01-01", 100.0),
        create_transaction(3, "user1", "name1", "2024-01-02", 200.0),
        create_transaction(4, "user1", "name1", "2024-01-03", 2.99),
    ]
    assert get_min_transaction_amount(transactions) == 2.99


def test_get_most_frequent_names() -> None:
    """Test get_most_frequent_names identifies merchants with multiple amounts."""
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 10.0),  # Same amount
        create_transaction(3, "user1", "StoreA", "2024-01-03", 20.0),  # Different amount
        create_transaction(4, "user1", "StoreB", "2024-01-04", 30.0),
    ]
    # StoreA has transactions with same amount (10.0) and different amounts (10.0 and 20.0)
    assert len(get_most_frequent_names(transactions)) == 1  # StoreA has multiple amounts


def test_is_recurring() -> None:
    """Test is_recurring identifies recurring transactions."""
    transactions = [
        create_transaction(1, "user1", "Netflix", "2024-01-01", 15.99),
        create_transaction(2, "user1", "Netflix", "2024-02-01", 15.99),
        create_transaction(3, "user1", "Netflix", "2024-03-01", 15.99),
    ]
    transaction = transactions[0]
    assert is_recurring(transaction, transactions)


def test_amount_ends_in_99() -> None:
    """Test that amount_ends_in_99 correctly identifies amounts ending with .99"""
    # Test positive case
    transaction = create_transaction(1, "user1", "Store", "2024-01-01", 9.99)
    assert amount_ends_in_99(transaction), "Should detect amount ending with .99"
    # Test negative cases
    transaction = create_transaction(2, "user1", "Store", "2024-01-02", 10.00)
    assert not amount_ends_in_99(transaction), "Should not detect amount ending with .00"
    transaction = create_transaction(3, "user1", "Store", "2024-01-03", 10.98)
    assert not amount_ends_in_99(transaction), "Should not detect amount ending with .98"


def test_amount_ends_in_00() -> None:
    """Test amount_ends_in_00 correctly identifies .00 amounts"""
    transaction = create_transaction(1, "user1", "Store", "2024-01-01", 10.00)
    assert amount_ends_in_00(transaction)
    transaction = create_transaction(2, "user1", "Store", "2024-01-02", 10.01)
    assert not amount_ends_in_00(transaction)


def test_get_n_transactions_same_merchant_amount() -> None:
    """Test counting transactions with same merchant and amount"""
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-01-15", 200.0),
    ]
    transaction = transactions[0]
    assert get_n_transactions_same_merchant_amount(transaction, transactions) == 2


def test_get_percent_transactions_same_merchant_amount() -> None:
    """Test percentage of transactions with same merchant/amount"""
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
        create_transaction(3, "user1", "VendorB", "2024-01-15", 100.0),
    ]
    transaction = transactions[0]
    assert get_percent_transactions_same_merchant_amount(transaction, transactions) == 2 / 3


def test_get_interval_variance_coefficient() -> None:
    """Test interval consistency measurement"""
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0),
    ]
    transaction = transactions[0]
    assert get_interval_variance_coefficient(transaction, transactions) == 0.0  # Perfectly consistent


def test_get_stddev_days_between_same_merchant_amount() -> None:
    """Test standard deviation of transaction intervals"""
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0),
    ]
    transaction = transactions[0]
    assert get_stddev_days_between_same_merchant_amount(transaction, transactions) == 0.0


def test_get_days_since_last_same_merchant_amount() -> None:
    """Test days since last same merchant/amount transaction"""
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0),
    ]
    transaction = transactions[2]
    assert get_days_since_last_same_merchant_amount(transaction, transactions) == 7


def test_is_expected_transaction_date() -> None:
    """Test if transaction occurs on expected date"""
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0),
    ]
    transaction = transactions[2]
    assert is_expected_transaction_date(transaction, transactions)


def test_has_incrementing_numbers() -> None:
    """Test detection of incrementing numbers in transaction names"""
    transactions = [
        create_transaction(1, "user1", "Payment #1001", "2024-01-01", 50.0),
        create_transaction(2, "user1", "Payment #1002", "2024-01-08", 50.0),
        create_transaction(3, "user1", "Payment #1003", "2024-01-15", 50.0),
    ]
    transaction = transactions[0]
    assert has_incrementing_numbers(transaction, transactions), (
        "Should detect incrementing numbers in Payment #1001, #1002, #1003"
    )
    # Test negative case
    transactions = [
        create_transaction(1, "user1", "Payment #1001", "2024-01-01", 50.0),
        create_transaction(2, "user1", "Payment #1005", "2024-01-08", 50.0),
        create_transaction(3, "user1", "Payment #1010", "2024-01-15", 50.0),
    ]
    transaction = transactions[0]
    assert not has_incrementing_numbers(transaction, transactions), (
        "Should not detect incrementing numbers with inconsistent jumps"
    )


def test_has_consistent_reference_codes() -> None:
    """Test detection of consistent reference codes"""
    transactions = [
        create_transaction(1, "user1", "Payment REF:ABC123", "2024-01-01", 50.0),
        create_transaction(2, "user1", "Payment REF:ABC123", "2024-01-08", 50.0),
    ]
    transaction = transactions[0]
    assert has_consistent_reference_codes(transaction, transactions)


# def test_is_recurring_through_past_transactions() -> None:
#     """Test if is_recurring_through_past_transactions identifies recurring transactions."""
#     transactions = [
#         create_transaction(1, "user1", "Netflix", "2024-01-01", 15.99),  # Monday
#         create_transaction(2, "user1", "Netflix", "2024-01-08", 15.99),  # Monday
#         create_transaction(3, "user1", "Netflix", "2024-01-15", 15.99),  # Monday
#         create_transaction(4, "user1", "Netflix", "2024-01-22", 15.99),  # Monday
#     ]
#     transaction = transactions[0]
#     assert is_recurring_through_past_transactions(transaction, transactions), (
#         "Should detect recurring transactions on the same day of the week"
#     )

#     # Test non-recurring case
#     transactions = [
#         create_transaction(1, "user1", "Netflix", "2024-01-01", 15.99),  # Monday
#         create_transaction(2, "user1", "Netflix", "2024-01-09", 15.99),  # Tuesday
#         create_transaction(3, "user1", "Netflix", "2024-01-15", 15.99),  # Monday
#     ]
#     transaction = transactions[0]
#     assert not is_recurring_through_past_transactions(transaction, transactions), (
#         "Should not detect recurring transactions with inconsistent days of the week"
#     )


# def test_get_transaction_amount_trend() -> None:
#     """Test get_transaction_amount_trend calculates the correct trend (slope)."""
#     transactions = [
#         create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
#         create_transaction(2, "user1", "VendorA", "2024-01-08", 200.0),
#         create_transaction(3, "user1", "VendorA", "2024-01-15", 300.0),
#     ]
#     transaction = transactions[0]
#     assert get_transaction_amount_trend(transaction, transactions) > 0, (
#         "Trend should be positive for increasing amounts"
#     )

#     # Test flat trend
#     transactions = [
#         create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
#         create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
#         create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0),
#     ]
#     transaction = transactions[0]
#     assert get_transaction_amount_trend(transaction, transactions) == 0.0, "Trend should be zero for flat amounts"

#     # Test insufficient data
#     transactions = [
#         create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
#     ]
#     transaction = transactions[0]
#     assert get_transaction_amount_trend(transaction, transactions) == 0.0, (
#         "Trend should be zero for insufficient data"
#     )


# def test_compare_recent_to_historical_average() -> None:
#     """Test compare_recent_to_historical_average calculates the correct ratio."""
#     transactions = [
#         create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
#         create_transaction(2, "user1", "VendorA", "2024-01-08", 200.0),
#         create_transaction(3, "user1", "VendorA", "2024-01-15", 300.0),
#     ]
#     transaction = create_transaction(4, "user1", "VendorA", "2024-01-22", 400.0)
#     assert compare_recent_to_historical_average(transaction, transactions) == 2.0, (
#         "Ratio should be 2.0 when the recent amount is double the historical average"
#     )

#     # Test when no historical data is available
#     transactions = []
#     transaction = create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0)
#     assert compare_recent_to_historical_average(transaction, transactions) == 0.0, (
#         "Ratio should be 0.0 when no historical data is available"
#     )

#     # Test when historical average is zero
#     transactions = [
#         create_transaction(1, "user1", "VendorA", "2024-01-01", 0.0),
#         create_transaction(2, "user1", "VendorA", "2024-01-08", 0.0),
#     ]
#     transaction = create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0)
#     assert compare_recent_to_historical_average(transaction, transactions) == 0.0, (
#         "Ratio should be 0.0 when historical average is zero"
#     )


# def test_calculate_amount_to_income_ratio() -> None:
#     """Test calculate_amount_to_income_ratio calculates the correct ratio."""
#     transaction = create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0)

#     # Test with valid monthly income
#     assert calculate_amount_to_income_ratio(transaction, 1000.0) == 0.1, (
#         "Ratio should be 0.1 when transaction amount is 10% of monthly income"
#     )

#     # Test with zero monthly income
#     assert calculate_amount_to_income_ratio(transaction, 0.0) == 0.0, (
#         "Ratio should be 0.0 when monthly income is zero"
#     )

#     # Test with negative monthly income
#     assert calculate_amount_to_income_ratio(transaction, -1000.0) == 0.0, (
#         "Ratio should be 0.0 when monthly income is negative"
#     )


# def test_detect_seasonality() -> None:
#     """Test detect_seasonality identifies annual or quarterly patterns."""
#     # Test annual pattern
#     transactions = [
#         create_transaction(1, "user1", "VendorA", "2023-01-01", 100.0),
#         create_transaction(2, "user1", "VendorA", "2024-01-01", 100.0),
#     ]
#     transaction = transactions[0]
#     assert detect_seasonality(transaction, transactions), (
#         "Should detect annual seasonality for transactions 365 days apart"
#     )

#     # Test quarterly pattern
#     transactions = [
#         create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
#         create_transaction(2, "user1", "VendorA", "2024-04-01", 100.0),
#     ]
#     transaction = transactions[0]
#     assert detect_seasonality(transaction, transactions), (
#         "Should detect quarterly seasonality for transactions 90 days apart"
#     )

#     # Test no seasonality
#     transactions = [
#         create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
#         create_transaction(2, "user1", "VendorA", "2024-02-01", 100.0),
#     ]
#     transaction = transactions[0]
#     assert not detect_seasonality(transaction, transactions), (
#         "Should not detect seasonality for transactions with irregular intervals"
#     )

#     # Test insufficient data
#     transactions = [
#         create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
#     ]
#     transaction = transactions[0]
#     assert not detect_seasonality(transaction, transactions), (
#         "Should not detect seasonality with less than two transactions"
#     )


def test_calculate_markovian_probability() -> None:
    """Test calculate_markovian_probability calculates the correct probability."""
    # Test with a matching pattern
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0),
        create_transaction(4, "user1", "VendorA", "2024-01-22", 100.0),
    ]
    transaction = transactions[0]
    assert calculate_markovian_probability(transaction, transactions, n=3) == 1.0, (
        "Should return 1.0 for matching patterns in the last n transactions"
    )

    # Test with a non-matching pattern
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 200.0),
        create_transaction(3, "user1", "VendorA", "2024-01-15", 300.0),
        create_transaction(4, "user1", "VendorA", "2024-01-22", 400.0),
    ]
    transaction = transactions[0]
    assert calculate_markovian_probability(transaction, transactions, n=3) == 0.0, (
        "Should return 0.0 for non-matching patterns in the last n transactions"
    )

    # Test with insufficient data
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
    ]
    transaction = transactions[0]
    assert calculate_markovian_probability(transaction, transactions, n=3) == 0.0, (
        "Should return 0.0 when there is insufficient data"
    )


def test_calculate_streaks() -> None:
    """Test calculate_streaks calculates the correct number of consecutive transactions."""
    # Test with a streak of weekly transactions
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0),
        create_transaction(4, "user1", "VendorA", "2024-01-22", 100.0),
    ]
    transaction = transactions[0]
    assert calculate_streaks(transaction, transactions) == 3, "Should return 3 for a streak of weekly transactions"

    # Test with a streak of monthly transactions
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-02-01", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-03-01", 100.0),
    ]
    transaction = transactions[0]
    assert calculate_streaks(transaction, transactions) == 2, "Should return 2 for a streak of monthly transactions"

    # Test with no streak
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-10", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-01-25", 100.0),
    ]
    transaction = transactions[0]
    assert calculate_streaks(transaction, transactions) == 0, "Should return 0 for no streak of transactions"

    # Test with insufficient data
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
    ]
    transaction = transactions[0]
    assert calculate_streaks(transaction, transactions) == 0, "Should return 0 when there is insufficient data"


def test_get_ewma_interval_deviation():
    """Test get_ewma_interval_deviation calculates correct deviation."""
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0),
    ]
    transaction = create_transaction(4, "user1", "VendorA", "2024-01-22", 100.0)
    assert round(get_ewma_interval_deviation(transaction, transactions), 2) == 0.0, (
        "Deviation should be 0.0 for perfectly consistent intervals"
    )

    # Test with inconsistent intervals
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-10", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-01-20", 100.0),
    ]
    transaction = create_transaction(4, "user1", "VendorA", "2024-01-30", 100.0)
    assert get_ewma_interval_deviation(transaction, transactions) > 0.0, (
        "Deviation should be greater than 0.0 for inconsistent intervals"
    )

    # Test with insufficient data
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
    ]
    transaction = create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0)
    assert get_ewma_interval_deviation(transaction, transactions) == 1.0, (
        "Deviation should be 1.0 when there is insufficient data"
    )


def test_get_hurst_exponent():
    """Test get_hurst_exponent calculates correct Hurst exponent."""
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0),
        create_transaction(4, "user1", "VendorA", "2024-01-22", 100.0),
    ]
    transaction = create_transaction(5, "user1", "VendorA", "2024-01-29", 100.0)
    assert 0.5 <= get_hurst_exponent(transaction, transactions) <= 1.0, (
        "Hurst exponent should be between 0.5 and 1.0 for consistent intervals"
    )

    # Test with insufficient data
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
    ]
    transaction = create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0)
    assert get_hurst_exponent(transaction, transactions) == 0.5, (
        "Hurst exponent should be 0.5 when there is insufficient data"
    )


def test_get_fourier_periodicity_score():
    """Test get_fourier_periodicity_score calculates correct periodicity score."""
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
        create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0),
        create_transaction(4, "user1", "VendorA", "2024-01-22", 100.0),
        create_transaction(5, "user1", "VendorA", "2024-01-29", 100.0),
        create_transaction(6, "user1", "VendorA", "2024-02-05", 100.0),
    ]
    transaction = create_transaction(7, "user1", "VendorA", "2024-02-12", 100.0)
    assert 0.0 <= get_fourier_periodicity_score(transaction, transactions) <= 1.0, (
        "Periodicity score should be between 0.0 and 1.0"
    )

    # Test with insufficient data
    transactions = [
        create_transaction(1, "user1", "VendorA", "2024-01-01", 100.0),
        create_transaction(2, "user1", "VendorA", "2024-01-08", 100.0),
    ]
    transaction = create_transaction(3, "user1", "VendorA", "2024-01-15", 100.0)
    assert get_fourier_periodicity_score(transaction, transactions) == 0.0, (
        "Periodicity score should be 0.0 when there is insufficient data"
    )
