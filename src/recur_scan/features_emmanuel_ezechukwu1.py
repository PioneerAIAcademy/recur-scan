import re
from typing import Any

from recur_scan.transactions import Transaction, group_transactions
from recur_scan.utils import parse_date


def get_is_always_recurring(transaction: Transaction) -> bool:
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
        "amazon prime",
        "disney+",
        "apple music",
        "xbox live",
        "playstation plus",
        "adobe",
        "microsoft 365",
        "audible",
        "dropbox",
        "zoom",
        "grammarly",
        "nordvpn",
        "expressvpn",
        "patreon",
        "onlyfans",
        "youtube premium",
        "apple tv",
        "hbo max",
        "paramount+",
        "peacock",
        "crunchyroll",
        "masterclass",
    }
    return transaction.name.lower() in always_recurring_vendors


def get_is_insurance(transaction: Transaction) -> bool:
    match = re.search(
        r"\b(insurance|insur|insuranc|geico|allstate|progressive|state farm|liberty mutual)\b",
        transaction.name,
        re.IGNORECASE,
    )
    return bool(match)


def get_is_utility(transaction: Transaction) -> bool:
    match = re.search(
        r"\b(utility|utilit|energy|water|gas|electric|comcast|xfinity|verizon fios|at&t u-verse|spectrum)\b",
        transaction.name,
        re.IGNORECASE,
    )
    return bool(match)


def get_is_phone(transaction: Transaction) -> bool:
    match = re.search(
        r"\b(at&t|t-mobile|verizon|sprint|boost|cricket|metro pcs|straight talk)\b", transaction.name, re.IGNORECASE
    )
    return bool(match)


