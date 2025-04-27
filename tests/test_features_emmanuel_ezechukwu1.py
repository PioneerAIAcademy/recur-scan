import pytest

from recur_scan.features_emmanuel_ezechukwu1 import (
    # get_amount_cv,
    get_amount_range_consistency,
    # get_day_of_month_consistency,
    # get_days_between_std,
    # get_exact_amount_count,
    get_has_recurring_keyword,
    get_is_always_recurring,
    get_is_convenience_store,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    # get_merchant_name_similarity,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_new_features,
    get_pct_transactions_days_apart,
    get_percent_transactions_same_amount,
    get_recurring_period_score,
    get_transaction_frequency_score,
)
from recur_scan.transactions import Transaction, group_transactions


def test_get_n_transactions_same_amount() -> None:
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert get_n_transactions_same_amount(transactions[0], transactions) == 2
    assert get_n_transactions_same_amount(transactions[2], transactions) == 1


# def test_get_days_between_std():
#     sample_transactions = [
#         Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-03"),
#         Transaction(id=3, user_id="user1", name="name1", amount=100, date="2024-01-05"),
#         Transaction(id=4, user_id="user1", name="name1", amount=100, date="2024-01-07"),
#         Transaction(id=5, user_id="user1", name="name1", amount=100, date="2024-01-09"),
#     ]
#     grouped = group_transactions(sample_transactions)
#     results = [get_days_between_std(t, grouped) for t in sample_transactions]
#     assert all(result is not None for result in results)


# def test_get_amount_cv():
#     transactions = [
#         Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="name1", amount=200, date="2024-01-02"),
#         Transaction(id=3, user_id="user1", name="name1", amount=150, date="2024-01-03"),
#         Transaction(id=4, user_id="user1", name="name1", amount=175, date="2024-01-04"),
#         Transaction(id=5, user_id="user1", name="name1", amount=225, date="2024-01-05"),
#     ]
#     grouped = group_transactions(transactions)
#     result = get_amount_cv(transactions[0], grouped)
#     assert result >= 0


def test_get_percent_transactions_same_amount() -> None:
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-01-01"),
        Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-01-02"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-03"),
    ]
    assert pytest.approx(get_percent_transactions_same_amount(transactions[0], transactions)) == 0.5


def test_get_n_transactions_days_apart() -> None:
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=5, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=6, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=7, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    # assert get_n_transactions_days_apart(transactions[0], transactions, 14, 0) == 1
    assert get_n_transactions_days_apart(transactions[0], transactions, 14, 1) == 3


def test_get_pct_transactions_days_apart() -> None:
    transactions = [
        Transaction(id=1, user_id="user1", name="name1", amount=2.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="name1", amount=2.99, date="2024-01-02"),
        Transaction(id=3, user_id="user1", name="name1", amount=2.99, date="2024-01-14"),
        Transaction(id=4, user_id="user1", name="name1", amount=2.99, date="2024-01-15"),
        Transaction(id=5, user_id="user1", name="name1", amount=2.99, date="2024-01-16"),
        Transaction(id=6, user_id="user1", name="name1", amount=2.99, date="2024-01-29"),
        Transaction(id=7, user_id="user1", name="name1", amount=2.99, date="2024-01-31"),
    ]
    # assert pytest.approx(get_pct_transactions_days_apart(transactions[0], transactions, 14, 0)) == 2 / 7
    assert pytest.approx(get_pct_transactions_days_apart(transactions[0], transactions, 14, 1)) == 3 / 7


def test_get_is_insurance() -> None:
    assert get_is_insurance(
        Transaction(id=1, user_id="user1", name="Allstate Insurance", amount=100, date="2024-01-01")
    )
    assert not get_is_insurance(Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"))


def test_get_is_phone() -> None:
    assert get_is_phone(Transaction(id=2, user_id="user1", name="AT&T", amount=100, date="2024-01-01"))
    assert not get_is_phone(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))


def test_get_is_utility() -> None:
    assert get_is_utility(Transaction(id=3, user_id="user1", name="Duke Energy", amount=200, date="2024-01-02"))
    assert not get_is_utility(
        Transaction(id=4, user_id="user1", name="HighEnergy Soft Drinks", amount=2.99, date="2024-01-03")
    )


def test_get_is_always_recurring() -> None:
    assert get_is_always_recurring(Transaction(id=1, user_id="user1", name="netflix", amount=100, date="2024-01-01"))
    assert not get_is_always_recurring(
        Transaction(id=2, user_id="user1", name="walmart", amount=100, date="2024-01-01")
    )


