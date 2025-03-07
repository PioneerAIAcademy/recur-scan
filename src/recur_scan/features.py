from collections import Counter, defaultdict

from recur_scan.transactions import Transaction


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions)


def get_average_transaction_amount(all_transactions: list[Transaction]) -> float:
    """Get the average amount of all transactions"""
    if not all_transactions:
        return 0.0
    total_amount = sum(t.amount for t in all_transactions)
    return total_amount / len(all_transactions)


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


def get_most_frequent_names(all_transactions: list[Transaction]) -> list[str]:
    """Get the most frequent names in the recurring transactions"""
    if not all_transactions:
        return []

    # Group transactions by user_id and name
    grouped_transactions = defaultdict(list)
    for transaction in all_transactions:
        grouped_transactions[(transaction.user_id, transaction.name)].append(transaction)

    recurring_names = []
    for (_user_id, name), transactions in grouped_transactions.items():
        # Check if there are multiple transactions with the same amount
        amount_counter = Counter(t.amount for t in transactions)
        if any(count > 1 for count in amount_counter.values()):
            recurring_names.append(name)

    return recurring_names


def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "average_transaction_amount": get_average_transaction_amount(all_transactions),
        "max_transaction_amount": get_max_transaction_amount(all_transactions),
        "min_transaction_amount": get_min_transaction_amount(all_transactions),
        "most_frequent_names": len(get_most_frequent_names(all_transactions)),
    }
