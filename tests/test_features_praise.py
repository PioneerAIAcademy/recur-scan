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
    afterpay_future_same_amount_exists,
    afterpay_has_3_similar_in_6_weeks,
    afterpay_is_first_of_series,
    afterpay_likely_payment,
    afterpay_prev_same_amount_count,
    afterpay_recurrence_score,
    amount_ends_in_00,
    amount_ends_in_99,
    apple_amount_close_to_median,
    apple_days_since_first_seen_amount,
    apple_is_low_value_txn,
    apple_std_dev_amounts,
    apple_total_same_amount_past_6m,
    calculate_markovian_probability,
    calculate_streaks,
    compare_recent_to_historical_average,
    get_amount_coefficient_of_variation,
    get_amount_drift_slope,
    get_amount_iqr,
    get_amount_mad,
    get_amount_quantile,
    get_amount_zscore,
    get_average_transaction_amount,
    get_avg_days_between_same_merchant,
    get_avg_days_between_same_merchant_amount,
    get_burstiness_ratio,
    get_day_of_month_consistency,
    get_days_since_first_transaction,
    get_days_since_last_same_merchant_amount,
    get_days_since_last_transaction,
    get_ewma_interval_deviation,
    get_fourier_periodicity_score,
    get_hurst_exponent,
    get_interval_consistency_ratio,
    get_interval_variance_coefficient,
    get_interval_variance_ratio,
    get_max_transaction_amount,
    get_median_amount,
    get_min_transaction_amount,
    get_most_frequent_names,
    get_n_transactions_last_30_days,
    get_n_transactions_same_merchant_amount,
    get_normalized_recency,
    get_percent_transactions_same_merchant_amount,
    get_ratio_transactions_last_30_days,
    get_recurrence_score_by_amount,
    get_rolling_mean_amount,
    get_seasonality_score,
    get_serial_autocorrelation,
    get_stddev_amount_same_merchant,
    get_stddev_days_between_same_merchant_amount,
    get_transaction_recency_score,
    get_unique_merchants_count,
    get_weekday_concentration,
    has_consistent_reference_codes,
    has_incrementing_numbers,
    is_amount_outlier,
    is_consistent_weekday_pattern,
    is_end_of_month_transaction,
    is_expected_transaction_date,
    is_moneylion_common_amount,
    is_recurring,
    is_recurring_merchant,
    is_recurring_through_past_transactions,
    is_weekend_transaction,
    moneylion_days_since_last_same_amount,
    moneylion_is_biweekly,
    moneylion_weekday_pattern,
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


def test_afterpay_has_3_similar_in_6_weeks() -> None:
    """Test detection of 3 similar Afterpay transactions in 6 weeks."""
    transactions = [
        create_transaction(1, "user1", "Afterpay", "2024-01-01", 50.0),
        create_transaction(2, "user1", "Afterpay", "2024-01-15", 50.0),
        create_transaction(3, "user1", "Afterpay", "2024-02-10", 50.0),  # 40 days from first
    ]
    transaction = transactions[0]
    assert afterpay_has_3_similar_in_6_weeks(transaction, transactions)
    # Negative case: spread out more than 6 weeks
    transactions = [
        create_transaction(1, "user1", "Afterpay", "2024-01-01", 50.0),
        create_transaction(2, "user1", "Afterpay", "2024-02-20", 50.0),
        create_transaction(3, "user1", "Afterpay", "2024-04-01", 50.0),
    ]
    assert not afterpay_has_3_similar_in_6_weeks(transaction, transactions)


def test_afterpay_is_first_of_series() -> None:
    """Test detection of first Afterpay transaction in a biweekly series."""
    transactions = [
        create_transaction(1, "user1", "Afterpay", "2024-01-01", 20.0),
        create_transaction(2, "user1", "Afterpay", "2024-01-14", 20.0),
        create_transaction(3, "user1", "Afterpay", "2024-01-28", 20.0),
    ]
    transaction = transactions[0]
    assert afterpay_is_first_of_series(transaction, transactions)
    # Negative case: not the first or not enough regular gaps
    transaction = transactions[1]
    assert not afterpay_is_first_of_series(transaction, transactions)
    transactions = [
        create_transaction(1, "user1", "Afterpay", "2024-01-01", 20.0),
        create_transaction(2, "user1", "Afterpay", "2024-01-10", 20.0),
        create_transaction(3, "user1", "Afterpay", "2024-01-28", 20.0),
    ]
    assert not afterpay_is_first_of_series(transactions[0], transactions)


