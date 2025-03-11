import datetime
import itertools
import statistics

from recur_scan.transactions import Transaction


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return sum(1 for t in all_transactions if t.amount == transaction.amount)


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
        "youtube",
        "netflix",
        "spotify",
        "hulu",
        "la fitness",
        "cleo ai",
        "atlas",
        "google storage",
        "youtube premium",
        "afterpay",
        "amazon+",
        "walmart+",
        "amazonprime",
        "duke energy",
        "adobe",
        "charter comm",
        "boostmobile",
    }
    merchant_name = transaction.name.lower()
    return any(keyword in merchant_name for keyword in recurring_keywords)


def get_n_transactions_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions with the same merchant and amount"""
    return sum(1 for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount)


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


def get_recurring_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> str:
    """Determine if the transaction is recurring daily, weekly, or monthly"""
    same_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount],
        key=lambda x: x.date,
    )
    if len(same_transactions) < 2:
        return "none"

    intervals = [
        (
            datetime.datetime.strptime(t2.date, "%Y-%m-%d").date()
            - datetime.datetime.strptime(t1.date, "%Y-%m-%d").date()
        ).days
        for t1, t2 in itertools.pairwise(same_transactions)
    ]

    if not intervals:
        return "none"

    avg_interval = sum(intervals) / len(intervals)

    if avg_interval <= 1:
        return "daily"
    elif avg_interval <= 7:
        return "weekly"
    elif avg_interval <= 30:
        return "monthly"
    else:
        return "none"


def get_is_always_recurring(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Determine if the transaction is always recurring"""
    same_transactions = [t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount]
    return len(same_transactions) > 1


def get_is_insurance(transaction: Transaction) -> bool:
    """Determine if the transaction is related to insurance"""
    insurance_keywords = {"insurance", "ins", "policy"}
    merchant_name = transaction.name.lower()
    return any(keyword in merchant_name for keyword in insurance_keywords)


def get_is_utility(transaction: Transaction) -> bool:
    """Determine if the transaction is related to utilities"""
    utility_keywords = {"utility", "utilities", "electric", "water", "gas", "power", "energy"}
    merchant_name = transaction.name.lower()
    return any(keyword in merchant_name for keyword in utility_keywords)


def get_is_phone(transaction: Transaction) -> bool:
    """Determine if the transaction is related to phone services"""
    phone_keywords = {"phone", "mobile", "cellular", "wireless", "telecom"}
    merchant_name = transaction.name.lower()
    return any(keyword in merchant_name for keyword in phone_keywords)


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int | bool | str]:
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
        "recurring_frequency": get_recurring_frequency(transaction, all_transactions),
        "is_always_recurring": get_is_always_recurring(transaction, all_transactions),
        "is_insurance": get_is_insurance(transaction),
        "is_utility": get_is_utility(transaction),
        "is_phone": get_is_phone(transaction),
    }
