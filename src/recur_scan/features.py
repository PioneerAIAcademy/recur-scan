from recur_scan.transactions import Transaction
import datetime

def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])


def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions) 

def get_day_of_week_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int]:
    date_obj = datetime.datetime.strptime(transaction.date, "%Y-%m-%d")
    merchant_transactions = [t for t in all_transactions if t.name == transaction.name]
    dates = sorted([datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in merchant_transactions])
    last_transaction_date = dates[-2] if len(dates) > 1 else None
    days_since_last = (date_obj - last_transaction_date).days if last_transaction_date else 0

    return {
        "day_of_month": date_obj.day,
        "weekday": date_obj.weekday(),  # Monday = 0, Sunday = 6
        "week_of_year": date_obj.isocalendar()[1],
        "is_weekend": int(date_obj.weekday() >= 5),  # 1 if weekend, 0 otherwise
        "days_since_last_transaction": days_since_last,
    } 

def get_frequency_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    merchant_transactions = [t for t in all_transactions if t.name == transaction.name]
    if len(merchant_transactions) < 2:
        return {"frequency": 0.0, "date_variability": 0.0, "median_frequency": 0.0, "std_frequency": 0.0}

    dates = sorted([datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in merchant_transactions])
    date_diffs = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
    avg_frequency = sum(date_diffs) / len(date_diffs)
    median_frequency = sorted(date_diffs)[len(date_diffs) // 2]
    std_frequency = (sum((x - avg_frequency) ** 2 for x in date_diffs) / len(date_diffs)) ** 0.5
    date_variability = max(date_diffs) - min(date_diffs)

    return {
        "frequency": avg_frequency,
        "date_variability": date_variability,
        "median_frequency": median_frequency,
        "std_frequency": std_frequency,
    }

def is_valid_recurring_transaction(transaction: Transaction) -> bool:
    """
    Check if a transaction is valid for being marked as recurring based on vendor-specific rules.
    
    Rules:
    - For 'Apple': Amount must end with '.99'.
    - For 'Brigit': Amount must be either 9.99 or 14.99.
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
        "hugo insurance"
    }

    if vendor_name == "apple":
        return abs(amount - int(amount)) >= 0.98 and abs(amount - int(amount)) <= 0.99
    elif vendor_name == "brigit":
        return amount in {9.99, 14.99}
    elif vendor_name == "cleo ai":
        return amount in {3.99, 6.99}
    elif vendor_name == "credit genie":
        return amount in {3.49, 4.99}
    elif vendor_name in always_recurring_vendors:
        return True
    else:
        # For other vendors, assume the transaction is valid for recurring
        return True
    
def get_amount_features(transaction: Transaction) -> dict[str, float]:
    return {
        "is_amount_rounded": int(transaction.amount == round(transaction.amount)),
        "amount_category": int(transaction.amount // 10),
    }

def get_vendor_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    vendor_transactions = [t for t in all_transactions if t.name == transaction.name]
    avg_amount = sum(t.amount for t in vendor_transactions) / len(vendor_transactions) if vendor_transactions else 0.0
    return {
        "n_transactions_with_vendor": len(vendor_transactions),
        "avg_amount_for_vendor": avg_amount,
    }

def get_time_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, int]:
    date_obj = datetime.datetime.strptime(transaction.date, "%Y-%m-%d")
    merchant_transactions = [t for t in all_transactions if t.name == transaction.name]
    dates = sorted([datetime.datetime.strptime(t.date, "%Y-%m-%d") for t in merchant_transactions])
    next_transaction_date = dates[dates.index(date_obj) + 1] if dates.index(date_obj) < len(dates) - 1 else None
    days_until_next = (next_transaction_date - date_obj).days if next_transaction_date else 0

    return {
        "month": date_obj.month,
        "days_until_next_transaction": days_until_next,
    }

def get_user_recurrence_rate(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    if len(user_transactions) < 2:
        return {"user_recurrence_rate": 0.0}

    recurring_count = sum(1 for t in user_transactions if is_valid_recurring_transaction(t))
    user_recurrence_rate = recurring_count / len(user_transactions)

    return {
        "user_recurrence_rate": user_recurrence_rate,
    }

def get_user_specific_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float]:
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    if len(user_transactions) < 2:
        return {"user_transaction_count": 0.0, "user_recurring_transaction_count": 0.0, "user_recurring_transaction_rate": 0.0}

    recurring_count = sum(1 for t in user_transactions if is_valid_recurring_transaction(t))
    user_recurring_transaction_rate = recurring_count / len(user_transactions)

    return {
        "user_transaction_count": len(user_transactions),
        "user_recurring_transaction_count": recurring_count,
        "user_recurring_transaction_rate": user_recurring_transaction_rate,
    }
        
def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        **get_day_of_week_features(transaction, all_transactions),
        **get_frequency_features(transaction, all_transactions),
        **get_amount_features(transaction),
        **get_vendor_features(transaction, all_transactions),
        **get_time_features(transaction, all_transactions),
        **get_user_recurrence_rate(transaction, all_transactions),
        "is_recurring": is_valid_recurring_transaction(transaction),
        **get_user_specific_features(transaction, all_transactions),
    }