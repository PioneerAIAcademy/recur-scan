import unittest

# Import the functions to be tested
from recur_scan.features import (
    classify_subscription_tier,
    count_transactions_by_amount,
    get_amount_features,
    get_features,
    get_monthly_spending_trend,
    get_recurrence_patterns,
    get_recurring_consistency_score,
    get_refund_features,
    get_user_behavior_features,
    validate_recurring_transaction,
)
from recur_scan.transactions import Transaction


class TestTransactionFeatures(unittest.TestCase):
    def setUp(self):
        # Sample transactions for testing
        self.transactions = [
            Transaction(name="Netflix", amount=15.49, date="2023-01-01", user_id=1),
            Transaction(name="Netflix", amount=15.49, date="2023-02-01", user_id=1),
            Transaction(name="Netflix", amount=15.49, date="2023-03-01", user_id=1),
            Transaction(name="Spotify", amount=9.99, date="2023-01-01", user_id=1),
            Transaction(name="Spotify", amount=9.99, date="2023-02-01", user_id=1),
            Transaction(name="Amazon Prime", amount=12.99, date="2023-01-01", user_id=1),
        ]

    def test_count_transactions_by_amount(self):
        transaction = self.transactions[0]  # Netflix, 15.49
        count, pct = count_transactions_by_amount(transaction, self.transactions)
        assert count == 3  # 3 Netflix transactions with amount 15.49
        assert abs(pct - 0.5) < 1e-6  # 3 out of 6 transactions

    def test_get_recurrence_patterns(self):
        transaction = self.transactions[0]  # Netflix, 15.49
        patterns = get_recurrence_patterns(transaction, self.transactions)
        assert patterns["is_monthly"] == 1  # Monthly recurrence
        assert abs(patterns["avg_days_between"] - 30.0) < 1e-6  # Average days between transactions
        assert abs(patterns["std_days_between"] - 0.0) < 1e-6  # No deviation
        assert patterns["recurrence_score"] > 0.9  # High recurrence score

    def test_get_recurring_consistency_score(self):
        transaction = self.transactions[0]  # Netflix, 15.49
        score = get_recurring_consistency_score(transaction, self.transactions)
        assert score["recurring_consistency_score"] >= 0.9  # High consistency score

    def test_validate_recurring_transaction(self):
        transaction = self.transactions[0]  # Netflix, 15.49
        assert validate_recurring_transaction(transaction)  # Netflix is in RECURRING_VENDORS

    def test_classify_subscription_tier(self):
        transaction = self.transactions[0]  # Netflix, 15.49
        tier = classify_subscription_tier(transaction)
        assert tier == "Standard"  # Netflix Standard tier

    def test_get_amount_features(self):
        transaction = self.transactions[0]  # Netflix, 15.49
        features = get_amount_features(transaction, self.transactions)
        assert features["is_fixed_amount_recurring"] == 1  # Fixed amount
        assert abs(features["amount_fluctuation"] - 0.0) < 1e-6  # No fluctuation
        assert features["price_cluster"] == 0  # Cluster 0

    def test_get_user_behavior_features(self):
        transaction = self.transactions[0]  # Netflix, 15.49
        features = get_user_behavior_features(transaction, self.transactions)
        assert abs(features["user_avg_spent"] - 13.24) < 1e-2  # Average spending
        assert abs(features["user_total_spent"] - 79.44) < 1e-2  # Total spending
        assert features["user_subscription_count"] == 3  # 3 subscriptions

    def test_get_refund_features(self):
        transaction = self.transactions[0]  # Netflix, 15.49
        refund_transaction = Transaction(name="Netflix", amount=-15.49, date="2023-01-02", user_id=1)
        transactions_with_refund = [*self.transactions, refund_transaction]  # Fix RUF005
        features = get_refund_features(transaction, transactions_with_refund)
        assert abs(features["refund_rate"] - (1 / 7)) < 1e-6  # 1 refund out of 7 transactions
        assert abs(features["avg_refund_time_lag"] - 1.0) < 1e-6  # 1 day lag

    def test_get_monthly_spending_trend(self):
        transaction = self.transactions[0]  # Netflix, 15.49, January 2023
        features = get_monthly_spending_trend(transaction, self.transactions)
        assert abs(features["monthly_spending_trend"] - 38.47) < 1e-2  # Total spending in January 2023

    def test_get_features(self):
        transaction = self.transactions[0]  # Netflix, 15.49
        features = get_features(transaction, self.transactions)
        assert features["n_transactions_same_amount"] == 3  # 3 transactions with same amount
        assert abs(features["percent_transactions_same_amount"] - 0.5) < 1e-6  # 3 out of 6
        assert features["subscription_tier"] == "Standard"  # Netflix Standard tier
        assert features["is_valid_recurring_transaction"] == 1  # Valid recurring transaction


if __name__ == "__main__":
    unittest.main()
