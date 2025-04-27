# test features


from recur_scan.features_efehi import (
    get_irregular_periodicity,
    get_irregular_periodicity_with_tolerance,
    get_n_same_name_transactions,
    get_time_between_transactions,
    get_transaction_amount_stability,
    get_transaction_frequency,
    get_transaction_time_of_month,
    get_user_transaction_frequency,
    # days_between_user_txns,
    # price_similarity_to_user_median,
    # merchant_spread_days,
    # is_small_fluctuation,
    # weekly_recurring_indicator,
    get_vendor_category_score,
    get_vendor_recurrence_consistency,
    get_vendor_recurring_ratio,
    rolling_amount_deviation,
    # get_transaction_frequency_score,
    # get_amount_consistency_score,
    # get_day_of_month_variance,
    # get_interval_variance_score,
    # get_amount_range_score,
)
from recur_scan.transactions import Transaction


def test_get_transaction_time_of_month() -> None:
    """Test that get_transaction_time_of_month categorizes transactions correctly."""
    transaction_early = Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-05")
    transaction_mid = Transaction(id=2, user_id="user1", name="Test", amount=100, date="2024-01-15")
    transaction_late = Transaction(id=3, user_id="user1", name="Test", amount=100, date="2024-01-25")
    assert get_transaction_time_of_month(transaction_early) == 0
    assert get_transaction_time_of_month(transaction_mid) == 1
    assert get_transaction_time_of_month(transaction_late) == 2


def test_get_transaction_amount_stability() -> None:
    """Test that get_transaction_amount_stability calculates the standard deviation of transaction amounts."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Test", amount=200, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="Test", amount=300, date="2024-01-03"),
    ]
    assert get_transaction_amount_stability(transactions[0], transactions) > 0.0
    assert get_transaction_amount_stability(transactions[0], [transactions[0]]) == 0.0


def test_get_time_between_transactions() -> None:
    """Test that get_time_between_transactions calculates the average time gap between transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Test", amount=100, date="2024-01-05"),
        Transaction(id=3, user_id="user1", name="Test", amount=100, date="2024-01-10"),
    ]
    assert get_time_between_transactions(transactions[0], transactions) == 4.5
    assert get_time_between_transactions(transactions[0], [transactions[0]]) == 0.0


def test_get_transaction_frequency() -> None:
    """Test that get_transaction_frequency calculates average frequency correctly."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Allstate Insurance", date="2024-01-01", amount=100),
        Transaction(id=2, user_id="user1", name="Allstate Insurance", date="2024-01-02", amount=100),
        Transaction(id=3, user_id="user1", name="AT&T", date="2024-01-01", amount=200),
        Transaction(id=4, user_id="user1", name="Duke Energy", date="2024-01-02", amount=150),
        Transaction(id=5, user_id="user1", name="HighEnergy Soft Drinks", date="2024-01-03", amount=2.99),
    ]
    transaction = transactions[0]
    result = get_transaction_frequency(transaction, transactions)
    assert result > 0


def test_get_n_same_name_transactions() -> None:
    """Test that get_n_same_name_transactions correctly counts transactions with the same name."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Allstate Insurance", date="2024-01-01", amount=100),
        Transaction(id=2, user_id="user1", name="AT&T", date="2024-01-01", amount=200),
        Transaction(id=3, user_id="user1", name="Duke Energy", date="2024-01-02", amount=150),
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", date="2024-01-03", amount=2.99),
    ]
    assert get_n_same_name_transactions(transactions[0], transactions) == 1  # "Allstate Insurance" appears once
    assert get_n_same_name_transactions(transactions[1], transactions) == 1  # "AT&T" appears once
    # Add a duplicate transaction to test multiple occurrences
    transactions.append(Transaction(id=5, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-04"))
    assert get_n_same_name_transactions(transactions[0], transactions) == 2  # "Allstate Insurance" now appears twice


def test_get_irregular_periodicity() -> None:
    """Test that get_irregular_periodicity calculates the standard deviation of time gaps correctly."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Test", amount=100, date="2024-03-01"),
        Transaction(id=3, user_id="user1", name="Test", amount=100, date="2024-06-01"),
    ]
    assert get_irregular_periodicity(transactions[0], transactions) > 0.0
    assert get_irregular_periodicity(transactions[0], [transactions[0]]) == 0.0


def test_get_irregular_periodicity_with_tolerance() -> None:
    """Test that get_irregular_periodicity_with_tolerance calculates the standard deviation with tolerance."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Test", amount=100, date="2024-01-10"),
        Transaction(id=3, user_id="user1", name="Test", amount=100, date="2024-01-20"),
        Transaction(id=4, user_id="user1", name="Test", amount=100, date="2024-02-01"),
    ]
    result = get_irregular_periodicity_with_tolerance(transactions[0], transactions, tolerance=5)
    assert result > 0.0  # Ensure the result is greater than 0
    assert result < 0.4  # Ensure the result is within the expected range