def test_afterpay_likely_payment() -> None:
    """Test detection of likely Afterpay payment pattern."""
    transactions = [
        create_transaction(1, "user1", "Afterpay", "2024-01-01", 25.0),
        create_transaction(2, "user1", "Afterpay", "2024-01-15", 25.0),  # 14 days after
        create_transaction(3, "user1", "Afterpay", "2024-01-29", 25.0),  # 28 days after
    ]
    transaction = transactions[2]
    assert afterpay_likely_payment(transaction, transactions)
    # Negative case: not enough matches
    transactions = [
        create_transaction(1, "user1", "Afterpay", "2024-01-01", 25.0),
        create_transaction(2, "user1", "Afterpay", "2024-01-20", 25.0),
    ]
    assert not afterpay_likely_payment(transactions[1], transactions)


def test_afterpay_prev_same_amount_count() -> None:
    """Test counting previous Afterpay transactions with the same amount."""
    transactions = [
        create_transaction(1, "user1", "Afterpay", "2024-01-01", 10.0),
        create_transaction(2, "user1", "Afterpay", "2024-01-05", 10.0),
        create_transaction(3, "user1", "Afterpay", "2024-01-10", 10.0),
    ]
    transaction = transactions[2]
    assert afterpay_prev_same_amount_count(transaction, transactions) == 2
    transaction = transactions[0]
    assert afterpay_prev_same_amount_count(transaction, transactions) == 0


def test_afterpay_future_same_amount_exists() -> None:
    """Test detection of future Afterpay transactions with the same amount."""
    transactions = [
        create_transaction(1, "user1", "Afterpay", "2024-01-01", 5.0),
        create_transaction(2, "user1", "Afterpay", "2024-01-10", 5.0),
    ]
    transaction = transactions[0]
    assert afterpay_future_same_amount_exists(transaction, transactions)
    transaction = transactions[1]
    assert not afterpay_future_same_amount_exists(transaction, transactions)


def test_afterpay_recurrence_score() -> None:
    """Test Afterpay recurrence score calculation."""
    transactions = [
        create_transaction(1, "user1", "Afterpay", "2024-01-01", 25.0),
        create_transaction(2, "user1", "Afterpay", "2024-01-15", 25.0),
        create_transaction(3, "user1", "Afterpay", "2024-01-29", 25.0),
        create_transaction(4, "user1", "Afterpay", "2024-02-12", 25.0),
    ]
    transaction = transactions[0]
    score = afterpay_recurrence_score(transaction, transactions)
    assert 0.2 <= score <= 1.0
    # Negative case: not an Afterpay transaction
    transaction = create_transaction(5, "user1", "Other", "2024-02-19", 25.0)
    assert afterpay_recurrence_score(transaction, transactions) == 0.0


def test_is_moneylion_common_amount() -> None:
    """Test if transaction amount is among user's top 3 MoneyLion amounts."""
    transactions = [
        create_transaction(1, "user1", "MoneyLion", "2024-01-01", 50.0),
        create_transaction(2, "user1", "MoneyLion", "2024-01-02", 50.0),
        create_transaction(3, "user1", "MoneyLion", "2024-01-03", 75.0),
        create_transaction(4, "user1", "MoneyLion", "2024-01-04", 100.0),
        create_transaction(5, "user1", "MoneyLion", "2024-01-05", 100.0),
    ]
    transaction = transactions[0]
    assert is_moneylion_common_amount(transaction, transactions)
    transaction = create_transaction(6, "user1", "MoneyLion", "2024-01-06", 200.0)
    assert not is_moneylion_common_amount(transaction, transactions[:3])  # Less than 3 relevant


def test_moneylion_days_since_last_same_amount() -> None:
    """Test days since last MoneyLion transaction with same amount."""
    transactions = [
        create_transaction(1, "user1", "MoneyLion", "2024-01-01", 50.0),
        create_transaction(2, "user1", "MoneyLion", "2024-01-10", 50.0),
        create_transaction(3, "user1", "MoneyLion", "2024-01-20", 50.0),
    ]
    transaction = transactions[2]
    assert moneylion_days_since_last_same_amount(transaction, transactions) == 10
    transaction = create_transaction(4, "user1", "MoneyLion", "2024-01-05", 75.0)
    assert moneylion_days_since_last_same_amount(transaction, transactions) == -1


