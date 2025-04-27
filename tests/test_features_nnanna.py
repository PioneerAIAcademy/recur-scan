# test features
import pytest

from recur_scan.features_nnanna import (
    get_average_transaction_amount,
    get_cobblestone_recurrence_score,
    get_coefficient_of_variation,
    get_dispersion_transaction_amount,
    get_mad_transaction_amount,
    get_mobile_transaction,
    get_time_interval_between_transactions,
    get_transaction_frequency,
    get_transaction_interval_consistency,
    # get_recency_of_transaction,
    # get_transaction_consistency,
    # get_transaction_interval_variance,
    # get_is_recurring_transaction,
    # get_is_not_recurring_transaction,
    # get_recurring_transaction_by_amount_and_interval,
    # get_recurring_transaction_by_short_interval,
    get_u_dot_express_lane,
    is_consistent_transaction_amount,
    # get_weighted_recency,
    # get_transaction_clusters,
    # get_normalized_transaction_amount,
    # get_frequency_consistency,
    # get_vendor_recurrence_score,
    # is_outlier,
    # get_temporal_pattern_score,
    is_monthly_apple_storage,
)
from recur_scan.transactions import Transaction


def test_get_time_interval_between_transactions() -> None:
    """
    Test that get_time_interval_between_transactions returns the correct average time interval between
    transactions with the same amount.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="T-Mobile", amount=50, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="AT&T", amount=60, date="2024-01-05"),
        Transaction(id=6, user_id="user1", name="Verizon", amount=70, date="2024-01-06"),
        Transaction(id=7, user_id="user1", name="vendor1", amount=100, date="2024-01-26"),
        Transaction(id=8, user_id="user1", name="vendor2", amount=100.99, date="2024-01-07"),
        Transaction(id=9, user_id="user1", name="vendor2", amount=100.99, date="2024-01-14"),
        Transaction(id=10, user_id="user1", name="vendor2", amount=100.99, date="2024-01-21"),
        Transaction(id=11, user_id="user1", name="Sony Playstation", amount=500, date="2024-01-15"),
    ]
    assert get_time_interval_between_transactions(transactions[0], transactions) == 12.5
    assert get_time_interval_between_transactions(transactions[2], transactions) == 365.0


def test_get_mobile_transaction() -> None:
    """
    Test that get_mobile_transaction returns True for mobile company transactions and False otherwise.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="T-Mobile", amount=50, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="AT&T", amount=60, date="2024-01-05"),
        Transaction(id=6, user_id="user1", name="Verizon", amount=70, date="2024-01-06"),
        Transaction(id=7, user_id="user1", name="vendor1", amount=100, date="2024-01-26"),
        Transaction(id=8, user_id="user1", name="vendor2", amount=100.99, date="2024-01-07"),
        Transaction(id=9, user_id="user1", name="vendor2", amount=100.99, date="2024-01-14"),
        Transaction(id=10, user_id="user1", name="vendor2", amount=100.99, date="2024-01-21"),
        Transaction(id=11, user_id="user1", name="Sony Playstation", amount=500, date="2024-01-15"),
    ]
    assert get_mobile_transaction(transactions[3]) is True  # T-Mobile
    assert get_mobile_transaction(transactions[4]) is True  # AT&T
    assert get_mobile_transaction(transactions[5]) is True  # Verizon
    assert get_mobile_transaction(transactions[0]) is False  # vendor1


def test_get_transaction_frequency() -> None:
    """Test get_transaction_frequency."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03"),
    ]
    assert get_transaction_frequency(transactions[0], transactions) == 0.0
    assert (
        get_transaction_frequency(
            Transaction(id=12, user_id="user1", name="vendor3", amount=99.99, date="2024-01-08"), transactions
        )
        == 0.0
    )


def test_get_dispersion_transaction_amount() -> None:
    """Test get_dispersion_transaction_amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03"),
    ]
    assert (
        get_dispersion_transaction_amount(transactions[0], transactions) == 0.0
    )  # Replace with the correct expected value


