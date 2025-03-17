from collections import Counter, defaultdict
from datetime import datetime, timedelta
from itertools import pairwise

from recur_scan.transactions import Transaction


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    return sum(1 for t in all_transactions if t.amount == transaction.amount)


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    return (
        get_n_transactions_same_amount(transaction, all_transactions) / len(all_transactions)
        if all_transactions
        else 0.0
    )


def get_average_transaction_amount(all_transactions: list[Transaction]) -> float:
    return sum(t.amount for t in all_transactions) / len(all_transactions) if all_transactions else 0.0


def get_max_transaction_amount(all_transactions: list[Transaction]) -> float:
    return max((t.amount for t in all_transactions), default=0.0)


def get_min_transaction_amount(all_transactions: list[Transaction]) -> float:
    return min((t.amount for t in all_transactions), default=0.0)


def get_most_frequent_names(all_transactions: list[Transaction]) -> list[str]:
    grouped_transactions = defaultdict(list)
    for transaction in all_transactions:
        grouped_transactions[(transaction.user_id, transaction.name)].append(transaction)
    return [
        name
        for (_user_id, name), transactions in grouped_transactions.items()
        if any(count > 1 for count in Counter(t.amount for t in transactions).values())
    ]


def is_recurring(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    grouped_transactions = defaultdict(list)
    for t in all_transactions:
        grouped_transactions[(t.user_id, t.name)].append(t)
    for (_user_id, name), transactions in grouped_transactions.items():
        if transaction.name == name:
            transactions.sort(key=lambda x: datetime.strptime(x.date, "%Y-%m-%d"))
            for i in range(1, len(transactions)):
                date_diff = datetime.strptime(transactions[i].date, "%Y-%m-%d") - datetime.strptime(
                    transactions[i - 1].date, "%Y-%m-%d"
                )
                if (
                    transactions[i].amount == transactions[i - 1].amount
                    or transactions[i].amount == 1
                    or str(transactions[i].amount).endswith(".99")
                ) and (
                    (timedelta(days=6) <= date_diff <= timedelta(days=8))
                    or (timedelta(days=13) <= date_diff <= timedelta(days=15))
                    or (timedelta(days=28) <= date_diff <= timedelta(days=31))
                    or (timedelta(days=58) <= date_diff <= timedelta(days=62))
                ):
                    return True
    return False


# def amount_ends_in_99(transaction: Transaction) -> bool:
#     return round(transaction.amount % 1, 2) == 0.99


# def amount_ends_in_00(transaction: Transaction) -> bool:
#     return round(transaction.amount % 1, 2) == 0.00


def is_recurring_merchant(transaction: Transaction) -> bool:
    recurring_keywords = {
        "at&t",
        "google play",
        "verizon",
        "vz wireless",
        "t-mobile",
        "apple",
        "disney+",
        "amazon prime",
    }
    return any(keyword in transaction.name.lower() for keyword in recurring_keywords)


# def get_n_transactions_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
#     return sum(1 for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount)


# def get_percent_transactions_same_merchant_amount(
#     transaction: Transaction, all_transactions: list[Transaction]
# ) -> float:
#     return (
#         get_n_transactions_same_merchant_amount(transaction, all_transactions) / len(all_transactions)
#         if all_transactions
#         else 0.0
#     )


def get_avg_days_between_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    same_transactions = sorted(
        (t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount),
        key=lambda x: x.date,
    )
    if len(same_transactions) < 2:
        return 0.0
    intervals = [
        (datetime.strptime(t2.date, "%Y-%m-%d").date() - datetime.strptime(t1.date, "%Y-%m-%d").date()).days
        for t1, t2 in pairwise(same_transactions)
    ]
    return sum(intervals) / len(intervals) if intervals else 0.0


# def get_stddev_days_between_same_merchant_amount(
#     transaction: Transaction, all_transactions: list[Transaction]
# ) -> float:
#     same_transactions = sorted(
#         (t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount),
#         key=lambda x: x.date,
#     )
#     if len(same_transactions) < 2:
#         return 0.0
#     intervals = [
#         (datetime.strptime(t2.date, "%Y-%m-%d").date() - datetime.strptime(t1.date, "%Y-%m-%d").date()).days
#         for t1, t2 in pairwise(same_transactions)
#     ]
#     try:
#         return statistics.stdev(intervals)
#     except statistics.StatisticsError:
#         return 0.0


# def get_days_since_last_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
#     same_transactions = [
#         t
#         for t in all_transactions
#         if t.name == transaction.name and t.amount == transaction.amount and t.date < transaction.date
#     ]
#     if not same_transactions:
#         return 0
#     last_date = max(datetime.strptime(t.date, "%Y-%m-%d").date() for t in same_transactions)
#     return (datetime.strptime(transaction.date, "%Y-%m-%d").date() - last_date).days


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int | bool]:
    return {
        "amount": transaction.amount,
        # "amount_ends_in_99": amount_ends_in_99(transaction),
        # "amount_ends_in_00": amount_ends_in_00(transaction),
        "is_recurring_merchant": is_recurring_merchant(transaction),
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        # "n_transactions_same_merchant_amount": get_n_transactions_same_merchant_amount(transaction, all_transactions),
        # "percent_transactions_same_merchant_amount": get_percent_transactions_same_merchant_amount(
        #     transaction, all_transactions
        # ),
        "avg_days_between_same_merchant_amount": get_avg_days_between_same_merchant_amount(
            transaction, all_transactions
        ),
        # "stddev_days_between_same_merchant_amount": get_stddev_days_between_same_merchant_amount(
        #     transaction, all_transactions
        # ),
        # "days_since_last_same_merchant_amount": get_days_since_last_same_merchant_amount(
        #     transaction, all_transactions),
        "average_transaction_amount": get_average_transaction_amount(all_transactions),
        "max_transaction_amount": get_max_transaction_amount(all_transactions),
        "min_transaction_amount": get_min_transaction_amount(all_transactions),
        "most_frequent_names": len(get_most_frequent_names(all_transactions)),
        "is_recurring": is_recurring(transaction, all_transactions),
    }
