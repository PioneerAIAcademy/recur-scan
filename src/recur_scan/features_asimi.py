import datetime

from recur_scan.transactions import Transaction

# def get_frequency_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
#     merchant_transactions = [t for t in all_transactions if t.name == transaction.name]
#     if len(merchant_transactions) < 2:
#         return {
#             # "frequency": 0.0,
#             # "date_variability": 0.0,
#             # "median_frequency": 0.0,
#             # "std_frequency": 0.0
#         }

#     # dates = sorted([datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in merchant_transactions])
#     # date_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
#     # avg_frequency = sum(date_diffs) / len(date_diffs)
#     # median_frequency = sorted(date_diffs)[len(date_diffs) // 2]
#     # std_frequency = (sum((x - avg_frequency) ** 2 for x in date_diffs) / len(date_diffs)) ** 0.5
#     # date_variability = max(date_diffs) - min(date_diffs)

#     return {
#         # "frequency": avg_frequency,
#         # "date_variability": date_variability,
#         # "median_frequency": median_frequency,
#         # "std_frequency": std_frequency,
#     }


def is_valid_recurring_transaction(transaction: Transaction) -> bool:
    """
    Check if a transaction is valid for being marked as recurring based on vendor-specific rules.

    Rules:
    - For 'Apple', 'Brigit', 'Cleo AI', 'Credit Genie': Amount must end with '.99' (within floating point tolerance)
    and be less than 20. (Checking specific amounts is not reliable as they may change over time)
    """
    vendor_name = transaction.name.lower()
    amount = transaction.amount

    always_recurring_vendors = {
        "netflix",
        "spotify",
        "microsoft",
        "amazon prime",
        "at&t",
        "verizon",
        "spectrum",
        "geico",
        "hugo insurance",
    }

    # instead of checking for specific amounts, which may change over time, check for small amount ending in 0.99
    if vendor_name in {"apple", "brigit", "cleo ai", "credit genie"}:
        # Better way to check for .99 ending
        return amount < 20.00 and abs(amount - round(amount) + 0.01) < 0.001  # Check if decimal part is ~0.99
    elif vendor_name in always_recurring_vendors:
        return True
    else:
        return True


# def get_amount_features() -> dict[str, float]:
#     return {
#         # "is_amount_rounded": int(transaction.amount == round(transaction.amount)),
#         # "amount_category": int(transaction.amount // 10),
#     }


# def get_vendor_features() -> dict[str, float]:
#     # vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
#     # avg_amount = sum(t.amount for t in vendor_transactions) / len(vendor_transactions) \
#     if vendor_transactions else 0.0
#     return {
#         # "n_transactions_with_vendor": len(vendor_transactions),
#         # "avg_amount_for_vendor": avg_amount,
#     }


# def get_time_features() -> dict[str, int]:
#     # date_obj = datetime.datetime.strptime(transaction.date, "%Y-%m-%d")
#     # merchant_transactions = [t for t in all_transactions if t.name == transaction.name]
#     # dates = sorted([datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in merchant_transactions])
#     # next_transaction_date = dates[dates.index(date_obj) + 1] if dates.index(date_obj) < len(dates) - 1 else None
#     # days_until_next = (next_transaction_date - date_obj).days if next_transaction_date else 0

#     return {
#         # "month": date_obj.month,
#         # "days_until_next_transaction": days_until_next,
#     }


# def get_user_recurrence_rate(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
#     user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
#     if len(user_transactions) < 2:
#         return {
#             # "user_recurrence_rate": 0.0
#         }

#     # recurring_count = sum(1 for t in user_transactions if is_valid_recurring_transaction(t))
#     # user_recurrence_rate = recurring_count / len(user_transactions)

#     return {
#         # "user_recurrence_rate": user_recurrence_rate,
#     }