def test_get_mad_transaction_amount() -> None:
    """Test get_mad_transaction_amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="vendor2", amount=60, date="2024-01-05"),
        Transaction(id=6, user_id="user1", name="vendor2", amount=70, date="2024-01-06"),
    ]
    # Test for vendor1
    assert pytest.approx(get_mad_transaction_amount(transactions[0], transactions)) == 50.0
    # Test for vendor2
    assert pytest.approx(get_mad_transaction_amount(transactions[3], transactions)) == 10.0
    # Test for a vendor with only one transaction
    assert (
        get_mad_transaction_amount(
            Transaction(id=7, user_id="user1", name="vendor3", amount=100, date="2024-01-07"), transactions
        )
        == 0.0
    )


def test_get_coefficient_of_variation() -> None:
    """Test get_coefficient_of_variation."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="vendor2", amount=60, date="2024-01-05"),
        Transaction(id=6, user_id="user1", name="vendor2", amount=70, date="2024-01-06"),
    ]
    # Test for vendor1
    assert pytest.approx(get_coefficient_of_variation(transactions[0], transactions), rel=1e-4) == 0.2721655269759087
    # Test for vendor2
    assert pytest.approx(get_coefficient_of_variation(transactions[3], transactions), rel=1e-4) == 0.13608276348795434
    # Test for a vendor with only one transaction
    assert (
        get_coefficient_of_variation(
            Transaction(id=7, user_id="user1", name="vendor3", amount=100, date="2024-01-07"), transactions
        )
        == 0.0
    )
    # Test for a vendor with mean = 0 (edge case)
    assert (
        get_coefficient_of_variation(
            Transaction(id=8, user_id="user1", name="vendor4", amount=0, date="2024-01-08"), transactions
        )
        == 0.0
    )
    # Test for a vendor with mean = 0 (edge case)
    assert (
        get_coefficient_of_variation(
            Transaction(id=8, user_id="user1", name="vendor4", amount=0, date="2024-01-08"), transactions
        )
        == 0.0
    )


def test_get_transaction_interval_consistency() -> None:
    """Test get_transaction_interval_consistency."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-15"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-30"),
        Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-01"),
        Transaction(id=5, user_id="user1", name="vendor2", amount=60, date="2024-01-10"),
        Transaction(id=6, user_id="user1", name="vendor2", amount=70, date="2024-01-20"),
    ]
    # Test for vendor1
    assert pytest.approx(get_transaction_interval_consistency(transactions[0], transactions), rel=1e-4) == 14.5

    # Test for vendor2
    assert pytest.approx(get_transaction_interval_consistency(transactions[3], transactions), rel=1e-4) == 9.5

    # Test for a vendor with only one transaction
    assert (
        get_transaction_interval_consistency(
            Transaction(id=7, user_id="user1", name="vendor3", amount=100, date="2024-01-01"), transactions
        )
        == 0.0
    )


def test_get_average_transaction_amount() -> None:
    """Test get_average_transaction_amount."""
    transactions = [
        Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-04"),
        Transaction(id=5, user_id="user1", name="vendor2", amount=60, date="2024-01-05"),
        Transaction(id=6, user_id="user1", name="vendor2", amount=70, date="2024-01-06"),
    ]
    # Test for vendor1
    assert pytest.approx(get_average_transaction_amount(transactions[0], transactions)) == 150.0
    # Test for vendor2
    assert pytest.approx(get_average_transaction_amount(transactions[3], transactions)) == 60.0
    # Test for a vendor with only one transaction
    assert (
        get_average_transaction_amount(
            Transaction(id=7, user_id="user1", name="vendor3", amount=100, date="2024-01-07"), transactions
        )
        == 0.0
    )


# New Test Features

# def test_get_recency_of_transaction() -> None:
#     """
#     Test that get_recency_of_transaction returns the correct number of days since the last transaction
#     for the same vendor, avoiding data leakage.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-10"),
#         Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-20"),
#         Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-05"),
#         Transaction(id=5, user_id="user1", name="vendor2", amount=60, date="2024-01-15"),
#         Transaction(id=6, user_id="user1", name="vendor2", amount=70, date="2024-01-25"),
#     ]

#     # Test for vendor1
#     assert get_recency_of_transaction(transactions[2], transactions[:3]) == 10  # 2024-01-20 - 2024-01-10
#     assert get_recency_of_transaction(transactions[1], transactions[:2]) == 9   # 2024-01-10 - 2024-01-01
#     assert get_recency_of_transaction(transactions[0], transactions[:1]) == float('inf')  # No previous transaction