def test_get_user_transaction_frequency() -> None:
    """Test that get_user_transaction_frequency calculates the average frequency of user transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Test", amount=100, date="2024-01-10"),
        Transaction(id=3, user_id="user1", name="Test", amount=100, date="2024-01-20"),
        Transaction(id=4, user_id="user1", name="Test", amount=100, date="2024-02-01"),
    ]
    assert get_user_transaction_frequency("user1", transactions) == 10.333333333333334  # Update expected value
    assert get_user_transaction_frequency("user2", transactions) == 0.0


def test_get_vendor_recurring_ratio() -> None:
    """Test that get_vendor_recurring_ratio calculates the correct ratio of recurring transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Test", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Test", amount=100, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Test", amount=200, date="2024-03-01"),
    ]
    assert get_vendor_recurring_ratio(transactions[0], transactions) == 2 / 3
    assert get_vendor_recurring_ratio(transactions[2], transactions) == 1 / 3
    assert get_vendor_recurring_ratio(transactions[0], []) == 0.0


def test_get_vendor_recurrence_consistency() -> None:
    """Test that get_vendor_recurrence_consistency calculates the correct percentage of consistent intervals."""
    transactions = [
        Transaction(id=1, user_id="user1", name="VendorA", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="VendorA", amount=100, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="VendorA", amount=100, date="2024-03-01"),
        Transaction(id=4, user_id="user1", name="VendorA", amount=100, date="2024-05-01"),
    ]
    result = get_vendor_recurrence_consistency(transactions[0], transactions)
    assert 0.5 < result < 0.8  # Adjusted to match expected behavior


################################################
# = First Week (Variance Attack) Features test ==#
################################################

# def test_days_between_user_txns() -> None:
#     """Test average days between user's transactions with the same merchant."""
#     transactions = [
#         Transaction(id=1, user_id="user1", name="Netflix", amount=10.0, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="Netflix", amount=10.0, date="2024-01-08"),
#         Transaction(id=3, user_id="user1", name="Netflix", amount=10.0, date="2024-01-15"),
#     ]
#     txn = Transaction(id=4, user_id="user1", name="Netflix", amount=10.0, date="2024-01-22")
#     result = days_between_user_txns(txn, transactions)
#     assert 6.5 <= result <= 7.5

# def test_price_similarity_to_user_median() -> None:
#     """Test how close the transaction amount is to user's median."""
#     transactions = [
#         Transaction(id=1, user_id="user1", name="Netflix", amount=10.0, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="Netflix", amount=10.0, date="2024-01-08"),
#     ]
#     txn = Transaction(id=3, user_id="user1", name="Netflix", amount=10.0, date="2024-01-22")
#     result = price_similarity_to_user_median(txn, transactions)
#     assert result == 0.0

# def test_merchant_spread_days() -> None:
#     """Test days between first and last transaction with the merchant."""
#     transactions = [
#         Transaction(id=1, user_id="user1", name="Netflix", amount=10.0, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="Netflix", amount=10.0, date="2024-01-15"),
#     ]
#     txn = Transaction(id=3, user_id="user1", name="Netflix", amount=10.0, date="2024-01-22")
#     result = merchant_spread_days(txn, transactions)
#     assert result == 14

# def test_is_small_fluctuation() -> None:
#     """Test if transaction amount is within 5% of user's median."""
#     transactions = [
#         Transaction(id=1, user_id="user1", name="Netflix", amount=10.0, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="Netflix", amount=10.0, date="2024-01-08"),
#     ]
#     txn = Transaction(id=3, user_id="user1", name="Netflix", amount=10.0, date="2024-01-22")
#     result = is_small_fluctuation(txn, transactions)
#     assert result == 1

# def test_weekly_recurring_indicator() -> None:
#     """Test detection of transactions falling close to a 7-day interval."""
#     transactions = [
#         Transaction(id=1, user_id="user1", name="Netflix", amount=10.0, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="Netflix", amount=10.0, date="2024-01-08"),
#         Transaction(id=3, user_id="user1", name="Netflix", amount=10.0, date="2024-01-15"),
#     ]
#     txn = Transaction(id=4, user_id="user1", name="Netflix", amount=10.0, date="2024-01-22")
#     result = weekly_recurring_indicator(txn, transactions)
#     assert result == 1


###########################################
##-Newly Designed Feature Functions tests-#
###########################################
def test_get_vendor_category_score() -> None:
    """Test assigning recurrence probability based on vendor type."""

    # Test a subscription vendor (e.g., Apple is in subscription_vendors)
    txn1 = Transaction(id=1, user_id="user1", name="Apple", amount=10.0, date="2024-01-01")
    result1 = get_vendor_category_score(txn1)
    assert result1 == 0.9

    # Test a loan vendor (e.g., AfterPay is in loan_vendors)
    txn2 = Transaction(id=2, user_id="user2", name="AfterPay", amount=100.0, date="2024-02-01")
    result2 = get_vendor_category_score(txn2)
    assert result2 == 0.9

    # Test an insurance vendor (e.g., GEICO is in insurance_vendors)
    txn3 = Transaction(id=3, user_id="user3", name="GEICO", amount=120.0, date="2024-03-01")
    result3 = get_vendor_category_score(txn3)
    assert result3 == 0.5

    # Test a telecom vendor (e.g., Verizon is in telecom_vendors)
    txn4 = Transaction(id=4, user_id="user4", name="Verizon", amount=80.0, date="2024-04-01")
    result4 = get_vendor_category_score(txn4)
    assert result4 == 0.5

    # Test a housing vendor (e.g., Waterford Grove is in housing_vendors)
    txn5 = Transaction(id=5, user_id="user5", name="Waterford Grove", amount=900.0, date="2024-05-01")
    result5 = get_vendor_category_score(txn5)
    assert result5 == 0.5

    # Test an unknown vendor (should default to 0.2)
    txn6 = Transaction(id=6, user_id="user6", name="Random Vendor XYZ", amount=50.0, date="2024-06-01")
    result6 = get_vendor_category_score(txn6)
    assert result6 == 0.2