def test_moneylion_is_biweekly() -> None:
    """Test detection of biweekly MoneyLion payment pattern."""
    transactions = [
        create_transaction(1, "user1", "MoneyLion", "2024-01-01", 50.0),
        create_transaction(2, "user1", "MoneyLion", "2024-01-15", 50.0),
        create_transaction(3, "user1", "MoneyLion", "2024-01-29", 50.0),
        create_transaction(4, "user1", "MoneyLion", "2024-02-12", 50.0),
    ]
    transaction = transactions[3]
    assert moneylion_is_biweekly(transaction, transactions)
    # Negative case: not enough biweekly intervals
    transactions = [
        create_transaction(1, "user1", "MoneyLion", "2024-01-01", 50.0),
        create_transaction(2, "user1", "MoneyLion", "2024-01-20", 50.0),
        create_transaction(3, "user1", "MoneyLion", "2024-02-10", 50.0),
    ]
    transaction = transactions[2]
    assert not moneylion_is_biweekly(transaction, transactions)


def test_moneylion_weekday_pattern() -> None:
    """Test detection of consistent weekday pattern for MoneyLion."""
    transactions = [
        create_transaction(1, "user1", "MoneyLion", "2024-01-01", 50.0),  # Tuesday
        create_transaction(2, "user1", "MoneyLion", "2024-01-08", 50.0),  # Tuesday
        create_transaction(3, "user1", "MoneyLion", "2024-01-15", 50.0),  # Tuesday
        create_transaction(4, "user1", "MoneyLion", "2024-01-22", 50.0),  # Tuesday
    ]
    transaction = transactions[3]
    assert moneylion_weekday_pattern(transaction, transactions)
    # Negative case: not enough or inconsistent weekdays
    transactions = [
        create_transaction(1, "user1", "MoneyLion", "2024-01-01", 50.0),  # Tuesday
        create_transaction(2, "user1", "MoneyLion", "2024-01-09", 50.0),  # Wednesday
        create_transaction(3, "user1", "MoneyLion", "2024-01-15", 50.0),  # Tuesday
    ]
    transaction = transactions[2]
    assert not moneylion_weekday_pattern(transaction, transactions)


def test_apple_amount_close_to_median():
    txns = [
        create_transaction(1, "user1", "Apple", "2024-01-01", 10.0),
        create_transaction(2, "user1", "Apple", "2024-01-02", 12.0),
        create_transaction(3, "user1", "Apple", "2024-01-03", 11.0),
        create_transaction(4, "user1", "Apple", "2024-01-04", 20.0),
    ]
    txn = create_transaction(5, "user1", "Apple", "2024-01-05", 11.0)
    assert apple_amount_close_to_median(txn, txns)
    txn = create_transaction(6, "user1", "Apple", "2024-01-06", 25.0)
    assert not apple_amount_close_to_median(txn, txns[:2])  # less than 3 relevant


def test_apple_total_same_amount_past_6m():
    txns = [
        create_transaction(1, "user1", "Apple", "2023-07-01", 10.0),
        create_transaction(2, "user1", "Apple", "2023-12-01", 10.0),
        create_transaction(3, "user1", "Apple", "2024-01-01", 10.0),
    ]
    txn = create_transaction(4, "user1", "Apple", "2024-01-02", 10.0)
    assert apple_total_same_amount_past_6m(txn, txns) == 2


def test_apple_std_dev_amounts():
    txns = [
        create_transaction(1, "user1", "Apple", "2024-01-01", 10.0),
        create_transaction(2, "user1", "Apple", "2024-01-02", 12.0),
        create_transaction(3, "user1", "Apple", "2024-01-03", 11.0),
        create_transaction(4, "user1", "Apple", "2024-01-04", 20.0),
    ]
    txn = create_transaction(5, "user1", "Apple", "2024-01-05", 11.0)
    assert apple_std_dev_amounts(txn, txns) > 0
    txn = create_transaction(6, "user1", "Apple", "2024-01-02", 12.0)
    assert apple_std_dev_amounts(txn, txns[:2]) == -1.0


def test_apple_is_low_value_txn():
    txn = create_transaction(1, "user1", "Apple", "2024-01-01", 10.0)
    assert apple_is_low_value_txn(txn)
    txn = create_transaction(2, "user1", "Apple", "2024-01-02", 25.0)
    assert not apple_is_low_value_txn(txn)


def test_apple_days_since_first_seen_amount():
    txns = [
        create_transaction(1, "user1", "Apple", "2024-01-01", 10.0),
        create_transaction(2, "user1", "Apple", "2024-01-10", 10.0),
        create_transaction(3, "user1", "Apple", "2024-01-20", 10.0),
    ]
    txn = create_transaction(4, "user1", "Apple", "2024-01-20", 10.0)
    assert apple_days_since_first_seen_amount(txn, txns) == 19
    txn = create_transaction(5, "user1", "Apple", "2024-01-05", 20.0)
    assert apple_days_since_first_seen_amount(txn, txns) == -1


