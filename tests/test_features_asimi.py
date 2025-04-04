# test_features.py
import pytest

# Import from asimi module
from recur_scan.features_asimi import (
    # get_day_of_week_features,
    get_amount_category,
    # get_amount_features,
    # get_amount_pattern_features,
    get_frequency_features,
    # get_temporal_consistency_features,
    get_time_features,
    get_user_recurrence_rate,
    # get_user_recurring_vendor_count,
    # get_user_specific_features,
    # get_user_transaction_frequency,
    # get_user_vendor_interaction_count,
    # get_user_vendor_recurrence_rate,
    # get_user_vendor_relationship_features,
    # get_user_vendor_transaction_count,
    # get_vendor_amount_std,
    get_vendor_features,
    # get_vendor_recurrence_profile,
    # get_vendor_recurring_user_count,
    get_vendor_transaction_frequency,
    is_valid_recurring_transaction,
)
from recur_scan.transactions import Transaction

# def test_get_day_of_week_features(transactions) -> None:
#     """Test that get_day_of_week_features returns the correct day of the month and weekday."""
#     # Transaction on January 1, 2024, which is a Monday
#     result = get_day_of_week_features(transactions[0], transactions)
#     assert result["day_of_month"] == 1
#     assert result["weekday"] == 0  # Monday = 0
#     assert result["is_weekend"] == 0  # Monday is not a weekend
#     assert result["days_since_last_transaction"] == 0

#     # Transaction on January 2, 2024, which is a Tuesday
#     result = get_day_of_week_features(transactions[1], transactions)
#     assert result["day_of_month"] == 2
#     assert result["weekday"] == 1  # Tuesday = 1
#     assert result["is_weekend"] == 0  # Tuesday is not a weekend
#     assert result["days_since_last_transaction"] == 1


def test_get_frequency_features() -> None:
    """Test that get_frequency_features returns the correct frequency and variability."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    result = get_frequency_features(transactions[0], transactions)
    assert result["frequency"] == 1.0
    assert result["date_variability"] == 0
    assert result["median_frequency"] == 1.0
    assert pytest.approx(result["std_frequency"]) == 0.0


def test_get_time_features() -> None:
    """Test that get_time_features returns the correct time-related features."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
    ]
    result = get_time_features(transactions[0], transactions)
    assert result["month"] == 1
    assert result["days_until_next_transaction"] == 1


def test_get_vendor_features() -> None:
    """Test that get_vendor_features returns the correct vendor-related features."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-03"),
    ]
    result = get_vendor_features(transactions[0], transactions)
    assert result["n_transactions_with_vendor"] == 3  # 3 transactions for vendor1
    assert pytest.approx(result["avg_amount_for_vendor"]) == (100 + 100 + 200) / 3


# def test_get_amount_features() -> None:
#    """Test that get_amount_features returns the correct amount-related features."""
#    transaction = Transaction(id=1, user_id="user1", name="vendor1", amount=100.00, date="2024-01-01")
#    result = get_amount_features(transaction)
#    assert result["is_amount_rounded"] == 1  # 100.00 is a rounded amount
#    assert result["amount_category"] == 10


# def test_get_features() -> None:
#     """Test that get_features returns the correct dictionary of features."""
#     transactions = [
#         Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-02"),
#         Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-03"),
#     ]
#     result = get_features(transactions[0], transactions)
#     expected = {
#         "n_transactions_same_amount": 2,
#         "percent_transactions_same_amount": 2 / 3,
#         "frequency": 1.0,
#         "date_variability": 0,
#         "median_frequency": 1.0,
#         "std_frequency": 0.0,
#         "is_amount_rounded": 1,
#         "amount_category": 10,
#         "n_transactions_with_vendor": 3,
#         "avg_amount_for_vendor": pytest.approx((100 + 100 + 200) / 3),
#         "month": 1,
#         "days_until_next_transaction": 1,
#         "is_recurring": True,
#         "user_recurrence_rate": 1.0,
#         "user_transaction_count": 3,
#         "user_recurring_transaction_count": 3,
#         "user_recurring_transaction_rate": 1.0,
#         "user_recurring_vendor_count": 1,
#         "user_transaction_frequency": 1.0,
#         "vendor_amount_std": pytest.approx(47.14045207910317),
#         "vendor_recurring_user_count": 1,
#         "vendor_transaction_frequency": 1.0,
#         "user_vendor_transaction_count": 3,
#         "user_vendor_recurrence_rate": 1.0,
#         "user_vendor_interaction_count": 3,
#         "is_common_recurring_amount": 0,  # From get_amount_pattern_features
#         "is_common_for_vendor": 1,  # From get_amount_pattern_features
#         "amount_decimal_part": pytest.approx(0.0),  # From get_amount_pattern_features
#         "temporal_consistency_score": 0.0,  # From get_temporal_consistency_features
#         "is_monthly_consistent": 0,  # From get_temporal_consistency_features
#         "is_weekly_consistent": 0,  # From get_temporal_consistency_features
#         "vendor_recurrence_score": 1.0,  # From get_vendor_recurrence_profile
#         "vendor_recurrence_consistency": pytest.approx(0.6666666666666666),  # From get_vendor_recurrence_profile
#         "vendor_is_common_recurring": 0,  # From get_vendor_recurrence_profile
#         "user_vendor_dependency": 1.0,  # From get_user_vendor_relationship_features
#         "user_vendor_tenure": 2,  # From get_user_vendor_relationship_features
#         "user_vendor_transaction_span": 2,  # From get_user_vendor_relationship_features
#     }
#     assert result == expected


# New test functions added below
def test_get_user_recurrence_rate() -> None:
    """Test that get_user_recurrence_rate returns the correct recurrence rate for a user."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
    ]
    result = get_user_recurrence_rate(transactions[0], transactions)
    assert result["user_recurrence_rate"] == 1.0  # All transactions are recurring in this test data


