import collections
import datetime
import itertools
import math
import statistics
from typing import Any

import numpy as np

from recur_scan.transactions import Transaction

# Allowed feature value type
FeatureValue = float | int | bool


def amount_ends_in_00(transaction: Transaction) -> bool:
    """Check if the transaction amount ends in .00 using string formatting after rounding."""
    amount_str = f"{round(transaction.amount, 2):.2f}"
    return amount_str.endswith("00")


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
        "netflix",
        "spotify",
        "hulu",
        "la fitness",
        "cleo ai",
        "atlas",
        "google storage",
        "google drive",
        "youtube premium",
        "afterpay",
        "amazon+",
        "walmart+",
        "amazonprime",
        "duke energy",
        "adobe",
        "healthy.line",
        "canva pty limite",
        "brigit",
        "cleo",
        "microsoft",
        "earnin",
    }
    merchant_name = transaction.name.lower()
    return any(keyword in merchant_name for keyword in recurring_keywords)


def get_n_transactions_same_merchant_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions with the same merchant and amount"""
    return sum(1 for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount)


def get_percent_transactions_same_merchant_amount(
    transaction: Transaction, all_transactions: list[Transaction]
) -> float:
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


def get_recurring_frequency(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Determine if the transaction is recurring daily, weekly, or monthly"""
    same_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name and t.amount == transaction.amount],
        key=lambda x: x.date,
    )
    if len(same_transactions) < 2:
        return 0
    intervals = [
        (
            datetime.datetime.strptime(t2.date, "%Y-%m-%d").date()
            - datetime.datetime.strptime(t1.date, "%Y-%m-%d").date()
        ).days
        for t1, t2 in itertools.pairwise(same_transactions)
    ]
    if not intervals:
        return 0
    avg_interval = sum(intervals) / len(intervals)
    if avg_interval <= 1:
        return 1
    elif avg_interval <= 7:
        return 2
    elif avg_interval <= 30:
        return 3
    else:
        return 0


def get_is_utility(transaction: Transaction) -> bool:
    """Determine if the transaction is related to utilities"""
    utility_keywords = {"utility", "utilities", "electric", "water", "gas", "power", "energy"}
    merchant_name = transaction.name.lower()
    return any(keyword in merchant_name for keyword in utility_keywords)


def get_is_phone(transaction: Transaction) -> bool:
    """Determine if the transaction is related to phone services"""
    merchant_name = transaction.name.lower()
    return ("at&t" in merchant_name) or ("t-mobile" in merchant_name) or ("verizon" in merchant_name)


def is_subscription_amount(transaction: Transaction) -> bool:
    """Check if the transaction amount is one of the common subscription amounts"""
    subscription_amounts = {0.99, 1.99, 2.99, 4.99, 9.99, 10.99, 11.99, 12.99, 14.99, 19.99}
    return round(transaction.amount, 2) in subscription_amounts


def get_additional_features(
    transaction: Transaction, all_transactions: list[Transaction]
) -> dict[str, float | int | bool]:
    """Extract additional temporal and merchant consistency features that are not already included."""
    trans_date = datetime.datetime.strptime(transaction.date, "%Y-%m-%d").date()
    day_of_week: int = trans_date.weekday()
    day_of_month: int = trans_date.day
    is_weekend: bool = day_of_week >= 5
    is_end_of_month: bool = day_of_month >= 28
    same_merchant_transactions = sorted(
        [t for t in all_transactions if t.name == transaction.name], key=lambda x: x.date
    )
    if same_merchant_transactions:
        first_date = datetime.datetime.strptime(same_merchant_transactions[0].date, "%Y-%m-%d").date()
        days_since_first: int = (trans_date - first_date).days
    else:
        days_since_first = 0
    intervals = []
    for t1, t2 in itertools.pairwise(same_merchant_transactions):
        d1 = datetime.datetime.strptime(t1.date, "%Y-%m-%d").date()
        d2 = datetime.datetime.strptime(t2.date, "%Y-%m-%d").date()
        intervals.append((d2 - d1).days)
    min_interval: int = min(intervals) if intervals else 0
    max_interval: int = max(intervals) if intervals else 0
    merchant_total_count: int = sum(1 for t in all_transactions if t.name == transaction.name)
    merchant_recent_count: int = sum(
        1
        for t in all_transactions
        if t.name == transaction.name
        and (trans_date - datetime.datetime.strptime(t.date, "%Y-%m-%d").date()).days <= 30
    )
    merchant_amounts = [t.amount for t in all_transactions if t.name == transaction.name]
    if merchant_amounts:
        amount_stddev: float = statistics.stdev(merchant_amounts) if len(merchant_amounts) > 1 else 0.0
        merchant_avg: float = statistics.mean(merchant_amounts)
    else:
        amount_stddev = 0.0
        merchant_avg = 0.0
    relative_amount_difference: float = (
        abs(transaction.amount - merchant_avg) / merchant_avg if merchant_avg != 0 else 0.0
    )
    return {
        "day_of_week": day_of_week,
        "day_of_month": day_of_month,
        "is_weekend": is_weekend,
        "is_end_of_month": is_end_of_month,
        "days_since_first_occurrence": days_since_first,
        "min_days_between": min_interval,
        "max_days_between": max_interval,
        "merchant_total_count": merchant_total_count,
        "merchant_recent_count": merchant_recent_count,
        "merchant_amount_stddev": amount_stddev,
        "relative_amount_difference": relative_amount_difference,
    }