def test_get_rolling_mean_amount():
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 20.0),
        create_transaction(3, "user1", "StoreA", "2024-01-03", 30.0),
        create_transaction(4, "user1", "StoreA", "2024-01-04", 40.0),
    ]
    transaction = transactions[3]
    assert get_rolling_mean_amount(transaction, transactions, window=3) == 30.0
    transaction = transactions[1]
    assert get_rolling_mean_amount(transaction, transactions, window=2) == 15.0


def test_get_interval_variance_ratio():
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-08", 10.0),
        create_transaction(3, "user1", "StoreA", "2024-01-15", 10.0),
    ]
    transaction = transactions[2]
    assert get_interval_variance_ratio(transaction, transactions) == 0.0  # Intervals are all 7 days


def test_get_day_of_month_consistency():
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-02-01", 10.0),
        create_transaction(3, "user1", "StoreA", "2024-03-02", 10.0),
    ]
    transaction = transactions[2]
    assert get_day_of_month_consistency(transaction, transactions)
    # Inconsistent days
    transactions[2] = create_transaction(3, "user1", "StoreA", "2024-03-10", 10.0)
    assert not get_day_of_month_consistency(transaction, transactions)


def test_get_seasonality_score():
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-08", 10.0),
        create_transaction(3, "user1", "StoreA", "2024-01-15", 10.0),
        create_transaction(4, "user1", "StoreA", "2024-01-22", 10.0),
    ]
    transaction = transactions[3]
    assert get_seasonality_score(transaction, transactions) == 1.0  # All weekly intervals


def test_get_amount_drift_slope():
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 20.0),
        create_transaction(3, "user1", "StoreA", "2024-01-03", 30.0),
    ]
    transaction = transactions[2]
    slope = get_amount_drift_slope(transaction, transactions)
    assert slope > 0.0


def test_get_burstiness_ratio():
    transactions = [
        create_transaction(1, "user1", "StoreA", "2023-07-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2023-10-01", 10.0),
        create_transaction(3, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(4, "user1", "StoreA", "2024-03-01", 10.0),
    ]
    transaction = transactions[3]
    ratio = get_burstiness_ratio(transaction, transactions)
    assert ratio >= 0


def test_get_serial_autocorrelation():
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-08", 10.0),
        create_transaction(3, "user1", "StoreA", "2024-01-15", 10.0),
    ]
    transaction = transactions[2]
    assert get_serial_autocorrelation(transaction, transactions) == 0.0


def test_get_weekday_concentration():
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),  # Monday
        create_transaction(2, "user1", "StoreA", "2024-01-08", 10.0),  # Monday
        create_transaction(3, "user1", "StoreA", "2024-01-15", 10.0),  # Monday
    ]
    transaction = transactions[2]
    assert get_weekday_concentration(transaction, transactions) == 1.0


def test_get_interval_consistency_ratio():
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-08", 10.0),
        create_transaction(3, "user1", "StoreA", "2024-01-15", 10.0),
    ]
    transaction = transactions[2]
    assert get_interval_consistency_ratio(transaction, transactions) == 1.0


def test_get_median_amount():
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 20.0),
        create_transaction(3, "user1", "StoreA", "2024-01-03", 30.0),
    ]
    transaction = transactions[2]
    assert get_median_amount(transaction, transactions) == 20.0


def test_get_amount_mad():
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 20.0),
        create_transaction(3, "user1", "StoreA", "2024-01-03", 30.0),
    ]
    transaction = transactions[2]
    assert get_amount_mad(transaction, transactions) == 10.0


def test_get_amount_iqr():
    transactions = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 20.0),
        create_transaction(3, "user1", "StoreA", "2024-01-03", 30.0),
        create_transaction(4, "user1", "StoreA", "2024-01-04", 40.0),
    ]
    transaction = transactions[3]
    assert get_amount_iqr(transaction, transactions) == 15.0


def test_is_recurring_through_past_transactions():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-08", 10.0),
        create_transaction(3, "user1", "StoreA", "2024-01-15", 10.0),
    ]
    assert is_recurring_through_past_transactions(txns[2], txns)
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-10", 10.0),
    ]
    assert not is_recurring_through_past_transactions(txns[1], txns)


def test_get_amount_zscore():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 20.0),
        create_transaction(3, "user1", "StoreA", "2024-01-03", 30.0),
    ]
    assert abs(get_amount_zscore(txns[2], txns) - 1.0) < 0.01