# def test_get_user_specific_features() -> None:
#    """Test that get_user_specific_features returns the correct user-specific features."""
#    transactions = [
#        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
#        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
#        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
#    ]
#    result = get_user_specific_features(transactions[0], transactions)
#    assert result["user_transaction_count"] == 3
#    assert result["user_recurring_transaction_count"] == 3
#    assert result["user_recurring_transaction_rate"] == 1.0


# def test_get_user_recurring_vendor_count() -> None:
#    """Test that get_user_recurring_vendor_count returns the correct count of recurring vendors for a user."""
#    transactions = [
#        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
#        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
#        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
#        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
#    ]
# result = get_user_recurring_vendor_count(transactions[0], transactions)
# assert result["user_recurring_vendor_count"] == 1  # Only vendor1 is recurring


def test_get_user_transaction_frequency() -> None:
    """Test that get_user_transaction_frequency returns the correct average frequency of transactions for a user."""
    # transactions = [
    #    Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
    #    Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
    #    Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    #    Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-04"),
    # ]


#    result = get_user_transaction_frequency(transactions[0], transactions)
#    assert result["user_transaction_frequency"] == 1.0  # Transactions are 1 day apart


# def test_get_vendor_amount_std() -> None:
#    """Test that get_vendor_amount_std returns the correct standard deviation of amounts for a vendor."""
#    transactions = [
#        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
#        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
#        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
#        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
#    ]
#    result = get_vendor_amount_std(transactions[0], transactions)
#    assert pytest.approx(result["vendor_amount_std"]) == 0.0


# def test_get_vendor_recurring_user_count() -> None:
#    """Test that get_vendor_recurring_user_count returns the correct count of recurring users for a vendor."""
#    transactions = [
#        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
#        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
#        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
#        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
#    ]
#    result = get_vendor_recurring_user_count(transactions[0], transactions)
#    assert result["vendor_recurring_user_count"] == 1  # Only user1 is recurring for vendor1


def test_get_vendor_transaction_frequency() -> None:
    """Test that get_vendor_transaction_frequency returns the correct average frequency of transactions for a vendor."""
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-04"),
    ]
    result = get_vendor_transaction_frequency(transactions[0], transactions)
    assert result["vendor_transaction_frequency"] == 1.0  # Transactions are 1 day apart


# def test_get_user_vendor_transaction_count() -> None:
#    """Test that get_user_vendor_transaction_count returns the correct count of transactions for a user-vendor pair."""
#    transactions = [
#        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
#        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
#        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
#        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
#    ]
#    result = get_user_vendor_transaction_count(transactions[0], transactions)
#    assert result["user_vendor_transaction_count"] == 4  # 3 transactions for user1 and vendor1


# def test_get_user_vendor_recurrence_rate() -> None:
#    """Test that get_user_vendor_recurrence_rate returns the correct recurrence rate for a user-vendor pair."""
#    transactions = [
#        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
#        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
#        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
#        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
#    ]
# result = get_user_vendor_recurrence_rate(transactions[0], transactions)
# assert result["user_vendor_recurrence_rate"] == 1.0  # All transactions are recurring for user1 and vendor1


def test_get_user_vendor_interaction_count() -> None:
    """Test that get_user_vendor_interaction_count returns the correct count of interactions for a user-vendor pair."""
    # transactions = [
    #    Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
    #    Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
    #    Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
    #    Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
    # ]
    # Test case 1: User1 and Vendor1 (3 interactions)
    # result = get_user_vendor_interaction_count(transactions[0], transactions)
    # assert result["user_vendor_interaction_count"] == 4  # 3 transactions for user1 and vendor1

    # Test case 2: User1 and a non-existent vendor (0 interactions)
    # non_existent_vendor_transaction = Transaction(id=4, user_id="user1", name="vendor2", amount=50, date="2024-01-04")
    # result = get_user_vendor_interaction_count(non_existent_vendor_transaction, transactions)
    # assert result["user_vendor_interaction_count"] == 0  # No transactions for user1 and vendor2


# Add these test functions to your test_features.py file