#     # Test for vendor2
#     assert get_recency_of_transaction(transactions[5], transactions[:6]) == 10  # 2024-01-25 - 2024-01-15
#     assert get_recency_of_transaction(transactions[4], transactions[:5]) == 10  # 2024-01-15 - 2024-01-05
#     assert get_recency_of_transaction(transactions[3], transactions[:4]) == float('inf')  # No previous transaction

#     # Test for a vendor with only one transaction
#     assert (
#         get_recency_of_transaction(
#             Transaction(id=7, user_id="user1", name="vendor3", amount=100, date="2024-01-30"), transactions
#         )
#         == float('inf')
#     )


# def test_get_transaction_consistency() -> None:
#     """
#     Test that get_transaction_consistency calculates the correct consistency score for transaction amounts
#     for the same vendor.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-02"),
#         Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-03"),
#         Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-04"),
#         Transaction(id=5, user_id="user1", name="vendor2", amount=60, date="2024-01-05"),
#         Transaction(id=6, user_id="user1", name="vendor2", amount=70, date="2024-01-06"),
#     ]
#     # Test for vendor1
#     assert pytest.approx(get_transaction_consistency(transactions[0], transactions), rel=1e-4) == 0.2721655269759087
#     # Test for vendor2
#     assert pytest.approx(get_transaction_consistency(transactions[3], transactions), rel=1e-4) == 0.13608276348795434
#     # Test for a vendor with only one transaction
#     assert (
#         get_transaction_consistency(
#             Transaction(id=7, user_id="user1", name="vendor3", amount=100, date="2024-01-07"), transactions
#         )
#         == 0.0
#     )


# def test_get_transaction_interval_variance() -> None:
#     """
#     Test that get_transaction_interval_variance calculates the variance of intervals
#     (in days) between transactions for the same vendor, using regex for vendor name matching.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="Apple Inc.", amount=11.54, date="2023-01-26"),
#         Transaction(id=2, user_id="user1", name="Apple", amount=11.54, date="2023-02-27"),
#         Transaction(id=3, user_id="user1", name="Apple", amount=11.54, date="2023-03-27"),
#         Transaction(id=4, user_id="user1", name="Microsoft", amount=21.59, date="2023-01-31"),
#         Transaction(id=5, user_id="user1", name="Microsoft", amount=21.59, date="2024-11-17"),
#         Transaction(id=6, user_id="user1", name="Microsoft", amount=21.59, date="2024-12-18"),
#         Transaction(id=7, user_id="user1", name="Brigit", amount=9.99, date="2023-08-25"),
#         Transaction(id=8, user_id="user1", name="Brigit", amount=9.99, date="2024-01-26"),
#         Transaction(id=9, user_id="user1", name="Brigit", amount=9.99, date="2024-06-03"),
#     ]

#     # Test for Apple (matching "Apple Inc." and "Apple")
#     assert pytest.approx(get_transaction_interval_variance(transactions[0], transactions), rel=1e-4) == 30.25

#     # Test for Microsoft
#     assert pytest.approx(get_transaction_interval_variance(transactions[3], transactions), rel=1e-4) == 29241.0

#     # Test for Brigit
#     assert pytest.approx(get_transaction_interval_variance(transactions[6], transactions), rel=1e-4) == 123.25

#     # Test for a vendor with only one transaction
#     assert (
#         get_transaction_interval_variance(
#             Transaction(id=10, user_id="user1", name="Netflix", amount=25.17, date="2024-03-26"), transactions
#         )
#         == 36500.0
#     )


# def test_is_recurring_transaction() -> None:
#     """
#     Test that is_recurring_transaction correctly identifies recurring transactions.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-02-01"),
#         Transaction(id=3, user_id="user1", name="vendor1", amount=100, date="2024-03-01"),
#         Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-04"),
#         Transaction(id=5, user_id="user1", name="vendor2", amount=50, date="2024-02-06"),
#         Transaction(id=6, user_id="user1", name="vendor2", amount=50, date="2024-03-05"),
#         Transaction(id=7, user_id="user1", name="vendor3", amount=200, date="2024-01-15"),
#     ]

#     # Test for vendor1 (recurring on the same date every month)
#     assert get_is_recurring_transaction(transactions[0], transactions) is True

#     # Test for vendor2 (recurring within 3 days every month)
#     assert get_is_recurring_transaction(transactions[3], transactions) is True

