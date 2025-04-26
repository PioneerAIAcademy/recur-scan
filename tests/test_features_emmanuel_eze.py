from recur_scan.features_emmanuel_eze import (
    detect_sequence_patterns,
    get_is_recurring,
    get_recurring_transaction_confidence,
)
from recur_scan.transactions import Transaction


def test_get_recurring_transaction_confidence() -> None:
    """Test recurring transaction confidence score calculation."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-01-08"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-01-15"),
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-01-01"),
        Transaction(id=5, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
    ]

    # Test for a recurring transaction (Netflix)
    score = get_recurring_transaction_confidence(transactions[0], transactions)
    assert score > 0.5, f"Expected high confidence score for recurring transaction, got {score}"

    # Test for a transaction with no similar transactions
    non_recurring_transaction = Transaction(id=6, user_id="user1", name="Amazon", amount=50.00, date="2024-01-01")
    score = get_recurring_transaction_confidence(non_recurring_transaction, transactions)
    assert score < 0.5, f"Expected low confidence score for transaction with no similar transactions, got {score}"


def test_get_is_recurring() -> None:
    """Test the get_is_recurring function for identifying recurring transactions."""
    transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"),
        Transaction(id=4, user_id="user1", name="Spotify", amount=9.99, date="2024-01-01"),
        Transaction(id=5, user_id="user1", name="Amazon", amount=25.99, date="2024-01-15"),
    ]

    # Test recurring transaction (Netflix - monthly)
    is_recurring = get_is_recurring(transactions[0], transactions)
    assert is_recurring is True, "Netflix should be identified as recurring"

    # Test non-recurring transaction (Amazon - one-time purchase)
    is_recurring = get_is_recurring(transactions[4], transactions)
    assert is_recurring is False, "Amazon should not be identified as recurring"

    # Test with empty transaction list
    empty_transaction = Transaction(id=6, user_id="user1", name="Empty", amount=10.00, date="2024-01-01")
    is_recurring = get_is_recurring(empty_transaction, [])
    assert is_recurring is False, "Transaction with empty list should not be recurring"


def test_detect_sequence_patterns() -> None:
    """Test the detect_sequence_patterns function for identifying transaction patterns."""
    # Create base transactions for testing
    netflix_transactions = [
        Transaction(id=1, user_id="user1", name="Netflix", amount=15.99, date="2024-01-01"),
        Transaction(id=2, user_id="user1", name="Netflix", amount=15.99, date="2024-02-01"),
        Transaction(id=3, user_id="user1", name="Netflix", amount=15.99, date="2024-03-01"),
        Transaction(id=4, user_id="user1", name="Netflix", amount=15.99, date="2024-04-01"),
    ]

    # Test monthly pattern
    result = detect_sequence_patterns(netflix_transactions[0], netflix_transactions)
    assert result["sequence_pattern"] == 2, "Should detect monthly pattern (pattern code 2)"
    assert result["sequence_confidence"] > 0.8, (
        f"Expected high confidence for monthly pattern, got {result['sequence_confidence']}"
    )

    # Test weekly pattern
    weekly_transactions = [
        Transaction(id=5, user_id="user1", name="Gym", amount=10.00, date="2024-01-01"),
        Transaction(id=6, user_id="user1", name="Gym", amount=10.00, date="2024-01-08"),
        Transaction(id=7, user_id="user1", name="Gym", amount=10.00, date="2024-01-15"),
        Transaction(id=8, user_id="user1", name="Gym", amount=10.00, date="2024-01-22"),
    ]
    result = detect_sequence_patterns(weekly_transactions[0], weekly_transactions)
    assert result["sequence_pattern"] == 1, "Should detect weekly pattern (pattern code 1)"
    assert result["sequence_confidence"] > 0.8, (
        f"Expected high confidence for weekly pattern, got {result['sequence_confidence']}"
    )

    # Test yearly pattern
    yearly_transactions = [
        Transaction(id=9, user_id="user1", name="Insurance", amount=500.00, date="2022-01-01"),
        Transaction(id=10, user_id="user1", name="Insurance", amount=500.00, date="2023-01-01"),
        Transaction(id=11, user_id="user1", name="Insurance", amount=500.00, date="2024-01-01"),
    ]
    result = detect_sequence_patterns(yearly_transactions[0], yearly_transactions)
    assert result["sequence_pattern"] == 3, "Should detect yearly pattern (pattern code 3)"
    assert result["sequence_confidence"] > 0.8, (
        f"Expected high confidence for yearly pattern, got {result['sequence_confidence']}"
    )

    # Test with irregular transactions
    irregular_transactions = [
        Transaction(id=12, user_id="user1", name="Shopping", amount=50.00, date="2024-01-01"),
        Transaction(id=13, user_id="user1", name="Shopping", amount=50.00, date="2024-01-15"),
        Transaction(id=14, user_id="user1", name="Shopping", amount=50.00, date="2024-02-10"),
    ]
    result = detect_sequence_patterns(irregular_transactions[0], irregular_transactions)
    assert result["sequence_pattern"] == -1, "Should detect irregular pattern (pattern code -1)"
    assert result["sequence_confidence"] < 0.5, (
        f"Expected low confidence for irregular pattern, got {result['sequence_confidence']}"
    )

    # Test with insufficient data
    few_transactions = [
        Transaction(id=15, user_id="user1", name="Donation", amount=20.00, date="2024-01-01"),
        Transaction(id=16, user_id="user1", name="Donation", amount=20.00, date="2024-02-01"),
    ]
    result = detect_sequence_patterns(few_transactions[0], few_transactions)
    assert result["sequence_pattern"] == -1, "Should indicate insufficient data (pattern code -1)"
    assert result["sequence_confidence"] == 0.0, (
        f"Expected zero confidence for insufficient data, got {result['sequence_confidence']}"
    )

    # Test with empty transaction list
    empty_transaction = Transaction(id=17, user_id="user1", name="Empty", amount=10.00, date="2024-01-01")
    result = detect_sequence_patterns(empty_transaction, [])
    assert result["sequence_pattern"] == -1, "Should indicate insufficient data for empty list (pattern code -1)"
    assert result["sequence_confidence"] == 0.0, "Confidence should be 0 for empty list"

    # Test with zero amount transaction
    zero_transaction = Transaction(id=18, user_id="user1", name="Zero", amount=0.00, date="2024-01-01")
    result = detect_sequence_patterns(zero_transaction, [zero_transaction])
    assert result["sequence_pattern"] == -1, "Should handle zero amount transaction (pattern code -1)"
    assert result["sequence_confidence"] == 0.0, "Confidence should be 0 for zero amount transaction"
