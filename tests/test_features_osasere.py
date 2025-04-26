# test features
import pytest

from recur_scan.features_osasere import (
    detect_financial_service_fees,
    detect_housing_payments,
    detect_installment_payments,
    detect_insurance_payments,
    detect_streaming_services,
    get_day_of_month_consistency,
    get_day_of_month_variability,
    # new imports
    get_fixed_recurring,
    get_median_period,
    get_recurrence_confidence,
    has_consistent_amount,
    has_min_recurrence_period,
    has_regular_interval,
    is_likely_recurring_by_merchant,
    is_weekday_consistent,
    normalize_vendor_name,
)
from recur_scan.transactions import Transaction


def test_has_min_recurrence_period() -> None:
    """Test that has_min_recurrence_period correctly identifies if transactions span min_days."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-15"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-15"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-03-15"),
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-01-01"),
    ]
    # Netflix spans 60 days (Jan 15 to Mar 15)
    assert has_min_recurrence_period(transactions[0], transactions, min_days=60)
    # Spotify only has one transaction
    assert not has_min_recurrence_period(transactions[3], transactions)


# Osaseres tests
def test_get_day_of_month_consistency() -> None:
    """Test that get_day_of_month_consistency calculates correct fraction of matching dates."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-15"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-15"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-03-16"),  # +1 day
        Transaction(id=4, user_id="user1", name="Netflix", amount=15.99, date="2024-04-10"),  # -5 days
        Transaction(id=5, user_id="user1", name="Amazon", amount=12.99, date="2024-01-31"),
        Transaction(id=6, user_id="user1", name="Amazon", amount=12.99, date="2024-02-28"),
    ]
    # Netflix: 3/4 transactions within ±1 day of 15th
    assert get_day_of_month_consistency(transactions[0], transactions, tolerance_days=1) == 0.75
    # Amazon: both transactions treated as month-end
    assert get_day_of_month_consistency(transactions[4], transactions, tolerance_days=3) == 1.0


def test_get_day_of_month_variability() -> None:
    """Test that get_day_of_month_variability calculates correct standard deviation."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Consistent", amount=10.00, date="2024-01-15"),
        Transaction(id=2, user_id="user1", name="Consistent", amount=10.00, date="2024-02-15"),
        Transaction(id=3, user_id="user1", name="Variable", amount=10.00, date="2024-01-05"),
        Transaction(id=4, user_id="user1", name="Variable", amount=10.00, date="2024-02-20"),
        Transaction(id=5, user_id="user1", name="MonthEnd", amount=10.00, date="2024-01-31"),
        Transaction(id=6, user_id="user1", name="MonthEnd", amount=10.00, date="2024-02-28"),
    ]
    # Consistent dates should have low variability
    assert get_day_of_month_variability(transactions[0], transactions) < 1.0
    # Variable dates should have higher variability
    assert get_day_of_month_variability(transactions[2], transactions) > 7.0
    # Month-end dates should be treated as similar
    assert get_day_of_month_variability(transactions[4], transactions) < 3.0


def test_get_recurrence_confidence() -> None:
    """Test that get_recurrence_confidence calculates correct weighted confidence score."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Regular", amount=10.00, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Regular", amount=10.00, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Regular", amount=10.00, date="2024-03-01"),
        Transaction(id=4, user_id="user1", name="Irregular", amount=10.00, date="2024-01-01"),
        Transaction(id=5, user_id="user1", name="Irregular", amount=10.00, date="2024-01-15"),
        Transaction(id=6, user_id="user1", name="Irregular", amount=10.00, date="2024-03-20"),
    ]
    # Regular monthly transactions should have high confidence
    assert get_recurrence_confidence(transactions[0], transactions) > 0.7
    # Irregular transactions should have low confidence
    assert get_recurrence_confidence(transactions[3], transactions) < 0.5