#     # Test for vendor3 (not recurring)
#     assert get_is_recurring_transaction(transactions[6], transactions) is False


# def test_is_not_recurring_transaction() -> None:
#     """
#     Test that is_not_recurring_transaction correctly identifies non-recurring transactions.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-02-01"),
#         Transaction(id=3, user_id="user1", name="vendor1", amount=100, date="2024-03-01"),
#         Transaction(id=4, user_id="user1", name="T-Mobile", amount=50, date="2024-01-04"),
#         Transaction(id=5, user_id="user1", name="AT&T", amount=60, date="2024-02-05"),
#         Transaction(id=6, user_id="user1", name="vendor2", amount=200, date="2024-01-10"),
#         Transaction(id=7, user_id="user1", name="vendor2", amount=200, date="2024-03-15"),
#         Transaction(id=8, user_id="user1", name="vendor3", amount=300, date="2024-01-20"),
#     ]

#     # Test for vendor1 (recurring on the same date every month)
#     assert get_is_not_recurring_transaction(transactions[0], transactions) is False

#     # Test for T-Mobile (mobile company, considered recurring)
#     assert get_is_not_recurring_transaction(transactions[3], transactions) is False

#     # Test for vendor2 (not recurring due to inconsistent dates)
#     assert get_is_not_recurring_transaction(transactions[5], transactions) is True

#     # Test for vendor3 (only one transaction, considered not recurring)
#     assert get_is_not_recurring_transaction(transactions[7], transactions) is True


# def test_is_recurring_transaction_by_amount_and_interval() -> None:
#     """
#     Test that is_recurring_transaction_by_amount_and_interval correctly identifies recurring transactions.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-14"),
#         Transaction(id=3, user_id="user1", name="vendor1", amount=100, date="2024-01-28"),
#         Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-01"),
#         Transaction(id=5, user_id="user1", name="vendor2", amount=50, date="2024-01-20"),
#         Transaction(id=6, user_id="user1", name="vendor3", amount=200, date="2024-01-15"),
#     ]

#     # Test for vendor1 (recurring with 13-15 day intervals)
#     assert get_recurring_transaction_by_amount_and_interval(transactions[0], transactions) is True

#     # Test for vendor2 (not recurring due to inconsistent intervals)
#     assert get_recurring_transaction_by_amount_and_interval(transactions[3], transactions) is False

#     # Test for vendor3 (only one transaction, not recurring)
#     assert get_recurring_transaction_by_amount_and_interval(transactions[5], transactions) is False


# def test_is_recurring_transaction_by_short_interval() -> None:
#     """
#     Test that is_recurring_transaction_by_short_interval correctly identifies recurring transactions.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-07"),
#         Transaction(id=3, user_id="user1", name="vendor1", amount=100, date="2024-01-14"),
#         Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-01"),
#         Transaction(id=5, user_id="user1", name="vendor2", amount=50, date="2024-01-10"),
#         Transaction(id=6, user_id="user1", name="vendor3", amount=200, date="2024-01-15"),
#     ]

#     # Test for vendor1 (recurring with 6-8 day intervals)
#     assert get_recurring_transaction_by_short_interval(transactions[0], transactions) is True

#     # Test for vendor2 (not recurring due to inconsistent intervals)
#     assert get_recurring_transaction_by_short_interval(transactions[3], transactions) is False

#     # Test for vendor3 (only one transaction, not recurring)
#     assert get_recurring_transaction_by_short_interval(transactions[5], transactions) is False


def test_u_dot_express_lane():
    """
    Test that filter_u_dot_express_lane correctly filters out invalid transactions.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="U-dot-express Lane", amount=2.50, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="U-dot-express Lane", amount=25.00, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="U-dot-express Lane", amount=10.00, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="Other Vendor", amount=50.00, date="2024-01-04"),
    ]

    filtered = get_u_dot_express_lane(transactions)

    # Only the valid U-dot-express Lane transaction should remain
    assert len(filtered) == 2
    assert filtered[0].name == "U-dot-express Lane"
    assert filtered[0].amount == 2.50
    assert filtered[1].name == "Other Vendor"
    assert filtered[1].amount == 50.00
    assert filtered[1].name != "U-dot-express Lane" or filtered[1].amount != 2.50


# def test_get_weighted_recency() -> None:
#     """
#     Test that get_weighted_recency calculates the correct weighted recency score.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-10"),
#         Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-20"),
#     ]
#     current_transaction = Transaction(id=4, user_id="user1", name="vendor1", amount=250, date="2024-01-30")
#     assert pytest.approx(get_weighted_recency(transactions, current_transaction), rel=1e-4) == 0.1833