def get_n_transactions_days_apart(
    transaction: Transaction, all_transactions: list[Transaction], n_days_apart: int, n_days_off: int
) -> int:
    n_txs = 0
    transaction_date = parse_date(transaction.date)
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    effective_days_off = max(n_days_off, 1) if n_days_off == 0 else n_days_off
    for t in user_transactions:
        t_date = parse_date(t.date)
        days_diff = abs((t_date - transaction_date).days)
        if n_days_apart - effective_days_off <= days_diff <= n_days_apart + effective_days_off:
            n_txs += 1
    return n_txs


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    return len([t for t in user_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    if not all_transactions:
        return 0.0
    n_same_amount = get_n_transactions_same_amount(transaction, all_transactions)
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    return n_same_amount / len(user_transactions) if user_transactions else 0.0


# def get_days_between_std(
#     transaction: Transaction, grouped_transactions: dict[tuple[str, str], list[Transaction]]
# ) -> float:
#     user_transactions = grouped_transactions.get((transaction.user_id, transaction.name), [])
#     if len(user_transactions) < 2:
#         return 100.0
#     dates = sorted([parse_date(t.date) for t in user_transactions])
#     diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
#     std = float(np.std(diffs) if diffs else 100.0)
#     return min(std, 100.0)


# def get_amount_cv(transaction: Transaction, grouped_transactions: dict[tuple[str, str], list[Transaction]]) -> float:
#     user_transactions = grouped_transactions.get((transaction.user_id, transaction.name), [])
#     if not user_transactions:
#         return 1.0
#     amounts = [t.amount for t in user_transactions]
#     mean = np.mean(amounts)
#     cv = float(np.std(amounts) / mean if mean > 0 else 1.0)
#     return min(cv, 10.0)


def get_has_recurring_keyword(transaction: Transaction) -> int:
    recurring_keywords = (
        r"\b(sub|membership|renewal|monthly|annual|premium|bill|plan|fee|auto|pay|service|"
        r"recurring|subscription|auto-renew|recurr|autopay|rec|month|year|quarterly|weekly|due)\b"
    )
    return int(bool(re.search(recurring_keywords, transaction.name, re.IGNORECASE)))


def get_is_convenience_store(transaction: Transaction) -> int:
    return int(
        bool(
            re.search(
                r"\b(7-eleven|cvs|walgreens|rite aid|circle k|quiktrip|speedway|ampm|"
                r"7 eleven|seven eleven|sheetz)\b",
                transaction.name,
                re.IGNORECASE,
            )
        )
    )


def get_pct_transactions_days_apart(
    transaction: Transaction, all_transactions: list[Transaction], n_days_apart: int, n_days_off: int
) -> float:
    if not all_transactions:
        return 0.0
    n_txs = get_n_transactions_days_apart(transaction, all_transactions, n_days_apart, n_days_off)
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    return n_txs / len(user_transactions) if user_transactions else 0.0


# def get_day_of_month_consistency(
#     transaction: Transaction, grouped_transactions: dict[tuple[str, str], list[Transaction]]
# ) -> float:
#     user_transactions = grouped_transactions.get((transaction.user_id, transaction.name), [])
#     if not user_transactions:
#         return 1.0
#     days = [int(t.date.split("-")[2]) for t in user_transactions if t != transaction]
#     if not days:
#         return 1.0
#     value_counts = pd.Series(days).value_counts(normalize=True)
#     entropy = -sum(p * np.log2(p + 1e-10) for p in value_counts)
#     return float(entropy / np.log2(31))


# def get_exact_amount_count(
#     transaction: Transaction, grouped_transactions: dict[tuple[str, str], list[Transaction]]
# ) -> int:
#     user_transactions = grouped_transactions.get((transaction.user_id, transaction.name), [])
#     return sum(1 for t in user_transactions if t.amount == transaction.amount)


def get_amount_range_consistency(
    transaction: Transaction, grouped_transactions: dict[tuple[str, str], list[Transaction]]
) -> float:
    user_transactions = grouped_transactions.get((transaction.user_id, transaction.name), [])
    if len(user_transactions) < 2:
        return 0.0
    amounts = [t.amount for t in user_transactions]
    tolerance = 0.05
    within_range = sum(1 for amt in amounts if abs(amt - transaction.amount) <= transaction.amount * tolerance)
    return within_range / len(user_transactions)


def get_recurring_period_score(
    transaction: Transaction, grouped_transactions: dict[tuple[str, str], list[Transaction]]
) -> float:
    user_transactions = grouped_transactions.get((transaction.user_id, transaction.name), [])
    if len(user_transactions) < 2:
        return 0.0
    transaction_date = parse_date(transaction.date)
    periods = [30, 60, 90]
    tolerance = 3
    score = 0
    for t in user_transactions:
        t_date = parse_date(t.date)
        days_diff = abs((t_date - transaction_date).days)
        for period in periods:
            if abs(days_diff - period) <= tolerance:
                score += 1
                break
    return score / len(user_transactions)


# def get_merchant_name_similarity(transaction: Transaction, all_transactions: list[Transaction]) -> float:
#     user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id and t != transaction]
#     if not user_transactions:
#         return 0.0
#     # similarities = [fuzz.ratio(transaction.name.lower(), t.name.lower()) / 100 for t in user_transactions]
#     return float(np.mean(similarities) if similarities else 0.0)


def get_transaction_frequency_score(
    transaction: Transaction, grouped_transactions: dict[tuple[str, str], list[Transaction]]
) -> float:
    user_transactions = []
    for (user_id, _), txs in grouped_transactions.items():
        if user_id == transaction.user_id:
            user_transactions.extend(txs)
    if not user_transactions:
        return 0.0
    merchant_transactions = grouped_transactions.get((transaction.user_id, transaction.name), [])
    return len(merchant_transactions) / len(user_transactions)


def get_new_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, Any]:
    grouped_transactions = group_transactions(all_transactions)
    return {
        "is_always_recurring": int(get_is_always_recurring(transaction)),
        "is_insurance": int(get_is_insurance(transaction)),
        "is_utility": int(get_is_utility(transaction)),
        "is_phone": int(get_is_phone(transaction)),
        "n_transactions_days_apart_30": get_n_transactions_days_apart(transaction, all_transactions, 30, 3),
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        # "days_between_std": get_days_between_std(transaction, grouped_transactions),  # Use grouped_transactions
        # "amount_cv": get_amount_cv(transaction, grouped_transactions),  # Use grouped_transactions
        "has_recurring_keyword": get_has_recurring_keyword(transaction),
        "is_convenience_store": get_is_convenience_store(transaction),
        "pct_transactions_days_apart_30": get_pct_transactions_days_apart(transaction, all_transactions, 30, 3),
        # "day_of_month_consistency": get_day_of_month_consistency(transaction, grouped_transactions),
        # "exact_amount_count": get_exact_amount_count(transaction, grouped_transactions),  # Use grouped_transactions
        "amount_range_consistency": get_amount_range_consistency(transaction, grouped_transactions),
        "recurring_period_score": get_recurring_period_score(transaction, grouped_transactions),
        # "merchant_name_similarity": get_merchant_name_similarity(transaction, all_transactions),
        "transaction_frequency_score": get_transaction_frequency_score(transaction, grouped_transactions),
    }