# ------------------------- Functions for Detecting Amount Variations -------------------------


def get_amount_variation_features(
    transaction: Transaction, all_transactions: list[Transaction], threshold: float = 0.2
) -> dict[str, FeatureValue]:
    """
    Calculate features related to amount variations for a given transaction.
    """
    merchant_transactions = [t for t in all_transactions if t.name == transaction.name]
    merchant_avg = statistics.mean([t.amount for t in merchant_transactions]) if merchant_transactions else 0.0
    relative_diff = abs(transaction.amount - merchant_avg) / merchant_avg if merchant_avg != 0 else 0.0
    amount_anomaly = relative_diff > threshold
    return {
        "merchant_avg": merchant_avg,
        "relative_amount_diff": relative_diff,
        "amount_anomaly": amount_anomaly,
    }


# --------------------------------------------- New Feature--------------------------------------------------


def get_new_features(
    transaction: Any,
    all_transactions: list[Any],
    threshold: float = 0.2,
) -> dict[str, float | int | bool]:
    """Extracts comprehensive set of features for transaction recurrence detection."""
    # -------------------------- Core Features --------------------------
    # 1. Raw amount
    amt = transaction.amount

    # 2. Rolling mean of the last 3 amounts for this user+merchant
    same_user_merchant = sorted(
        [t for t in all_transactions if t.user_id == transaction.user_id and t.name == transaction.name],
        key=lambda t: datetime.datetime.strptime(t.date, "%Y-%m-%d"),
    )
    last_three = [t.amount for t in same_user_merchant if t.date <= transaction.date][-3:]
    rolling_mean = float(np.mean(last_three)) if last_three else 0.0

    # 3-5. Calendar features
    dt = datetime.datetime.strptime(transaction.date, "%Y-%m-%d")
    day_of_week = dt.weekday()  # 0=Monday … 6=Sunday
    day_of_month = dt.day  # 1-31
    month = dt.month  # 1-12

    # 6. Days since last same-merchant & same-amount transaction
    previous = [t for t in same_user_merchant if t.amount == amt and t.date < transaction.date]
    if previous:
        last_date = max(datetime.datetime.strptime(t.date, "%Y-%m-%d").date() for t in previous)
        days_since_last = (dt.date() - last_date).days
    else:
        days_since_last = 0

    # 7. Original recurring flag
    recurring_flag = bool(getattr(transaction, "recurring", False))

    # -------------------------- Additional Features --------------------------
    merchant_transactions = [t for t in all_transactions if t.name == transaction.name]
    merchant_avg = statistics.mean([t.amount for t in merchant_transactions]) if merchant_transactions else 0.0
    relative_diff = abs(transaction.amount - merchant_avg) / merchant_avg if merchant_avg != 0 else 0.0
    amount_anomaly = relative_diff > threshold

    same_amt = sorted(
        (t for t in merchant_transactions if t.amount == amt),
        key=lambda t: t.date,
    )
    intervals = [
        (
            datetime.datetime.strptime(t2.date, "%Y-%m-%d").date()
            - datetime.datetime.strptime(t1.date, "%Y-%m-%d").date()
        ).days
        for t1, t2 in itertools.pairwise(same_amt)
    ]

    if intervals:
        avg_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0.0
        interval_variance_ratio = std_interval / avg_interval if avg_interval else 0.0
        median_interval = statistics.median(intervals)
        mad_interval = statistics.median([abs(iv - median_interval) for iv in intervals])
    else:
        avg_interval = std_interval = interval_variance_ratio = 0.0
        median_interval = mad_interval = 0.0

    # Day-of-Month Consistency
    doms = [datetime.datetime.strptime(t.date, "%Y-%m-%d").day for t in same_amt]
    if doms:
        try:
            mode_dom = statistics.mode(doms)
        except statistics.StatisticsError:
            mode_dom = doms[0]
        dom_consistency = all(abs(d - mode_dom) <= 1 for d in doms)
    else:
        dom_consistency = False

    # Seasonality Score
    if intervals:
        weekly_count = sum(6 <= iv <= 8 for iv in intervals)
        monthly_count = sum(28 <= iv <= 32 for iv in intervals)
        seasonality_score = max(weekly_count, monthly_count) / len(intervals)
    else:
        seasonality_score = 0.0

    # Amount Drift (linear slope over time)
    if len(same_amt) > 1:
        dates_ord = [datetime.datetime.strptime(t.date, "%Y-%m-%d").toordinal() for t in same_amt]
        amounts = [t.amount for t in same_amt]
        slope = np.polyfit(dates_ord, amounts, 1)[0]
    else:
        slope = 0.0

    # Burstiness Ratio (recent vs prior 3 months)
    trans_date = dt.date()
    three_m_ago = trans_date - datetime.timedelta(days=90)
    last_3m = sum(
        1 for t in same_amt if three_m_ago <= datetime.datetime.strptime(t.date, "%Y-%m-%d").date() <= trans_date
    )
    prior_3m = sum(
        1
        for t in same_amt
        if three_m_ago - datetime.timedelta(days=90)
        <= datetime.datetime.strptime(t.date, "%Y-%m-%d").date()
        < three_m_ago
    )
    burstiness_ratio = (last_3m / prior_3m) if prior_3m else float(last_3m)

    # Expected-Next-Date Error
    if same_amt:
        last_date = datetime.datetime.strptime(same_amt[-1].date, "%Y-%m-%d").date()
        predicted = last_date + datetime.timedelta(days=avg_interval)
        next_date_error = abs((trans_date - predicted).days)
    else:
        next_date_error = 0

    # Serial Autocorrelation
    if len(intervals) > 1:
        mean_iv = statistics.mean(intervals)
        num = sum((intervals[i] - mean_iv) * (intervals[i - 1] - mean_iv) for i in range(1, len(intervals)))
        den = sum((iv - mean_iv) ** 2 for iv in intervals)
        acf1 = num / den if den else 0
    else:
        acf1 = 0

    # Seasonal Fourier Features
    doy = trans_date.timetuple().tm_yday
    sin_doy = math.sin(2 * math.pi * doy / 365)
    cos_doy = math.cos(2 * math.pi * doy / 365)

    # Weekday Concentration
    weekdays = [datetime.datetime.strptime(t.date, "%Y-%m-%d").weekday() for t in same_amt]
    top_count = max(collections.Counter(weekdays).values(), default=0)
    weekday_concentration = top_count / len(weekdays) if weekdays else 0

    # Interval Consistency Ratio
    if intervals:
        within = sum(abs(iv - median_interval) <= 0.1 * median_interval for iv in intervals)
        cons_ratio = within / len(intervals)
    else:
        cons_ratio = 0

    # Robust Amount Stats
    amounts = [t.amount for t in merchant_transactions]
    if amounts:
        med_amt = statistics.median(amounts)
        mad_amt = statistics.median([abs(a - med_amt) for a in amounts])
        q1, q3 = np.percentile(amounts, [25, 75])
        iqr_amt = q3 - q1
    else:
        med_amt = mad_amt = iqr_amt = 0.0

    features: dict[str, float | int | bool] = {
        # Core features
        "amount": float(amt),
        "rolling_mean_amount": rolling_mean,
        "day_of_week": day_of_week,
        "day_of_month": day_of_month,
        "month": month,
        "days_since_last": days_since_last,
        "recurring": recurring_flag,
        # Additional features
        "merchant_avg": merchant_avg,
        "relative_amount_diff": relative_diff,
        "amount_anomaly": amount_anomaly,
        "interval_variance_ratio": interval_variance_ratio,
        "dom_consistency": dom_consistency,
        "seasonality_score": seasonality_score,
        "amount_drift": slope,
        "burstiness_ratio": burstiness_ratio,
        "next_date_error": next_date_error,
        "serial_autocorrelation": acf1,
        "sin_doy": sin_doy,
        "cos_doy": cos_doy,
        "weekday_concentration": weekday_concentration,
        "interval_consistency_ratio": cons_ratio,
        "median_interval": median_interval,
        "mad_interval": mad_interval,
        "robust_iqr_amount": iqr_amt,
        "median_amount": med_amt,
        "mad_amount": mad_amt,
    }

    return features