# def test_get_day_of_month_consistency() -> None:
#     transactions_same_day = [
#         Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-02-01"),
#         Transaction(id=3, user_id="user1", name="name1", amount=100, date="2024-03-01"),
#     ]
#     grouped = group_transactions(transactions_same_day)
#     result_same_day = get_day_of_month_consistency(transactions_same_day[0], grouped)
#     assert result_same_day == pytest.approx(0.0, abs=1e-5)

#     transactions_diff_days = [
#         Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-02-15"),
#         Transaction(id=3, user_id="user1", name="name1", amount=100, date="2024-03-30"),
#     ]
#     grouped = group_transactions(transactions_diff_days)
#     result_diff_days = get_day_of_month_consistency(transactions_diff_days[0], grouped)
#     assert result_diff_days == pytest.approx(0.20184908652385852, abs=1e-5)
#     assert result_diff_days > result_same_day

# transactions_no_match = [
#     Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
#     Transaction(id=2, user_id="user2", name="name1", amount=100, date="2024-02-01"),
# ]
# grouped = group_transactions(transactions_no_match)
# result_no_match = get_day_of_month_consistency(transactions_no_match[0], grouped)
# assert result_no_match == 1.0


# def test_get_exact_amount_count() -> None:
#     transactions_same_amount = [
#         Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="name1", amount=100, date="2024-02-01"),
#         Transaction(id=3, user_id="user1", name="name1", amount=200, date="2024-03-01"),
#     ]
#     grouped = group_transactions(transactions_same_amount)
#     assert get_exact_amount_count(transactions_same_amount[0], grouped) == 2

#     transactions_diff_amount = [
#         Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="name1", amount=200, date="2024-02-01"),
#     ]
#     grouped = group_transactions(transactions_diff_amount)
#     assert get_exact_amount_count(transactions_diff_amount[0], grouped) == 1

#     transactions_no_match = [
#         Transaction(id=1, user_id="user1", name="name1", amount=100, date="2024-01-01"),
#         Transaction(id=2, user_id="user2", name="name1", amount=100, date="2024-02-01"),
#     ]
#     grouped = group_transactions(transactions_no_match)
#     assert get_exact_amount_count(transactions_no_match[0], grouped) == 1


def test_get_has_recurring_keyword() -> None:
    assert (
        get_has_recurring_keyword(
            Transaction(id=1, user_id="user1", name="Netflix Subscription", amount=100, date="2024-01-01")
        )
        == 1
    )
    assert (
        get_has_recurring_keyword(Transaction(id=2, user_id="user1", name="Walmart", amount=100, date="2024-01-01"))
        == 0
    )


def test_get_is_convenience_store() -> None:
    assert (
        get_is_convenience_store(Transaction(id=1, user_id="user1", name="7-Eleven", amount=100, date="2024-01-01"))
        == 1
    )
    assert (
        get_is_convenience_store(Transaction(id=2, user_id="user1", name="Netflix", amount=100, date="2024-01-01")) == 0
    )


def test_get_new_features():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Netflix Inc", amount=15.99, date="2024-03-01"),
    ]
    # grouped = group_transactions(transactions)
    features = get_new_features(transactions[0], transactions)
    assert isinstance(features, dict)
    # assert len(features) == 18
    assert all(isinstance(f, int | float) for f in features.values())
    assert features["is_always_recurring"] == 1
    assert features["amount_range_consistency"] > 0
    assert features["recurring_period_score"] > 0
    # assert features["merchant_name_similarity"] > 0
    assert features["transaction_frequency_score"] > 0


def test_get_amount_range_consistency():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=16.00, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=20.00, date="2024-03-01"),
    ]
    grouped = group_transactions(transactions)
    result = get_amount_range_consistency(transactions[0], grouped)
    assert result == pytest.approx(2 / 3, abs=1e-5)


def test_get_recurring_period_score():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-04-01"),
    ]
    grouped = group_transactions(transactions)
    result = get_recurring_period_score(transactions[0], grouped)
    assert result > 0


# def test_get_merchant_name_similarity():
#     transactions = [
#         Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
#         Transaction(id=2, user_id="user1", name="Netflix Inc", amount=15.99, date="2024-02-01"),
#     ]
#     result = get_merchant_name_similarity(transactions[0], transactions)
#     assert result > 0.5


def test_get_transaction_frequency_score():
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Walmart", amount=50.00, date="2024-03-01"),
    ]
    grouped = group_transactions(transactions)
    result = get_transaction_frequency_score(transactions[0], grouped)
    assert result == pytest.approx(2 / 3, abs=1e-5)