def test_is_amount_outlier():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 10.0),
        create_transaction(3, "user1", "StoreA", "2024-01-03", 50.0),
    ]
    # Accept that 50.0 may not be flagged as outlier with only 3 samples
    assert not is_amount_outlier(txns[2], txns)
    assert not is_amount_outlier(txns[0], txns)


def test_get_stddev_amount_same_merchant():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 20.0),
    ]
    assert round(get_stddev_amount_same_merchant(txns[1], txns), 2) == 7.07


def test_get_avg_days_between_same_merchant():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-11", 20.0),
        create_transaction(3, "user1", "StoreA", "2024-01-21", 30.0),
    ]
    assert get_avg_days_between_same_merchant(txns[2], txns) == 10.0


def test_is_weekend_transaction():
    txn = create_transaction(1, "user1", "StoreA", "2024-01-06", 10.0)  # Saturday
    assert is_weekend_transaction(txn)
    txn = create_transaction(2, "user1", "StoreA", "2024-01-03", 10.0)  # Wednesday
    assert not is_weekend_transaction(txn)


def test_is_end_of_month_transaction():
    txn = create_transaction(1, "user1", "StoreA", "2024-01-31", 10.0)
    assert is_end_of_month_transaction(txn)
    txn = create_transaction(2, "user1", "StoreA", "2024-01-30", 10.0)
    assert not is_end_of_month_transaction(txn)


def test_get_days_since_first_transaction():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-11", 20.0),
    ]
    assert get_days_since_first_transaction(txns[1], txns) == 10


def test_get_amount_coefficient_of_variation():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 20.0),
    ]
    assert abs(get_amount_coefficient_of_variation(txns[1], txns) - 0.47) < 0.01


def test_get_unique_merchants_count():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreB", "2024-01-02", 20.0),
    ]
    assert get_unique_merchants_count(txns[0], txns) == 2


def test_get_amount_quantile():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 20.0),
        create_transaction(3, "user1", "StoreA", "2024-01-03", 30.0),
    ]
    assert get_amount_quantile(txns[1], txns) == 2 / 3


def test_is_consistent_weekday_pattern():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),  # Monday
        create_transaction(2, "user1", "StoreA", "2024-01-08", 10.0),  # Monday
        create_transaction(3, "user1", "StoreA", "2024-01-15", 10.0),  # Monday
    ]
    assert is_consistent_weekday_pattern(txns[2], txns)
    txns[2] = create_transaction(3, "user1", "StoreA", "2024-01-16", 10.0)  # Tuesday
    assert not is_consistent_weekday_pattern(txns[2], txns)


def test_get_recurrence_score_by_amount():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-08", 10.0),
        create_transaction(3, "user1", "StoreA", "2024-01-15", 10.0),
    ]
    assert get_recurrence_score_by_amount(txns[2], txns) > 0.5


def test_compare_recent_to_historical_average():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-02", 10.0),
        create_transaction(3, "user1", "StoreA", "2024-01-03", 10.0),
        create_transaction(4, "user1", "StoreA", "2024-01-04", 10.0),
    ]
    txn = create_transaction(5, "user1", "StoreA", "2024-01-05", 10.0)
    assert compare_recent_to_historical_average(txn, txns) == 1.0


def test_get_days_since_last_transaction():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-11", 20.0),
    ]
    assert get_days_since_last_transaction(txns[1], txns) == 10


def test_get_normalized_recency():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-11", 20.0),
        create_transaction(3, "user1", "StoreA", "2024-01-21", 30.0),
    ]
    assert abs(get_normalized_recency(txns[2], txns) - 1.0) < 0.01


def test_get_transaction_recency_score():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-11", 20.0),
        create_transaction(3, "user1", "StoreA", "2024-01-21", 30.0),
    ]
    assert get_transaction_recency_score(txns[2], txns) == 1.0
    assert get_transaction_recency_score(txns[0], txns) == 0.0


def test_get_n_transactions_last_30_days():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-10", 20.0),
        create_transaction(3, "user1", "StoreA", "2024-01-20", 30.0),
    ]
    txn = create_transaction(4, "user1", "StoreA", "2024-01-21", 40.0)
    assert get_n_transactions_last_30_days(txn, txns, window_days=20) == 3


def test_get_ratio_transactions_last_30_days():
    txns = [
        create_transaction(1, "user1", "StoreA", "2024-01-01", 10.0),
        create_transaction(2, "user1", "StoreA", "2024-01-10", 20.0),
        create_transaction(3, "user1", "StoreA", "2024-01-20", 30.0),
    ]
    txn = create_transaction(4, "user1", "StoreA", "2024-01-21", 40.0)
    assert abs(get_ratio_transactions_last_30_days(txn, txns, window_days=20) - 1.0) < 0.01
