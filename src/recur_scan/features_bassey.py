import re
from collections import defaultdict
from datetime import datetime

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


# The following functions are the new features added by Bassey


# new features are below


def get_is_recurring_apple_bassey(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the transaction is recurring for Apple.
    A transaction is considered recurring if it occurs not more than 2 times in a month
    and repeats for at least 2 months.
    """
    # Group transactions by month and year
    monthly_counts: dict[tuple[int, int], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for t in all_transactions:
        t_date = datetime.strptime(t.date, "%Y-%m-%d")
        _month_year = (t_date.year, t_date.month)
        if "apple" in t.name.lower():
            monthly_counts[_month_year][t.name] += 1

    # Check if the transaction meets the criteria
    recurring_months = 0
    for _month_year, counts in monthly_counts.items():
        if 1 <= counts.get(transaction.name, 0) <= 2:  # Occurs not more than 2 times
            recurring_months += 1

    return recurring_months >= 2  # Repeats for at least 2 months


def get_is_weekly_recurring_apple_bassey(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the transaction is recurring for Apple on a weekly basis.
    A transaction is considered recurring if it occurs at most once every 7 days
    for a particular month.
    """
    # Filter transactions related to Apple
    apple_transactions = [t for t in all_transactions if "apple" in t.name.lower()]

    # Group transactions by month and year
    monthly_transactions: dict[tuple[int, int], list[datetime]] = defaultdict(list)
    for t in apple_transactions:
        t_date = datetime.strptime(t.date, "%Y-%m-%d")
        month_year = (t_date.year, t_date.month)
        monthly_transactions[month_year].append(t_date)

    # Check if the transaction meets the criteria for the month of the given transaction
    t_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    month_year = (t_date.year, t_date.month)
    if month_year not in monthly_transactions:
        return False

    # Sort the transaction dates for the month
    dates = sorted(monthly_transactions[month_year])

    # Check if the transactions are spaced at least 7 days apart using `all()`
    return all((dates[i] - dates[i - 1]).days >= 7 for i in range(1, len(dates)))


def get_is_high_value_transaction_bassey(transaction: Transaction, threshold: float = 100.0) -> bool:
    """Check if the transaction amount is considered high value."""
    return transaction.amount > threshold


def get_is_frequent_merchant_bassey(
    transaction: Transaction, all_transactions: list[Transaction], frequency_threshold: int = 5
) -> bool:
    """Check if the merchant is a frequent one for the user."""
    merchant_counts: dict[str, int] = defaultdict(int)  # Add type annotation for merchant_counts
    for t in all_transactions:
        merchant_counts[t.name] += 1
    return merchant_counts[transaction.name] >= frequency_threshold  # Ensure the return type is bool


def get_is_weekend_transaction_bassey(transaction: Transaction) -> bool:
    """Check if the transaction occurred on a weekend."""
    t_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    return t_date.weekday() >= 5  # Saturday (5) or Sunday (6)


def get_monthly_spending_average_bassey(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the average spending for the user in the month of the transaction."""
    t_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    monthly_transactions = [
        t.amount
        for t in all_transactions
        if datetime.strptime(t.date, "%Y-%m-%d").year == t_date.year
        and datetime.strptime(t.date, "%Y-%m-%d").month == t_date.month
    ]
    return sum(monthly_transactions) / len(monthly_transactions) if monthly_transactions else 0.0


def get_is_merchant_recurring_bassey(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if the merchant appears in multiple months for the user."""
    merchant_months = set()
    for t in all_transactions:
        if t.name == transaction.name:
            t_date = datetime.strptime(t.date, "%Y-%m-%d")
            merchant_months.add((t_date.year, t_date.month))
    return len(merchant_months) > 1


def get_days_since_last_transaction_bassey(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Calculate the number of days since the user's last transaction."""
    t_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    previous_dates = [datetime.strptime(t.date, "%Y-%m-%d") for t in all_transactions if t.date < transaction.date]
    if not previous_dates:
        return -1  # No previous transactions
    last_date = max(previous_dates)
    return (t_date - last_date).days


def get_is_same_day_multiple_transactions_bassey(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if there are multiple transactions on the same day."""
    same_day_transactions = [t for t in all_transactions if t.date == transaction.date]
    return len(same_day_transactions) > 1


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int | bool | float]:
    """Get the new features for the transaction."""

    return {
        "is_recurring_apple": get_is_recurring_apple_bassey(transaction, all_transactions),
        "is_weekly_recurring_apple": get_is_weekly_recurring_apple_bassey(transaction, all_transactions),
        "is_high_value_transaction": get_is_high_value_transaction_bassey(transaction),
        "is_frequent_merchant": get_is_frequent_merchant_bassey(transaction, all_transactions),
        "is_weekend_transaction": get_is_weekend_transaction_bassey(transaction),
        "monthly_spending_average": get_monthly_spending_average_bassey(transaction, all_transactions),
        "is_merchant_recurring": get_is_merchant_recurring_bassey(transaction, all_transactions),
        "days_since_last_transaction": get_days_since_last_transaction_bassey(transaction, all_transactions),
        "is_same_day_multiple_transactions": get_is_same_day_multiple_transactions_bassey(
            transaction, all_transactions
        ),
    }
