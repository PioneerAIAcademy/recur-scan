import re

from recur_scan.transactions import Transaction


def get_is_subscription(transaction: Transaction) -> bool:
    """Check if the transaction is a subscription payment."""
    match = re.search(r"\b(subscription|monthly|recurring)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_streaming_service(transaction: Transaction) -> bool:
    """Check if the transaction is a streaming service payment."""
    streaming_services = {"netflix", "hulu", "spotify", "disney+"}
    return transaction.name.lower() in streaming_services


def get_is_gym_membership(transaction: Transaction) -> bool:
    """Check if the transaction is a gym membership payment."""
    match = re.search(r"\b(gym|fitness|membership|planet fitness)\b", transaction.name, re.IGNORECASE)
    return bool(match)
