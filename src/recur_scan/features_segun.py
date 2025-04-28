from datetime import datetime
from statistics import median, stdev

from recur_scan.transactions import Transaction


def get_total_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the total amount of all transactions"""
    return sum(t.amount for t in all_transactions)


def get_average_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the average amount of all transactions"""
    if not all_transactions:
        return 0.0
    return sum(t.amount for t in all_transactions) / len(all_transactions)


def get_max_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the maximum transaction amount"""
    if not all_transactions:
        return 0.0
    return max(t.amount for t in all_transactions)


def get_min_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the minimum transaction amount"""
    if not all_transactions:
        return 0.0
    return min(t.amount for t in all_transactions)


def get_transaction_count(all_transactions: list[Transaction]) -> int:
    """Get the total number of transactions"""
    return len(all_transactions)


def get_transaction_amount_std(all_transactions: list[Transaction]) -> float:
    """Get the standard deviation of transaction amounts"""
    if len(all_transactions) < 2:  # Standard deviation requires at least two data points
        return 0.0
    return stdev(t.amount for t in all_transactions)


def get_transaction_amount_median(all_transactions: list[Transaction]) -> float:
    """Get the median transaction amount"""
    if not all_transactions:
        return 0.0
    return median(t.amount for t in all_transactions)


def get_transaction_amount_range(all_transactions: list[Transaction]) -> float:
    """Get the range of transaction amounts (max - min)"""
    if not all_transactions:
        return 0.0
    return max(t.amount for t in all_transactions) - min(t.amount for t in all_transactions)


def get_unique_transaction_amount_count(all_transactions: list[Transaction]) -> int:
    """Get the number of unique transaction amounts"""
    return len({t.amount for t in all_transactions})


def get_transaction_amount_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the frequency of the transaction amount in all transactions"""
    return sum(1 for t in all_transactions if t.amount == transaction.amount)


def get_transaction_day_of_week(transaction: Transaction) -> int:
    """Get the day of the week for the transaction (0=Monday, 6=Sunday)"""
    return datetime.strptime(transaction.date, "%Y-%m-%d").weekday()


def get_transaction_time_of_day(transaction: Transaction) -> int:
    """Get the time of day for the transaction (morning, afternoon, evening, night)"""
    try:
        hour = datetime.strptime(transaction.date, "%Y-%m-%d %H:%M:%S").hour
    except ValueError:
        return -1  # Default value for missing time

    if 6 <= hour < 12:
        return 1
    elif 12 <= hour < 18:
        return 2
    elif 18 <= hour < 24:
        return 3
    else:
        return 4


def get_average_transaction_interval(all_transactions: list[Transaction]) -> float:
    """Get the average time interval (in days) between transactions"""
    if len(all_transactions) < 2:
        return 0.0
    intervals = [
        (
            datetime.strptime(all_transactions[i].date, "%Y-%m-%d")
            - datetime.strptime(all_transactions[i - 1].date, "%Y-%m-%d")
        ).days
        for i in range(1, len(all_transactions))
    ]
    return sum(intervals) / len(intervals)


# segun new features


def get_transaction_interval_std(all_transactions: list[Transaction]) -> float:
    """Get the standard deviation of the intervals (in days) between transactions."""
    if len(all_transactions) < 2:
        return 0.0
    intervals = [
        (
            datetime.strptime(all_transactions[i].date, "%Y-%m-%d")
            - datetime.strptime(all_transactions[i - 1].date, "%Y-%m-%d")
        ).days
        for i in range(1, len(all_transactions))
    ]
    if len(intervals) < 2:  # Standard deviation requires at least two data points
        return 0.0
    return stdev(intervals)


def get_transaction_amount_percentage(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of the transaction amount relative to the total transaction amounts."""
    total_amount = sum(t.amount for t in all_transactions)
    if total_amount == 0:
        return 0.0
    return (transaction.amount / total_amount) * 100


