from recur_scan.transactions import Transaction
from recur_scan.utils import get_day


# feature/add-xbox-and-recur-companies-feature
def is_microsoft_xbox_same_or_near_day(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the transaction is for 'Microsoft Xbox' and occurs on the same day of the month
    or within 2 days before or after the previous transaction date.
    """
    if "microsoft xbox" not in transaction.name.lower():
        return False

    transaction_day = get_day(transaction.date)
    for t in all_transactions:
        if "microsoft xbox" in t.name.lower():
            previous_day = get_day(t.date)
            if abs(transaction_day - previous_day) <= 2:
                return True

    return False
