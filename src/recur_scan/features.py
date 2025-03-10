import datetime
import itertools
import statistics

from recur_scan.transactions import Transaction


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    return get_n_transactions_same_amount(transaction, all_transactions) / len(all_transactions)


def amount_ends_in_99(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in .99"""
    return round(transaction.amount % 1, 2) == 0.99


def amount_ends_in_00(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in .00"""
    return round(transaction.amount % 1, 2) == 0.00


def is_recurring_merchant(transaction: Transaction) -> bool:
    """Check if the transaction's merchant is a known recurring company"""
    recurring_keywords = {
        "at&t",
        "google play",
        "verizon",
        "vz wireless",
        "vzw",
        "t-mobile",
        "apple",
        "disney+",
        "disney mobile",
        "hbo max",
        "amazon prime",
    }
    # Changed from merchant to name
    merchant_name = transaction.name.lower()
    return any(keyword in merchant_name for keyword in recurring_keywords)


def get_n_transactions_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions with the same merchant and amount"""
    # Changed from merchant to name
    return len([t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount])


def get_percent_transactions_same_merchant_amount(
    transaction: Transaction, all_transactions: list[Transaction]
) -> float:
    """Get the percentage of transactions with the same merchant and amount"""
    if not all_transactions:
        return 0.0
    n_same = get_n_transactions_same_merchant_amount(transaction, all_transactions)
    return n_same / len(all_transactions)


def get_avg_days_between_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the average days between transactions with the same merchant and amount"""
    # Changed from merchant to name
    same_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount],
        key=lambda x: x.date,
    )
    if len(same_transactions) < 2:
        return 0.0
    intervals = [
        (
            datetime.datetime.strptime(t2.date, "%Y-%m-%d").date()
            - datetime.datetime.strptime(t1.date, "%Y-%m-%d").date()
        ).days
        for t1, t2 in itertools.pairwise(same_transactions)
    ]
    return sum(intervals) / len(intervals) if intervals else 0.0


def get_stddev_days_between_same_merchant_amount(
    transaction: Transaction, all_transactions: list[Transaction]
) -> float:
    """Calculate the standard deviation of days between transactions with the same merchant and amount"""
    # Changed from merchant to name
    same_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount],
        key=lambda x: x.date,
    )
    if len(same_transactions) < 2:
        return 0.0
    intervals = [
        (
            datetime.datetime.strptime(t2.date, "%Y-%m-%d").date()
            - datetime.datetime.strptime(t1.date, "%Y-%m-%d").date()
        ).days
        for t1, t2 in itertools.pairwise(same_transactions)
    ]
    try:
        return statistics.stdev(intervals)
    except statistics.StatisticsError:
        return 0.0


def get_days_since_last_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of days since the last transaction with the same merchant and amount"""
    # Changed from merchant to name
    same_transactions = [
        t
        for t in all_transactions
        if t.name == transaction.name and t.amount == transaction.amount and t.date < transaction.date
    ]
    if not same_transactions:
        return 0
    last_date = max(datetime.datetime.strptime(t.date, "%Y-%m-%d").date() for t in same_transactions)
    transaction_date = datetime.datetime.strptime(transaction.date, "%Y-%m-%d").date()
    return (transaction_date - last_date).days


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int | bool]:
    """Extract features for a given transaction"""
    return {
        "amount": transaction.amount,
        "amount_ends_in_99": amount_ends_in_99(transaction),
        "amount_ends_in_00": amount_ends_in_00(transaction),
        "is_recurring_merchant": is_recurring_merchant(transaction),
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "n_transactions_same_merchant_amount": get_n_transactions_same_merchant_amount(transaction, all_transactions),
        "percent_transactions_same_merchant_amount": get_percent_transactions_same_merchant_amount(
            transaction, all_transactions
        ),
        "avg_days_between_same_merchant_amount": get_avg_days_between_same_merchant_amount(
            transaction, all_transactions
        ),
        "stddev_days_between_same_merchant_amount": get_stddev_days_between_same_merchant_amount(
            transaction, all_transactions
        ),
        "days_since_last_same_merchant_amount": get_days_since_last_same_merchant_amount(transaction, all_transactions),
    }


# Example Usage
if __name__ == "__main__":
    transactions = [
        Transaction(id=1, user_id="1", amount=50.99, name="AT&T", date="2023-01-01"),
        Transaction(id=2, user_id="1", amount=30.00, name="Google Play", date="2023-01-15"),
        Transaction(id=3, user_id="1", amount=50.99, name="AT&T", date="2023-02-01"),
        Transaction(id=4, user_id="1", amount=20.00, name="Amazon Prime", date="2023-02-15"),
        Transaction(id=5, user_id="1", amount=50.99, name="AT&T", date="2023-03-01"),
        Transaction(id=6, user_id="1", amount=9.99, name="Disney+", date="2023-03-15"),
    ]

    features = get_features(transactions[0], transactions)
    print(features)
# comment
