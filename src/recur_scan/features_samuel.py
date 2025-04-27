from collections import Counter
from statistics import StatisticsError, mean, mode

import numpy as np

from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date


def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring because of the vendor name - check lowercase match."""
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
        "amazon prime",
        "apple music",
        "microsoft 365",
        "dropbox",
        "adobe creative cloud",
        "discord nitro",
        "zoom subscription",
        "patreon",
        "new york times",
        "wall street journal",
        "github copilot",
        "notion",
        "evernote",
        "expressvpn",
        "nordvpn",
        "youtube premium",
        "linkedin premium",
        "at&t",
        "afterpay",
        "amazon+",
        "walmart+",
        "amazonprime",
        "t-mobile",
        "duke energy",
        "adobe",
        "charter comm",
        "boostmobile",
        "verizon",
        "disney+",
    }
    return transaction.name.lower() in always_recurring_vendors


def get_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get frequency of transactions with same name."""
    return sum(1 for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip())


def get_amount_std_dev(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get standard deviation of amounts for similar transactions."""
    amounts = [t.amount for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()]
    return float(np.std(amounts, ddof=0)) if amounts else 0.0


def get_median_transaction_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get median amount for similar transactions."""
    amounts = [t.amount for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()]
    return float(np.median(amounts)) if amounts else 0.0


def get_is_weekend_transaction(transaction: Transaction) -> bool:
    """Check if transaction occurred on weekend."""
    return parse_date(transaction.date).weekday() >= 5


def get_transaction_day(transaction: Transaction) -> int:
    """Get day of month for transaction."""
    return parse_date(transaction.date).day


def get_transaction_weekday(transaction: Transaction) -> int:
    """Get weekday for transaction (0=Monday, 6=Sunday)."""
    return parse_date(transaction.date).weekday()


def get_transaction_month(transaction: Transaction) -> int:
    """Get month for transaction."""
    return parse_date(transaction.date).month


def get_transaction_year(transaction: Transaction) -> int:
    """Get year for transaction."""
    return parse_date(transaction.date).year


def get_is_first_half_month(transaction: Transaction) -> bool:
    """Check if transaction occurred in first half of month."""
    return parse_date(transaction.date).day <= 15


def get_is_month_end(transaction: Transaction) -> bool:
    """Check if transaction occurred at month end."""
    day = parse_date(transaction.date).day
    return day >= 28


def get_amount_above_mean(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if amount is above mean of all transactions."""
    avg = mean([t.amount for t in all_transactions])
    return transaction.amount > avg


def get_amount_equal_previous(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if amount equals previous transaction with same name."""
    relevant = [t for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()]
    relevant.sort(key=lambda t: parse_date(t.date))
    for idx, t in enumerate(relevant):
        if t == transaction and idx > 0:
            return transaction.amount == relevant[idx - 1].amount
    return False


def get_name_token_count(transaction: Transaction) -> int:
    """Get count of words in transaction name."""
    return len(transaction.name.split())


def get_has_digits_in_name(transaction: Transaction) -> bool:
    """Check if transaction name contains digits."""
    return any(char.isdigit() for char in transaction.name)


def get_average_days_between_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate average days between similar transactions."""
    dates = sorted([
        parse_date(t.date) for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()
    ])
    if len(dates) < 2:
        return 0.0
    gaps = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    return float(mean(gaps)) if gaps else 0.0


def get_transaction_count_last_90_days(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Count similar transactions in last 90 days."""
    txn_date = parse_date(transaction.date)
    return sum(
        1
        for t in all_transactions
        if t.name.lower().strip() == transaction.name.lower().strip()
        and 0 <= (txn_date - parse_date(t.date)).days <= 90
    )


def get_is_last_day_of_week(transaction: Transaction) -> bool:
    """Check if transaction occurred on Sunday."""
    return parse_date(transaction.date).weekday() == 6


def get_amount_round(transaction: Transaction) -> bool:
    """Check if amount is a round number."""
    return transaction.amount == round(transaction.amount)


def get_amount_decimal_places(transaction: Transaction) -> int:
    """Get number of decimal places in amount."""
    return len(str(transaction.amount).split(".")[-1]) if "." in str(transaction.amount) else 0


def get_contains_subscription_keywords(transaction: Transaction) -> bool:
    """Check if name contains subscription keywords."""
    keywords = {"subscription", "subscr", "renewal", "monthly", "yearly", "annual", "billed"}
    name = transaction.name.lower()
    return any(kw in name for kw in keywords)


def get_is_fixed_amount(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if amount is always the same for similar transactions."""
    amounts = [t.amount for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()]
    return len(set(amounts)) == 1 if amounts else False


def get_name_length(transaction: Transaction) -> int:
    """Get length of transaction name."""
    return len(transaction.name)


def get_most_common_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get most common amount for similar transactions."""
    amounts = [t.amount for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()]
    return mode(amounts) if amounts else 0.0


def get_amount_difference_from_mode(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get absolute difference from mode amount."""
    try:
        return abs(transaction.amount - get_most_common_amount(transaction, all_transactions))
    except (StatisticsError, ValueError):
        return 0.0


def get_transaction_date_is_first(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if this is the first transaction with this name."""
    dates = sorted([
        parse_date(t.date) for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()
    ])
    return parse_date(transaction.date) == dates[0] if dates else False


def get_transaction_date_is_last(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """Check if this is the last transaction with this name."""
    dates = sorted([
        parse_date(t.date) for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()
    ])
    return parse_date(transaction.date) == dates[-1] if dates else False


def get_transaction_name_word_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get frequency of words in transaction name across all transactions."""
    words = [word.lower() for t in all_transactions for word in t.name.split()]
    word_count = Counter(words)
    txn_words = transaction.name.split()
    return sum(word_count[word.lower()] for word in txn_words) / len(words) if words else 0.0


def get_transaction_amount_percentile(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get percentile of transaction amount compared to all transactions."""
    amounts = sorted([t.amount for t in all_transactions])
    if not amounts:
        return 0.0
    less_than = sum(1 for amt in amounts if amt < transaction.amount)
    return less_than / len(amounts)


def get_transaction_name_is_upper(transaction: Transaction) -> bool:
    """Check if name is all uppercase."""
    return transaction.name.isupper()


def get_transaction_name_is_title_case(transaction: Transaction) -> bool:
    """Check if name is title case."""
    return transaction.name.istitle()


def get_days_since_last_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get days since last transaction with same name."""
    dates = sorted([
        parse_date(t.date) for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()
    ])
    txn_date = parse_date(transaction.date)
    idx = dates.index(txn_date) if txn_date in dates else -1
    return (txn_date - dates[idx - 1]).days if idx > 0 else -1


def get_days_until_next_transaction(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get days until next transaction with same name."""
    dates = sorted([
        parse_date(t.date) for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()
    ])
    txn_date = parse_date(transaction.date)
    idx = dates.index(txn_date) if txn_date in dates else -1
    return (dates[idx + 1] - txn_date).days if 0 <= idx < len(dates) - 1 else -1


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int | bool | float]:
    """Get all new features for the transaction."""
    return {
        "transaction_day": get_transaction_day(transaction),
        "transaction_weekday": get_transaction_weekday(transaction),
        "transaction_month": get_transaction_month(transaction),
        "transaction_year": get_transaction_year(transaction),
        "is_first_half_month": get_is_first_half_month(transaction),
        "is_month_end": get_is_month_end(transaction),
        "amount_above_mean": get_amount_above_mean(transaction, all_transactions),
        "amount_equal_previous": get_amount_equal_previous(transaction, all_transactions),
        "name_token_count": get_name_token_count(transaction),
        "has_digits_in_name": get_has_digits_in_name(transaction),
        "average_days_between_transactions": get_average_days_between_transactions(transaction, all_transactions),
        "transaction_count_last_90_days": get_transaction_count_last_90_days(transaction, all_transactions),
        "is_last_day_of_week": get_is_last_day_of_week(transaction),
        "amount_round": get_amount_round(transaction),
        "amount_decimal_places": get_amount_decimal_places(transaction),
        "contains_subscription_keywords": get_contains_subscription_keywords(transaction),
        "is_fixed_amount": get_is_fixed_amount(transaction, all_transactions),
        "name_length": get_name_length(transaction),
        "most_common_amount": get_most_common_amount(transaction, all_transactions),
        "amount_difference_from_mode": get_amount_difference_from_mode(transaction, all_transactions),
        "transaction_date_is_first": get_transaction_date_is_first(transaction, all_transactions),
        "transaction_date_is_last": get_transaction_date_is_last(transaction, all_transactions),
        "transaction_name_word_frequency": get_transaction_name_word_frequency(transaction, all_transactions),
        "transaction_amount_percentile": get_transaction_amount_percentile(transaction, all_transactions),
        "transaction_name_is_upper": get_transaction_name_is_upper(transaction),
        "transaction_name_is_title_case": get_transaction_name_is_title_case(transaction),
        "days_since_last_transaction": get_days_since_last_transaction(transaction, all_transactions),
        "days_until_next_transaction": get_days_until_next_transaction(transaction, all_transactions),
    }