# def test_get_transaction_clusters() -> None:
#     """
#     Test that get_transaction_clusters calculates the correct time intervals for a vendor.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-10"),
#         Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-20"),
#     ]
#     assert get_transaction_clusters(transactions, "vendor1") == [9, 10]


# def test_get_normalized_transaction_amount() -> None:
#     """
#     Test that get_normalized_transaction_amount calculates the correct normalized value.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-10"),
#         Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-20"),
#     ]
#     current_transaction = Transaction(id=4, user_id="user1", name="vendor1", amount=150, date="2024-01-30")
#     assert pytest.approx(get_normalized_transaction_amount(transactions, current_transaction), rel=1e-4) == 0.0

# def test_get_frequency_consistency() -> None:
#     """
#     Test that get_frequency_consistency calculates the correct consistency score.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-10"),
#         Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-20"),
#     ]
#     assert pytest.approx(get_frequency_consistency(transactions, "vendor1"), rel=1e-4) == 0.5

# def test_get_vendor_recurrence_score() -> None:
#     """
#     Test that get_vendor_recurrence_score calculates the correct recurrence score.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-10"),
#         Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-20"),
#     ]
#     assert pytest.approx(get_vendor_recurrence_score(transactions, "vendor1"), rel=1e-4) == 0.9


# def test_is_outlier() -> None:
#     """
#     Test that is_outlier correctly identifies outlier transactions.
#     """
#     transactions = [
#         Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="vendor1", amount=150, date="2024-01-10"),
#         Transaction(id=3, user_id="user1", name="vendor1", amount=200, date="2024-01-20"),
#     ]
#     outlier_transaction = Transaction(id=4, user_id="user1", name="vendor1", amount=500, date="2024-01-30")
#     assert is_outlier(outlier_transaction, transactions) is True

# def test_get_temporal_pattern_score() -> None:
#     """
#     Test that get_temporal_pattern_score calculates the correct score based on the day of the week.
#     """
#     transaction_weekday = Transaction(id=1, user_id="user1", name="vendor1", amount=100, date="2024-01-01")  # Monday
#      transaction_weekend = Transaction(
#          id=2, user_id="user1", name="vendor1", amount=100, date="2024-01-06"
#      )  # Saturday
#     assert get_temporal_pattern_score(transaction_weekday) == 0.5
#     assert get_temporal_pattern_score(transaction_weekend) == 1.0