def test_rolling_amount_deviation() -> None:
    """Test deviation of current amount from rolling mean of previous amounts."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=10.0, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=12.0, date="2024-01-08"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=11.0, date="2024-01-15"),
        Transaction(id=4, user_id="user1", name="Netflix", amount=20.0, date="2024-01-22"),
    ]
    txn = transactions[3]  # the transaction we are testing
    result = rolling_amount_deviation(txn, transactions)
    expected_deviation = abs(20.0 - ((10.0 + 12.0 + 11.0) / 3))
    assert abs(result - expected_deviation) < 1e-6


# def test_get_transaction_frequency_score() -> None:
#     """Test transaction frequency score calculation."""

#     transactions = [
#         Transaction(id=1, user_id="user1", name="Netflix", amount=10.0, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="Netflix", amount=10.0, date="2024-01-31"),  # 30 days apart
#     ]
#     txn = Transaction(id=3, user_id="user1", name="Netflix", amount=10.0, date="2024-02-29")
#     result = get_transaction_frequency_score(txn, transactions)
#     assert abs(result - 2) < 0.01  # 2 transactions in 30 days => score ~2

# def test_get_amount_consistency_score() -> None:
#     """Test amount consistency score (coefficient of variation)."""
#     transactions = [
#         Transaction(id=1, user_id="user1", name="Spotify", amount=10.0, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="Spotify", amount=12.0, date="2024-02-01"),
#     ]
#     txn = Transaction(id=3, user_id="user1", name="Spotify", amount=11.0, date="2024-03-01")
#     result = get_amount_consistency_score(txn, transactions)
#     expected_cv = np.std([10.0, 12.0]) / np.mean([10.0, 12.0])
#     assert abs(result - expected_cv) < 0.01

# def test_get_day_of_month_variance() -> None:
#     """Test day of month variance calculation."""

#     transactions = [
#         Transaction(id=1, user_id="user1", name="Gym", amount=20.0, date="2024-01-05"),
#         Transaction(id=2, user_id="user1", name="Gym", amount=20.0, date="2024-02-06"),
#     ]
#     txn = Transaction(id=3, user_id="user1", name="Gym", amount=20.0, date="2024-03-07")
#     result = get_day_of_month_variance(txn, transactions)
#     expected_variance = np.var([5, 6])
#     assert abs(result - expected_variance) < 0.01

# def test_get_interval_variance_score() -> None:
#     """Test interval variance score calculation."""

#     transactions = [
#         Transaction(id=1, user_id="user1", name="Phone Bill", amount=30.0, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="Phone Bill", amount=30.0, date="2024-02-01"),
#         Transaction(id=3, user_id="user1", name="Phone Bill", amount=30.0, date="2024-03-03"),
#     ]
#     txn = Transaction(id=4, user_id="user1", name="Phone Bill", amount=30.0, date="2024-04-01")
#     result = get_interval_variance_score(txn, transactions)
#     intervals = [(datetime.strptime("2024-02-01", "%Y-%m-%d") - datetime.strptime("2024-01-01", "%Y-%m-%d")).days,
#                  (datetime.strptime("2024-03-03", "%Y-%m-%d") - datetime.strptime("2024-02-01", "%Y-%m-%d")).days]
#     expected_variance = np.var(intervals)
#     assert abs(result - expected_variance) < 0.01


# def test_get_amount_range_score() -> None:
#     """Test amount range based recurrence score."""
#     txn_small = Transaction(id=1, user_id="user1", name="Vendor", amount=5.0, date="2024-01-01")
#     txn_medium = Transaction(id=2, user_id="user1", name="Vendor", amount=30.0, date="2024-01-01")
#     txn_large = Transaction(id=3, user_id="user1", name="Vendor", amount=150.0, date="2024-01-01")
#     txn_very_large = Transaction(id=4, user_id="user1", name="Vendor", amount=500.0, date="2024-01-01")
#     txn_huge = Transaction(id=5, user_id="user1", name="Vendor", amount=5000.0, date="2024-01-01")

#     assert get_amount_range_score(txn_small) == 0.9
#     assert get_amount_range_score(txn_medium) == 0.7
#     assert get_amount_range_score(txn_large) == 0.5
#     assert get_amount_range_score(txn_very_large) == 0.3
#     assert get_amount_range_score(txn_huge) == 0.2