def test_is_weekday_consistent() -> None:
    """Test that is_weekday_consistent correctly identifies consistent weekdays."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Weekly", amount=5.00, date="2024-01-01"),  # Monday
        Transaction(id=2, user_id="user1", name="Weekly", amount=5.00, date="2024-01-08"),  # Monday
        Transaction(id=3, user_id="user1", name="Biweekly", amount=10.00, date="2024-01-01"),  # Monday
        Transaction(id=4, user_id="user1", name="Biweekly", amount=10.00, date="2024-01-15"),  # Monday
        Transaction(id=5, user_id="user1", name="Random", amount=15.00, date="2024-01-01"),  # Monday
        Transaction(id=6, user_id="user1", name="Random", amount=15.00, date="2024-01-03"),  # Wednesday
        Transaction(id=7, user_id="user1", name="Random", amount=15.00, date="2024-01-07"),  # Sunday
    ]
    # Consistent weekday (all Mondays)
    assert is_weekday_consistent(transactions[0], transactions)
    # Also consistent (only 2 weekdays)
    assert is_weekday_consistent(transactions[2], transactions)
    # Inconsistent (3 different weekdays)
    assert not is_weekday_consistent(transactions[4], transactions)


def test_get_median_period() -> None:
    """Test that get_median_period calculates correct median days between transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Monthly", amount=10.00, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Monthly", amount=10.00, date="2024-02-01"),  # 31 days
        Transaction(id=3, user_id="user1", name="Monthly", amount=10.00, date="2024-03-01"),  # 29 days
        Transaction(id=4, user_id="user1", name="Biweekly", amount=5.00, date="2024-01-01"),
        Transaction(id=5, user_id="user1", name="Biweekly", amount=5.00, date="2024-01-15"),  # 14 days
        Transaction(id=6, user_id="user1", name="Biweekly", amount=5.00, date="2024-01-29"),  # 14 days
        Transaction(id=7, user_id="user1", name="Single", amount=20.00, date="2024-01-01"),
    ]
    # Monthly transactions median should be ~30 days
    assert get_median_period(transactions[0], transactions) == pytest.approx(30.0, abs=1.0)
    # Biweekly transactions median should be 14 days
    assert get_median_period(transactions[3], transactions) == 14.0
    # Single transaction should return 0
    assert get_median_period(transactions[6], transactions) == 0.0


# Helper function to create transactions
def create_transaction(id, name, amount, date):
    return Transaction(id=id, user_id="test_user", name=name, amount=amount, date=date)


# Test data
SAMPLE_TRANSACTIONS = [
    create_transaction(1, "Netflix Subscription", 15.99, "2024-01-15"),
    create_transaction(2, "Netflix Subscription", 15.99, "2024-02-15"),
    create_transaction(3, "AfterPay Payment", 50.00, "2024-01-01"),
    create_transaction(4, "AfterPay Payment", 50.00, "2024-01-15"),
    create_transaction(5, "Albert App Fee", 5.00, "2024-01-01"),
    create_transaction(6, "Albert App Fee", 5.00, "2024-02-01"),
    create_transaction(7, "Albert App Fee", 5.00, "2024-03-01"),
    create_transaction(8, "Rent - Apartment LLC", 1200.00, "2024-01-01"),
    create_transaction(9, "Rent - Apartment LLC", 1200.00, "2024-02-01"),
    create_transaction(10, "GEICO Insurance", 85.00, "2024-01-01"),
    create_transaction(11, "Kikoff Credit Builder", 10.00, "2024-01-01"),
    create_transaction(12, "Spotify Premium", 9.99, "2024-01-01"),
    create_transaction(13, "Amazon Prime Video", 12.99, "2024-01-01"),
    create_transaction(14, "Variable Payment Inc", 100.00, "2024-01-01"),
    create_transaction(15, "Variable Payment Inc", 105.00, "2024-02-01"),
    create_transaction(16, "Irregular Service", 20.00, "2024-01-01"),
    create_transaction(17, "Irregular Service", 20.00, "2024-03-15"),
    create_transaction(18, "Rent - 123 Main St Apt 3B", 1500.00, "2024-01-01"),
    create_transaction(19, "Rent - 123 Main St Apt 3B", 1500.00, "2024-02-01"),
]


def test_get_fixed_recurring():
    """Test fixed recurring payment detection."""
    t = create_transaction(1, "Netflix Subscription", 15.99, "2024-01-15")
    assert get_fixed_recurring("Netflix", t) is True
    assert get_fixed_recurring("Spotify", t) is False
    assert get_fixed_recurring("netflix", t) is True  # Case insensitive
    assert get_fixed_recurring("flix", t) is True  # Partial match


def test_detect_installment_payments():
    """Test installment payment detection."""
    # Positive case
    t = SAMPLE_TRANSACTIONS[2]  # AfterPay Payment
    assert detect_installment_payments(t, SAMPLE_TRANSACTIONS) is True

    # Negative case - wrong interval
    bad_interval = [
        create_transaction(21, "Klarna Payment", 75.00, "2024-01-01"),
        create_transaction(22, "Klarna Payment", 75.00, "2024-03-01"),  # >20 days apart
    ]
    assert detect_installment_payments(bad_interval[0], bad_interval) is False