def test_is_monthly_apple_storage() -> None:
    """
    Test that is_monthly_apple_storage correctly identifies Apple transactions
    that occur monthly with amounts ending in .99.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="Apple", amount=0.99, date="2024-01-26"),
        Transaction(id=2, user_id="user1", name="Apple", amount=0.99, date="2024-02-26"),
        Transaction(id=3, user_id="user1", name="Apple", amount=0.99, date="2024-03-26"),
        Transaction(id=4, user_id="user1", name="Apple", amount=0.99, date="2024-04-26"),
        Transaction(id=5, user_id="user1", name="Apple", amount=0.99, date="2024-05-26"),
    ]

    # Test for a valid monthly Apple transaction
    transaction = Transaction(id=6, user_id="user1", name="Apple", amount=0.99, date="2024-06-26")
    assert is_monthly_apple_storage(transaction, transactions) is True

    # Test for a transaction with a different name
    transaction = Transaction(id=7, user_id="user1", name="Google", amount=0.99, date="2024-06-26")
    assert is_monthly_apple_storage(transaction, transactions) is False

    # Test for a transaction with a different amount
    transaction = Transaction(id=8, user_id="user1", name="Apple", amount=1.99, date="2024-06-26")
    assert is_monthly_apple_storage(transaction, transactions) is False

    # Test for a transaction that does not occur monthly
    transactions = [
        Transaction(id=1, user_id="user1", name="Apple", amount=0.99, date="2024-01-26"),
        Transaction(id=2, user_id="user1", name="Apple", amount=0.99, date="2024-03-26"),
    ]
    transaction = Transaction(id=3, user_id="user1", name="Apple", amount=0.99, date="2024-04-26")
    assert is_monthly_apple_storage(transaction, transactions) is False


def test_get_cobblestone_recurrence_score() -> None:
    """
    Test that get_cobblestone_recurrence_score calculates the correct weighted recurrence score
    for Cobblestone Wash transactions.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="Cobblestone Wash", amount=39.0, date="2023-05-23"),
        Transaction(id=2, user_id="user1", name="Cobblestone Wash", amount=39.0, date="2023-06-23"),
        Transaction(id=3, user_id="user1", name="Cobblestone Wash", amount=39.0, date="2023-07-25"),
        Transaction(id=4, user_id="user1", name="Cobblestone Wash", amount=39.0, date="2023-08-23"),
        Transaction(id=5, user_id="user1", name="Cobblestone Wash", amount=39.0, date="2023-09-25"),
        Transaction(id=6, user_id="user1", name="Cobblestone Wash", amount=10.0, date="2023-10-24"),
        Transaction(id=7, user_id="user1", name="Cobblestone Wash", amount=39.0, date="2023-11-28"),
    ]

    # Test for a transaction with the primary amount (39.0)
    transaction = Transaction(id=8, user_id="user1", name="Cobblestone Wash", amount=39.0, date="2023-12-26")
    score = get_cobblestone_recurrence_score(transaction, transactions)
    assert 0.8 <= score <= 1.0, f"Expected score close to 1.0, got {score}"

    # Test for a transaction with a smaller amount (10.0)
    transaction = Transaction(id=9, user_id="user1", name="Cobblestone Wash", amount=10.0, date="2023-12-26")
    score = get_cobblestone_recurrence_score(transaction, transactions)
    assert 0.4 <= score <= 0.6, f"Expected score close to 0.5, got {score}"

    # Test for a transaction with a different vendor
    transaction = Transaction(id=10, user_id="user1", name="Other Vendor", amount=39.0, date="2023-12-26")
    score = get_cobblestone_recurrence_score(transaction, transactions)
    assert score == 0.0, f"Expected score 0.0 for a different vendor, got {score}"

    # Test for insufficient transactions
    transactions = [
        Transaction(id=1, user_id="user1", name="Cobblestone Wash", amount=39.0, date="2023-05-23"),
    ]
    transaction = Transaction(id=2, user_id="user1", name="Cobblestone Wash", amount=39.0, date="2023-06-23")
    score = get_cobblestone_recurrence_score(transaction, transactions)
    assert score == 0.0, f"Expected score 0.0 for insufficient transactions, got {score}"


def test_is_consistent_transaction_amount() -> None:
    """
    Test that is_consistent_transaction_amount correctly identifies consistent and inconsistent transactions.
    """
    transactions = [
        Transaction(id=1, user_id="user1", name="American Water Works", amount=114.88, date="2022-09-19"),
        Transaction(id=2, user_id="user1", name="American Water Works", amount=61.26, date="2022-11-14"),
        Transaction(id=3, user_id="user1", name="American Water Works", amount=136.05, date="2023-01-04"),
        Transaction(id=4, user_id="user1", name="American Water Works", amount=44.95, date="2023-02-27"),
        Transaction(id=5, user_id="user1", name="American Water Works", amount=59.87, date="2023-10-03"),
        Transaction(id=6, user_id="user1", name="American Water Works", amount=98.76, date="2023-11-09"),
    ]

    # Test for inconsistent transactions
    transaction = Transaction(id=7, user_id="user1", name="American Water Works", amount=52.82, date="2023-11-29")
    assert is_consistent_transaction_amount(transaction, transactions, threshold=0.2) is False

    # Test for consistent transactions
    consistent_transactions = [
        Transaction(id=1, user_id="user1", name="Vendor A", amount=50.0, date="2023-01-01"),
        Transaction(id=2, user_id="user1", name="Vendor A", amount=50.0, date="2023-02-01"),
        Transaction(id=3, user_id="user1", name="Vendor A", amount=50.0, date="2023-03-01"),
    ]
    transaction = Transaction(id=4, user_id="user1", name="Vendor A", amount=50.0, date="2023-04-01")
    assert is_consistent_transaction_amount(transaction, consistent_transactions, threshold=0.2) is True