def get_transaction_recency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of days since the last transaction."""
    transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    previous_dates = [
        datetime.strptime(t.date, "%Y-%m-%d")
        for t in all_transactions
        if datetime.strptime(t.date, "%Y-%m-%d") < transaction_date
    ]
    if not previous_dates:
        return 0
    last_transaction_date = max(previous_dates)
    return (transaction_date - last_transaction_date).days


def get_transaction_frequency_per_month(all_transactions: list[Transaction]) -> float:
    """Get the average number of transactions per month."""
    if not all_transactions:
        return 0.0
    transaction_dates = [datetime.strptime(t.date, "%Y-%m-%d") for t in all_transactions]
    months = {(date.year, date.month) for date in transaction_dates}
    return len(all_transactions) / len(months)


def get_transaction_is_weekend(transaction: Transaction) -> bool:
    """Check if the transaction is on a weekend."""
    transaction_date = datetime.strptime(transaction.date, "%Y-%m-%d")
    return transaction_date.weekday() >= 5  # 5 = Saturday, 6 = Sunday


def amazon_prime_day_proximity(transaction: Transaction) -> int:
    """Calculate how close the transaction date is to the 17th of the month."""
    transaction_day = int(transaction.date.split("-")[2])
    return abs(transaction_day - 17)


def transaction_day_of_month(transaction: Transaction) -> int:
    """Get the day of the month the transaction occurred."""
    return int(transaction.date.split("-")[2])


def is_recurring_day(all_transactions: list[Transaction]) -> bool:
    """Check if a recurring day pattern exists (e.g., 7-day or 30-day intervals)."""
    days = [
        (
            datetime.strptime(all_transactions[i].date, "%Y-%m-%d")
            - datetime.strptime(all_transactions[i - 1].date, "%Y-%m-%d")
        ).days
        for i in range(1, len(all_transactions))
    ]
    return any(abs(day - 7) <= 1 or abs(day - 30) <= 1 for day in days)


def transaction_amount_similarity(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Measure how similar the transaction amount is to previous transactions."""
    amounts = [t.amount for t in all_transactions if t != transaction]
    if not amounts:
        return 0.0
    return min(abs(transaction.amount - amount) for amount in amounts)


# (Segun F2)
def markovian_probability(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """
    Calculate the Markovian probability of the transaction occurring based on the day of the week.
    Uses a first-order Markov chain to model transitions between days of the week.
    """
    if len(all_transactions) < 2:
        return 0.0

    # Get the day of the week for each transaction (0=Monday, 6=Sunday)
    days_of_week = [datetime.strptime(t.date, "%Y-%m-%d").weekday() for t in all_transactions]
    current_day = datetime.strptime(transaction.date, "%Y-%m-%d").weekday()

    # Build a transition matrix (7x7 for days of the week)
    transition_counts = [[0] * 7 for _ in range(7)]
    for i in range(len(days_of_week) - 1):
        prev_day = days_of_week[i]
        next_day = days_of_week[i + 1]
        transition_counts[prev_day][next_day] += 1

    # Calculate transition probabilities
    transition_probs = [[0.0] * 7 for _ in range(7)]
    for i in range(7):
        total_transitions = sum(transition_counts[i])
        if total_transitions > 0:
            for j in range(7):
                transition_probs[i][j] = transition_counts[i][j] / total_transitions
        else:
            # If no transitions, assume uniform probability
            for j in range(7):
                transition_probs[i][j] = 1.0 / 7

    # Get the previous transaction's day of the week
    previous_dates = [
        datetime.strptime(t.date, "%Y-%m-%d")
        for t in all_transactions
        if datetime.strptime(t.date, "%Y-%m-%d") < datetime.strptime(transaction.date, "%Y-%m-%d")
    ]
    if not previous_dates:
        return 0.0
    last_transaction_date = max(previous_dates)
    last_day = last_transaction_date.weekday()

    # Return the probability of transitioning to the current day
    return transition_probs[last_day][current_day]


def calculate_streak(all_transactions: list[Transaction]) -> int:
    """
    Calculate the longest streak of consecutive days with transactions.
    """
    if not all_transactions:
        return 0

    # Sort transactions by date
    sorted_transactions = sorted(all_transactions, key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))
    dates = [datetime.strptime(t.date, "%Y-%m-%d") for t in sorted_transactions]

    if not dates:
        return 0

    current_streak = 1
    max_streak = 1

    for i in range(1, len(dates)):
        # Check if the current date is consecutive to the previous date
        if (dates[i] - dates[i - 1]).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1

    return max_streak


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int | bool | float]:
    """Get the new features for the transaction."""

    # NOTE: Do NOT add features that are already in the original features.py file.
    # NOTE: Each feature should be on a separate line. Do not use **dict shorthand.
    return {
        "transaction_interval_std": get_transaction_interval_std(all_transactions),
        "transaction_amount_percentage": get_transaction_amount_percentage(transaction, all_transactions),
        "transaction_recency": get_transaction_recency(transaction, all_transactions),
        "transaction_frequency_per_month": get_transaction_frequency_per_month(all_transactions),
        "transaction_is_weekend": get_transaction_is_weekend(transaction),
        "amazon_prime_day_proximity": amazon_prime_day_proximity(transaction),
        "transaction_day_of_month": transaction_day_of_month(transaction),
        "is_recurring_day": is_recurring_day(all_transactions),
        "transaction_amount_similarity": transaction_amount_similarity(transaction, all_transactions),
        "markovian_probability": markovian_probability(transaction, all_transactions),
        "transaction_streak": calculate_streak(all_transactions),
    }