def get_user_recurring_transaction_count(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    if len(user_transactions) < 2:
        return 0.0

    recurring_count = sum(1 for t in user_transactions if is_valid_recurring_transaction(t))

    return recurring_count


# def get_user_recurring_vendor_count() -> dict[str, int]:
#     # user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
#     # recurring_vendors = {t.name for t in user_transactions if is_valid_recurring_transaction(t)}
#     return {
#         # "user_recurring_vendor_count": len(recurring_vendors)
#     }


# def get_user_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
#     user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
#     if len(user_transactions) < 2:
#         return {"user_transaction_frequency": 0.0}

#     # Sort transactions by date
#     user_transactions_sorted = sorted(user_transactions, key=lambda t: t.date)
#     dates = [datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in user_transactions_sorted]

#     # Calculate the average time between transactions
#     date_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
#     avg_frequency = sum(date_diffs) / len(date_diffs)

#     return {"user_transaction_frequency": avg_frequency}


# def get_vendor_amount_std(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
#     vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
#     if len(vendor_transactions) < 2:
#         return {
#             # "vendor_amount_std": 0.0
#         }

#     # amounts = [t.amount for t in vendor_transactions]
#     # mean_amount = sum(amounts) / len(amounts)
#     # std_amount = (sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5

#     return {
#         # "vendor_amount_std": std_amount
#     }


# def get_vendor_recurring_user_count() -> dict[str, int]:
#     # vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
#     # recurring_users = {t.user_id for t in vendor_transactions if is_valid_recurring_transaction(t)}
#     return {
#         # "vendor_recurring_user_count": len(recurring_users)
#     }


def get_vendor_transaction_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(vendor_transactions) < 2:
        return 0.0

    # Sort transactions by date
    vendor_transactions_sorted = sorted(vendor_transactions, key=lambda t: t.date)
    dates = [datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in vendor_transactions_sorted]

    # Calculate the average time between transactions
    date_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    avg_frequency = sum(date_diffs) / len(date_diffs)

    return avg_frequency


# def get_user_vendor_transaction_count() -> dict[str, int]:
#     # user_vendor_transactions = [
#     #     t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name
#     # ]
#     return {
#         # "user_vendor_transaction_count": len(user_vendor_transactions)
#     }


# def get_user_vendor_recurrence_rate(
#     transaction: Transaction, all_transactions: list[Transaction]
# ) -> dict[str, float]:
#     user_vendor_transactions = [
#         t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name
#     ]
#     if len(user_vendor_transactions) < 1:
#         return {
#             # "user_vendor_recurrence_rate": 0.0
#         }

#     # recurring_count = sum(1 for t in user_vendor_transactions if is_valid_recurring_transaction(t))
#     # recurrence_rate = recurring_count / len(user_vendor_transactions)

#     return {
#         # "user_vendor_recurrence_rate": recurrence_rate
#     }


# def get_user_vendor_interaction_count() -> dict[str, int]:
#     # user_vendor_transactions = [
#     #     t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name
#     # ]
#     return {
#         # "user_vendor_interaction_count": len(user_vendor_transactions)
#     }


# def get_amount_category(transaction: Transaction) -> dict[str, int]:
#     amount = transaction.amount
#     if amount < 10:
#         return {
#             # "amount_category": 0
#         }
#     elif 10 <= amount < 20:
#         return {
#             # "amount_category": 1
#         }
#     elif 20 <= amount < 50:
#         return {
#             # "amount_category": 2
#         }
#     else:
#         return {
#             # "amount_category": 3
#         }


def get_amount_decimal_part(transaction: Transaction) -> float:
    """Identify amount decimal part"""
    amount = transaction.amount

    return amount - int(amount)


def get_temporal_consistency_score(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Measure how consistent transaction timing is for this vendor"""
    vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(vendor_transactions) < 3:
        return 0.0

    dates = sorted([datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in vendor_transactions])
    date_diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

    # Check for monthly consistency (28-31 day intervals)
    monthly_diffs = [diff for diff in date_diffs if 28 <= diff <= 31]
    monthly_consistency = len(monthly_diffs) / len(date_diffs) if date_diffs else 0

    # Check for weekly consistency (7 day intervals)
    weekly_diffs = [diff for diff in date_diffs if 6 <= diff <= 8]
    weekly_consistency = len(weekly_diffs) / len(date_diffs) if date_diffs else 0

    return (monthly_consistency + weekly_consistency) / 2


def get_vendor_is_common_recurring(transaction: Transaction) -> int:
    """Analyze how often this vendor appears in recurring patterns across all users"""
    vendor_name = transaction.name.lower()

    common_recurring_vendors = {
        "netflix",
        "spotify",
        "microsoft",
        "amazon prime",
        "at&t",
        "verizon",
        "spectrum",
        "geico",
        "hugo insurance",
    }

    return int(vendor_name in common_recurring_vendors)


def get_user_vendor_relationship_features(
    transaction: Transaction, all_transactions: list[Transaction]
) -> dict[str, float]:
    """Analyze the relationship between this user and vendor"""
    user_vendor_transactions = [
        t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name
    ]
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]

    if not user_transactions:
        return {
            # "user_vendor_dependency": 0.0,
            "user_vendor_tenure": 0.0,
            "user_vendor_transaction_span": 0.0,
        }

    # Calculate what percentage of user's transactions are with this vendor
    # dependency = len(user_vendor_transactions) / len(user_transactions)

    # Calculate tenure (days since first transaction with this vendor)
    if user_vendor_transactions:
        dates = [datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in user_vendor_transactions]
        tenure = (max(dates) - min(dates)).days
    else:
        tenure = 0

    return {
        # "user_vendor_dependency": dependency,
        "user_vendor_tenure": tenure,
        "user_vendor_transaction_span": tenure,
    }