def test_detect_financial_service_fees():
    """Test financial service fee detection."""
    # Positive case (Albert has 3 consistent payments)
    t = SAMPLE_TRANSACTIONS[4]
    assert detect_financial_service_fees(t, SAMPLE_TRANSACTIONS) is True

    # Negative case - not enough transactions
    single_fee = create_transaction(23, "Dave App Fee", 3.00, "2024-01-01")
    assert detect_financial_service_fees(single_fee, SAMPLE_TRANSACTIONS) is False

    # Negative case - inconsistent amounts
    inconsistent = [
        create_transaction(24, "FloatMe Fee", 5.00, "2024-01-01"),
        create_transaction(25, "FloatMe Fee", 10.00, "2024-02-01"),
        create_transaction(26, "FloatMe Fee", 5.00, "2024-03-01"),
    ]
    assert detect_financial_service_fees(inconsistent[0], inconsistent) is False


def test_normalize_vendor_name():
    """Test vendor name normalization."""
    assert normalize_vendor_name("Apartment LLC") == "apartment"
    assert normalize_vendor_name("Rent - 123 Main St Apt 3B") == "rent"
    assert normalize_vendor_name("GEICO Insurance Corp") == "geico insurance"
    assert normalize_vendor_name("Netflix Subscription") == "netflix subscription"
    assert normalize_vendor_name("Payment Inc 555-123-4567") == "payment"
    assert normalize_vendor_name("Service Co contact@example.com") == "service"


def test_detect_housing_payments():
    """Test housing payment detection."""
    # Positive case - consistent monthly payments
    t = SAMPLE_TRANSACTIONS[7]
    assert detect_housing_payments(t, SAMPLE_TRANSACTIONS) is True

    # Positive case - normalized name matching
    t = SAMPLE_TRANSACTIONS[17]
    assert detect_housing_payments(t, SAMPLE_TRANSACTIONS) is True

    # Negative case - not housing related
    t = SAMPLE_TRANSACTIONS[0]
    assert detect_housing_payments(t, SAMPLE_TRANSACTIONS) is False


def test_detect_streaming_services():
    """Test streaming service detection."""
    assert detect_streaming_services(SAMPLE_TRANSACTIONS[0]) is True  # Netflix
    assert detect_streaming_services(SAMPLE_TRANSACTIONS[11]) is True  # Spotify
    assert detect_streaming_services(SAMPLE_TRANSACTIONS[12]) is True  # Amazon Prime
    assert detect_streaming_services(SAMPLE_TRANSACTIONS[4]) is False  # Albert


def test_detect_insurance_payments():
    """Test insurance payment detection."""
    assert detect_insurance_payments(SAMPLE_TRANSACTIONS[9]) is True  # GEICO
    assert detect_insurance_payments(create_transaction(30, "Progressive Insurance", 120.00, "2024-01-01")) is True
    assert detect_insurance_payments(SAMPLE_TRANSACTIONS[0]) is False  # Netflix


def test_is_likely_recurring_by_merchant():
    """Test merchant-based recurring detection."""
    assert is_likely_recurring_by_merchant(SAMPLE_TRANSACTIONS[10]) is True  # Kikoff
    assert is_likely_recurring_by_merchant(SAMPLE_TRANSACTIONS[4]) is True  # Albert
    assert is_likely_recurring_by_merchant(SAMPLE_TRANSACTIONS[0]) is False  # Netflix


def test_has_consistent_amount():
    """Test consistent amount detection."""
    # Exact match case
    t = SAMPLE_TRANSACTIONS[0]
    assert has_consistent_amount(t, SAMPLE_TRANSACTIONS) is True

    # Approximate match case
    t = SAMPLE_TRANSACTIONS[13]
    assert has_consistent_amount(t, SAMPLE_TRANSACTIONS, exact_match=False) is True
    assert has_consistent_amount(t, SAMPLE_TRANSACTIONS, exact_match=True) is False

    # Negative case
    t = create_transaction(31, "Inconsistent", 10.00, "2024-01-01")
    inconsistent = [
        t,
        create_transaction(32, "Inconsistent", 20.00, "2024-02-01"),
        create_transaction(33, "Inconsistent", 10.00, "2024-03-01"),
    ]
    assert has_consistent_amount(t, inconsistent) is False


def test_has_regular_interval():
    """Test regular interval detection."""
    t = SAMPLE_TRANSACTIONS[0]
    assert has_regular_interval(t, SAMPLE_TRANSACTIONS) is False

    # Negative case - not enough transactions
    t = create_transaction(34, "New Service", 10.00, "2024-01-01")
    few_transactions = [
        t,
        create_transaction(35, "New Service", 10.00, "2024-02-01"),
    ]
    assert has_regular_interval(t, few_transactions) is False

    # Negative case - irregular intervals
    t = SAMPLE_TRANSACTIONS[15]
    assert has_regular_interval(t, SAMPLE_TRANSACTIONS) is False