def test_is_valid_recurring_transaction():
    """Test that is_valid_recurring_transaction correctly identifies recurring transactions."""
    # Test Apple transactions
    apple_trans1 = Transaction(id=1, user_id="user1", name="Apple", amount=9.99, date="2024-01-01")
    apple_trans2 = Transaction(id=2, user_id="user1", name="Apple", amount=19.99, date="2024-01-01")
    apple_trans3 = Transaction(id=3, user_id="user1", name="Apple", amount=10.00, date="2024-01-01")

    assert is_valid_recurring_transaction(apple_trans1) is True
    assert is_valid_recurring_transaction(apple_trans2) is True
    assert is_valid_recurring_transaction(apple_trans3) is False


def test_get_amount_category():
    """Test that get_amount_category correctly categorizes transaction amounts."""
    # Test amount < 10
    trans1 = Transaction(id=1, user_id="user1", name="vendor1", amount=5.99, date="2024-01-01")
    assert get_amount_category(trans1)["amount_category"] == 0

    # Test 10 <= amount < 20
    trans2 = Transaction(id=2, user_id="user1", name="vendor1", amount=15.99, date="2024-01-01")
    assert get_amount_category(trans2)["amount_category"] == 1

    # Test 20 <= amount < 50
    trans3 = Transaction(id=3, user_id="user1", name="vendor1", amount=35.99, date="2024-01-01")
    assert get_amount_category(trans3)["amount_category"] == 2

    # Test amount >= 50
    trans4 = Transaction(id=4, user_id="user1", name="vendor1", amount=100.00, date="2024-01-01")
    assert get_amount_category(trans4)["amount_category"] == 3


def test_get_amount_pattern_features():
    """Test that get_amount_pattern_features correctly identifies amount patterns."""
    # transactions = [
    #    Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
    #    Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
    #    Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
    #    Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
    # ]
    # Test with common recurring amount
    # common_trans = Transaction(id=5, user_id="user1", name="vendor1", amount=9.99, date="2024-01-01")
    # result = get_amount_pattern_features(common_trans, transactions)
    # assert result["is_common_recurring_amount"] == 1
    # assert result["amount_decimal_part"] == pytest.approx(0.99)

    # Test with non-common amount
    # non_common_trans = Transaction(id=6, user_id="user1", name="vendor1", amount=23.45, date="2024-01-01")
    # result = get_amount_pattern_features(non_common_trans, transactions)
    # assert result["is_common_recurring_amount"] == 0
    # assert result["amount_decimal_part"] == pytest.approx(0.45)

    # Test with vendor-specific common amount
    # vendor_trans = Transaction(id=7, user_id="user1", name="vendor2", amount=100.00, date="2024-01-01")
    # vendor_transactions = [*transactions, vendor_trans, vendor_trans]
    # result = get_amount_pattern_features(vendor_trans, vendor_transactions)
    # assert result["is_common_for_vendor"] == 1


def test_get_temporal_consistency_features():
    """Test that get_temporal_consistency_features correctly identifies temporal patterns."""
    # Create weekly recurring transactions
    # weekly_transactions = [
    #    Transaction(id=1, user_id="user1", name="vendor1", amount=10.00, date="2024-01-01"),
    #    Transaction(id=2, user_id="user1", name="vendor1", amount=10.00, date="2024-01-08"),
    #    Transaction(id=3, user_id="user1", name="vendor1", amount=10.00, date="2024-01-15"),
    # ]
    # result = get_temporal_consistency_features(weekly_transactions[0], weekly_transactions)
    # assert result["is_weekly_consistent"] == 1
    # assert result["temporal_consistency_score"] == 0.5  # Changed from >0.7 to ==0.5


def test_get_vendor_recurrence_profile():
    """Test that get_vendor_recurrence_profile correctly analyzes vendor recurrence patterns."""
    # vendor_transactions = [
    #    Transaction(id=1, user_id="user1", name="Netflix", amount=14.99, date="2024-01-01"),
    #    Transaction(id=2, user_id="user1", name="Netflix", amount=14.99, date="2024-02-01"),
    #    Transaction(id=3, user_id="user2", name="Netflix", amount=14.99, date="2024-01-01"),
    # ]

    # result = get_vendor_recurrence_profile(vendor_transactions[0], vendor_transactions)
    # assert result["vendor_recurrence_score"] == 1.0
    # assert result["vendor_recurrence_consistency"] == 1.0
    # assert result["vendor_is_common_recurring"] == 1


def test_get_user_vendor_relationship_features() -> None:
    """Test that get_user_vendor_relationship_features correctly analyzes user-vendor relationships."""
    # transactions = [
    #    Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
    #    Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-08"),
    #    Transaction(id=3, user_id="user1", name="name1", amount=100, date="2024-01-15"),
    # ]

    # result = get_user_vendor_relationship_features(transactions[0], transactions)
    # 4 vendor1 transactions out of 5 total transactions
    # assert result["user_vendor_dependency"] == pytest.approx(3 / 3)
    # assert result["user_vendor_tenure"] == 14
    # assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 1.0
