from collections import defaultdict
import re
from datetime import datetime


from recur_scan.features_adedotun import (
    compute_recurring_inputs_at,
    get_is_always_recurring_at,
    get_is_communication_or_energy_at,
    get_percent_transactions_same_amount_tolerant,
    is_recurring_allowance_at,
    is_recurring_core_at,
)
from recur_scan.features_adeyinka import (
    get_average_days_between_transactions,
    get_outlier_score,
    get_recurring_confidence_score,
    get_same_amount_vendor_transactions,
    get_subscription_keyword_score,
    get_time_regularity_score,
    get_transaction_amount_variance,
)
from recur_scan.features_adeyinka import (
    get_is_always_recurring as get_is_always_recurring_adeyinka,
)
from recur_scan.features_adeyinka import (
    get_n_transactions_days_apart as get_n_transactions_days_apart_adeyinka,
)
from recur_scan.features_asimi import (
    get_amount_category,
    get_amount_pattern_features,
    get_temporal_consistency_features,
    get_user_recurring_vendor_count,
    get_user_specific_features,
    get_user_transaction_frequency,
    get_user_vendor_interaction_count,
    get_user_vendor_recurrence_rate,
    get_user_vendor_relationship_features,
    get_user_vendor_transaction_count,
    get_vendor_amount_std,
    get_vendor_recurrence_profile,
    get_vendor_recurring_user_count,
    get_vendor_transaction_frequency,
    is_valid_recurring_transaction,
)
from recur_scan.features_asimi import (
    get_amount_features as get_amount_features_asimi,
)
from recur_scan.features_bassey import (
    get_is_gym_membership,
    get_is_streaming_service,
    get_is_subscription,
)
from recur_scan.features_christopher import (
    detect_skipped_months,
    follows_regular_interval,
    get_coefficient_of_variation,
    get_day_of_month_consistency,
    get_median_interval,
    get_n_transactions_same_amount_chris,
    get_percent_transactions_same_amount_chris,
    get_transaction_frequency,
    get_transaction_std_amount,
    is_known_fixed_subscription,
    is_known_recurring_company,
)
from recur_scan.features_ebenezer import (
    get_avg_amount_same_day_of_week,
    get_avg_amount_same_month,
    get_avg_amount_same_name,
    get_n_transactions_same_month,
    get_n_transactions_same_name,
    get_n_transactions_same_user_id,
    get_n_transactions_within_amount_range,
    get_percent_transactions_same_day_of_week,
    get_percent_transactions_same_month,
    get_percent_transactions_same_name,
    get_percent_transactions_same_user_id,
    get_percent_transactions_within_amount_range,
    get_std_amount_same_day_of_week,
    get_std_amount_same_month,
    get_std_amount_same_name,
)
from recur_scan.features_elliot import (
    get_is_always_recurring as get_is_always_recurring_elliot,
)
from recur_scan.features_elliot import (
    get_is_near_same_amount,
    get_transaction_similarity,
    is_auto_pay,
    is_membership,
    is_price_trending,
    is_recurring_based_on_99,
    is_split_transaction,
    is_utility_bill,
    is_weekday_transaction,
)
from recur_scan.features_emmanuel_ezechukwu1 import (
    get_amount_cv,
    get_days_between_std,
    get_exact_amount_count,
    get_has_recurring_keyword,
    get_is_convenience_store,
)
from recur_scan.features_emmanuel_ezechukwu1 import (
    get_day_of_month_consistency as get_day_of_month_consistency_emmanuel1,
)
from recur_scan.features_emmanuel_ezechukwu1 import (
    get_is_always_recurring as get_is_always_recurring_emmanuel1,
)
from recur_scan.features_emmanuel_ezechukwu1 import (
    get_is_insurance as get_is_insurance_emmanuel1,
)
from recur_scan.features_emmanuel_ezechukwu1 import (
    get_is_phone as get_is_phone_emmanuel1,
)
from recur_scan.features_emmanuel_ezechukwu1 import (
    get_is_utility as get_is_utility_emmanuel1,
)
from recur_scan.features_emmanuel_ezechukwu1 import (
    get_n_transactions_days_apart as get_n_transactions_days_apart_emmanuel1,
)
from recur_scan.features_emmanuel_ezechukwu1 import (
    get_n_transactions_same_amount as get_n_transactions_same_amount_emmanuel1,
)
from recur_scan.features_emmanuel_ezechukwu1 import (
    get_percent_transactions_same_amount as get_percent_transactions_same_amount_emmanuel1,
)
from recur_scan.features_emmanuel_ezechukwu2 import (
    classify_subscription_tier,
    get_monthly_spending_trend,
    get_recurrence_patterns,
    get_recurring_consistency_score,
    get_refund_features,
    get_user_behavior_features,
    validate_recurring_transaction,
)
from recur_scan.features_emmanuel_ezechukwu2 import (
    get_amount_features as get_amount_features_emmanuel2,
)
from recur_scan.features_ernest import (
    get_average_transaction_amount as get_average_transaction_amount_ernest,
)
from recur_scan.features_ernest import (
    get_is_biweekly,
    get_is_fixed_amount,
    get_is_high_frequency_vendor,
    get_is_monthly,
    get_is_quarterly,
    get_is_recurring_vendor,
    get_is_round_amount,
    get_is_same_day_of_month,
    get_is_small_amount,
    get_is_subscription_based,
    get_is_weekly,
    get_recurring_interval_score,
    get_transaction_gap_stats,
    get_vendor_amount_variance,
    get_vendor_transaction_count,
)
from recur_scan.features_ernest import (
    get_is_weekend_transaction as get_is_weekend_transaction_ernest,
)
from recur_scan.features_ernest import (
    get_transaction_frequency as get_transaction_frequency_ernest,
)
from recur_scan.features_felix import (
    get_average_transaction_amount as get_average_transaction_amount_felix,
)
from recur_scan.features_felix import (
    get_day as get_day_felix,
)
from recur_scan.features_felix import (
    get_dispersion_transaction_amount as get_dispersion_transaction_amount_felix,
)
from recur_scan.features_felix import (
    get_is_always_recurring as get_is_always_recurring_felix,
)
from recur_scan.features_felix import (
    get_is_insurance as get_is_insurance_felix,
)
from recur_scan.features_felix import (
    get_is_phone as get_is_phone_felix,
)
from recur_scan.features_felix import (
    get_is_utility as get_is_utility_felix,
)
from recur_scan.features_felix import (
    get_max_transaction_amount as get_max_transaction_amount_felix,
)
from recur_scan.features_felix import (
    get_median_variation_transaction_amount,
    get_month,
    get_n_transactions_same_vendor,
    get_transaction_rate,
    get_transactions_interval_stability,
    get_variation_ratio,
    get_year,
)
from recur_scan.features_felix import (
    get_min_transaction_amount as get_min_transaction_amount_felix,
)
from recur_scan.features_felix import (
    get_transaction_intervals as get_transaction_intervals_felix,
)
from recur_scan.features_frank import (
    amount_coefficient_of_variation,
    amount_similarity,
    amount_stability_score,
    amount_z_score,
    detect_non_recurring_pattern,
    detect_recurring_company,
    detect_subscription_pattern,
    frequency_features,
    get_enhanced_features,
    get_same_amount_ratio,
    get_transaction_intervals,
    get_transaction_stability_features,
    merchant_category_features,
    normalized_days_difference,
    one_time_features,
    proportional_timing_deviation,
    recurrence_interval_variance,
    seasonal_spending_cycle,
    vendor_recurrence_trend,
    weekly_spending_cycle,
)
from recur_scan.features_freedom import (
    get_day_of_week,
    get_days_until_next_transaction,
    get_periodicity_confidence,
    get_recurrence_streak,
)
from recur_scan.features_happy import (
    get_day_of_month_consistency as get_day_of_month_consistency_happy,
)
from recur_scan.features_happy import (
    get_n_transactions_same_description,
    get_percent_transactions_same_description,
)
from recur_scan.features_happy import (
    get_transaction_frequency as get_transaction_frequency_happy,
)
from recur_scan.features_laurels import (
    _aggregate_transactions,
    _calculate_intervals,
    _calculate_statistics,
    date_irregularity_dominance,
    day_consistency_score_feature,
    day_of_week_feature,
    identical_transaction_ratio_feature,
    interval_variability_feature,
    is_deposit_feature,
    is_monthly_recurring_feature,
    is_near_periodic_interval_feature,
    is_single_transaction_feature,
    is_varying_amount_recurring_feature,
    low_amount_variation_feature,
    merchant_amount_frequency_feature,
    merchant_amount_std_feature,
    merchant_interval_mean_feature,
    merchant_interval_std_feature,
    non_recurring_irregularity_score,
    recurrence_likelihood_feature,
    rolling_amount_mean_feature,
    time_since_last_transaction_same_merchant_feature,
    transaction_month_feature,
    transaction_pattern_complexity,
)
from recur_scan.features_naomi import (
    get_irregular_periodicity,
    get_irregular_periodicity_with_tolerance,
    get_n_same_name_transactions,
    get_time_between_transactions,
    get_transaction_amount_stability,
    get_transaction_time_of_month,
    get_vendor_recurrence_consistency,
    get_vendor_recurring_ratio,
)
from recur_scan.features_naomi import (
    get_transaction_frequency as get_transaction_frequency_naomi,
)
from recur_scan.features_naomi import (
    get_user_transaction_frequency as get_user_transaction_frequency_naomi,
)
from recur_scan.features_nnanna import (
    get_average_transaction_amount,
    get_dispersion_transaction_amount,
    get_mad_transaction_amount,
    get_mobile_transaction,
    get_time_interval_between_transactions,
    get_transaction_interval_consistency,
)
from recur_scan.features_nnanna import (
    get_coefficient_of_variation as get_coefficient_of_variation_nnanna,
)
from recur_scan.features_nnanna import (
    get_transaction_frequency as get_transaction_frequency_nnanna,
)
from recur_scan.features_original import (
    get_ends_in_99,
    get_is_always_recurring,
    get_is_insurance,
    get_is_phone,
    get_is_utility,
    get_n_transactions_days_apart,
    get_n_transactions_same_amount,
    get_n_transactions_same_day,
    get_pct_transactions_days_apart,
    get_pct_transactions_same_day,
    get_percent_transactions_same_amount,
    get_transaction_z_score,
)
from recur_scan.features_osasere import (
    get_day_of_month_consistency as get_day_of_month_consistency_osasere,
)
from recur_scan.features_osasere import (
    get_day_of_month_variability,
    get_median_period,
    get_recurrence_confidence,
    has_min_recurrence_period,
    is_weekday_consistent,
)
from recur_scan.features_praise import (
    amount_ends_in_00,
    amount_ends_in_99,
    get_avg_days_between_same_merchant_amount,
    get_days_since_last_same_merchant_amount,
    get_interval_variance_coefficient,
    get_max_transaction_amount,
    get_min_transaction_amount,
    get_most_frequent_names,
    get_n_transactions_same_merchant_amount,
    get_percent_transactions_same_merchant_amount,
    get_stddev_days_between_same_merchant_amount,
    has_consistent_reference_codes,
    has_incrementing_numbers,
    is_expected_transaction_date,
    is_recurring,
    is_recurring_merchant,
)
from recur_scan.features_praise import (
    get_average_transaction_amount as get_average_transaction_amount_praise,
)
from recur_scan.features_precious import (
    amount_ends_in_00 as amount_ends_in_00_precious,
)
from recur_scan.features_precious import (
    get_additional_features,
    get_amount_variation_features,
    get_recurring_frequency,
    is_subscription_amount,
)
from recur_scan.features_precious import (
    get_avg_days_between_same_merchant_amount as get_avg_days_between_same_merchant_amount_precious,
)
from recur_scan.features_precious import (
    get_days_since_last_same_merchant_amount as get_days_since_last_same_merchant_amount_precious,
)
from recur_scan.features_precious import (
    get_n_transactions_same_merchant_amount as get_n_transactions_same_merchant_amount_precious,
)
from recur_scan.features_precious import (
    get_percent_transactions_same_merchant_amount as get_percent_transactions_same_merchant_amount_precious,
)
from recur_scan.features_precious import (
    get_stddev_days_between_same_merchant_amount as get_stddev_days_between_same_merchant_amount_precious,
)
from recur_scan.features_precious import (
    is_recurring_merchant as is_recurring_merchant_precious,
)
from recur_scan.features_raphael import (
    get_has_irregular_spike,
    get_is_common_subscription_amount,
    get_is_first_of_month,
    get_is_fixed_interval,
    get_is_similar_name,
    get_occurs_same_week,
)
from recur_scan.features_raphael import (
    get_n_transactions_days_apart as get_n_transactions_days_apart_raphael,
)
from recur_scan.features_raphael import (
    get_n_transactions_same_day as get_n_transactions_same_day_raphael,
)
from recur_scan.features_raphael import (
    get_pct_transactions_days_apart as get_pct_transactions_days_apart_raphael,
)
from recur_scan.features_raphael import (
    get_pct_transactions_same_day as get_pct_transactions_same_day_raphael,
)
from recur_scan.features_samuel import (
    get_amount_std_dev,
    get_is_weekend_transaction,
    get_median_transaction_amount,
)
from recur_scan.features_samuel import (
    get_is_always_recurring as get_is_always_recurring_samuel,
)
from recur_scan.features_samuel import (
    get_transaction_frequency as get_transaction_frequency_samuel,
)
from recur_scan.features_segun import (
    get_average_transaction_amount as get_average_transaction_amount_segun,
)
from recur_scan.features_segun import (
    get_average_transaction_interval,
    get_total_transaction_amount,
    get_transaction_amount_frequency,
    get_transaction_amount_median,
    get_transaction_amount_std,
    get_transaction_day_of_week,
    get_transaction_time_of_day,
    get_unique_transaction_amount_count,
)
from recur_scan.features_segun import (
    get_max_transaction_amount as get_max_transaction_amount_segun,
)
from recur_scan.features_segun import (
    get_min_transaction_amount as get_min_transaction_amount_segun,
)
from recur_scan.features_segun import (
    get_transaction_amount_range as get_transaction_amount_range_segun,
)
from recur_scan.features_tife import (
    get_amount_cluster_count,
    get_amount_range,
    get_amount_relative_change,
    get_amount_variability,
    get_days_since_last_same_amount,
    get_dominant_interval_strength,
    get_interval_consistency,
    get_interval_histogram,
    get_interval_mode,
    get_merchant_amount_signature,
    get_merchant_name_frequency,
    get_near_amount_consistency,
    get_normalized_interval_consistency,
    get_transaction_count,
    get_transaction_density,
)
from recur_scan.features_tife import (
    get_amount_stability_score as get_amount_stability_score_tife,
)
from recur_scan.features_tife import (
    get_transaction_frequency as get_transaction_frequency_tife,
)
from recur_scan.features_victor import get_avg_days_between
from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date

# feature/add-xbox-and-recur-companies-feature
def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring because of the vendor name - check lowercase match"""
    always_recurring_vendors = {
        "google storage",
        "netflix",
        "hulu",
        "spotify",
        "Empower",
        "T-Mobile",
        "AT&T",
        "Verizon",
        "Amazon Prime",
        "Amazon",
        "Apple",
        "Apple Music",
        "Apple TV",
        "Youtube G.co",

    }
    return transaction.name.lower() in always_recurring_vendors


def get_is_insurance(transaction: Transaction) -> bool:
    """Check if the transaction is an insurance payment."""
    # use a regular expression with boundaries to match case-insensitive insurance
    # and insurance-related terms
    match = re.search(r"\b(insurance|insur|insuranc)\b", transaction.name, re.IGNORECASE)
    return bool(match)


def get_is_utility(transaction: Transaction) -> bool:
    """Check if the transaction is a utility payment."""
    # use a regular expression with boundaries to match case-insensitive utility
    # and utility-related terms
    match = re.search(r"\b(utility|utilit|energy)\b", transaction.name, re.IGNORECASE)
    return bool(match)

def get_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int | bool]:
    """Get the features for a transaction"""
    """Extract all features for a transaction by calling individual feature functions.
    This prepares a dictionary of features for model training.
main

    Args:
        transaction (Transaction): The transaction to extract features for.
        all_transactions (List[Transaction]): List of all transactions for context.

    Returns:
        Dict[str, Union[float, int]]: Dictionary mapping feature names to their computed values.
    """
    # Compute groups and amount counts internally
    groups = _aggregate_transactions(all_transactions)
    amount_counts: defaultdict[float, int] = defaultdict(int)
    for t in all_transactions:
        amount_counts[t.amount] += 1

    # Extract user ID and merchant name from the transaction
    user_id, merchant_name = transaction.user_id, transaction.name
    # Get transactions for this user and merchant
    merchant_trans = groups.get(user_id, {}).get(merchant_name, [])
    # Sort transactions by date for chronological analysis
    merchant_trans.sort(key=lambda x: x.date)

    # Parse all dates for this merchant's transactions once
    parsed_dates = []
    for trans in merchant_trans:
        date = parse_date(trans.date)
        if date is not None:
            parsed_dates.append(date)

    # Calculate intervals and amounts for statistical analysis
    intervals = _calculate_intervals(parsed_dates)
    amounts = [trans.amount for trans in merchant_trans]
    interval_stats = _calculate_statistics([float(i) for i in intervals])
    amount_stats = _calculate_statistics(amounts)

    histogram = get_interval_histogram(all_transactions)

# feature/add-xbox-and-recur-companies-feature
def is_microsoft_xbox_same_or_near_day(transaction: Transaction, all_transactions: list[Transaction]) -> bool:
    """
    Check if the transaction is for 'Microsoft Xbox' and occurs on the same day of the month
    or within 2 days before or after the previous transaction date.
    """
    if "microsoft xbox" not in transaction.name.lower():
        return False

    transaction_day = _get_day(transaction.date)
    for t in all_transactions:
        if "microsoft xbox" in t.name.lower():
            previous_day = _get_day(t.date)
            if abs(transaction_day - previous_day) <= 2:
                return True

    return False

def calculate_avg_days_between_transactions(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Calculate the average number of days between transactions for the same vendor."""
    transaction_days = [_get_days(t.date) for t in all_transactions]
    transaction_days.sort()
    if len(transaction_days) < 2:
        return 0.0  # Not enough transactions to calculate
    day_differences = [transaction_days[i] - transaction_days[i - 1] for i in range(1, len(transaction_days))]
    return sum(day_differences) / len(day_differences)

    vendor_txns, user_vendor_txns, preprocessed = compute_recurring_inputs_at(transaction, all_transactions)
    date_obj = preprocessed["date_objects"][transaction]
    total_txns = len(vendor_txns)
    main

    return {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
        "ends_in_99": get_ends_in_99(transaction),
        "amount": transaction.amount,
        "same_day_exact": get_n_transactions_same_day(transaction, all_transactions, 0),
        "pct_transactions_same_day": get_pct_transactions_same_day(transaction, all_transactions, 0),
        "same_day_off_by_1": get_n_transactions_same_day(transaction, all_transactions, 1),
        "same_day_off_by_2": get_n_transactions_same_day(transaction, all_transactions, 2),
        "14_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 14, 0),
        "pct_14_days_apart_exact": get_pct_transactions_days_apart(transaction, all_transactions, 14, 0),
        "14_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 14, 1),
        "pct_14_days_apart_off_by_1": get_pct_transactions_days_apart(transaction, all_transactions, 14, 1),
        "7_days_apart_exact": get_n_transactions_days_apart(transaction, all_transactions, 7, 0),
        "pct_7_days_apart_exact": get_pct_transactions_days_apart(transaction, all_transactions, 7, 0),
        "7_days_apart_off_by_1": get_n_transactions_days_apart(transaction, all_transactions, 7, 1),
        "pct_7_days_apart_off_by_1": get_pct_transactions_days_apart(transaction, all_transactions, 7, 1),
        "is_insurance": get_is_insurance(transaction),
        "is_utility": get_is_utility(transaction),
        "is_phone": get_is_phone(transaction),
        "is_always_recurring": get_is_always_recurring(transaction),
feature/add-xbox-and-recur-companies-feature
        "is_microsoft_xbox_same_or_near_day": is_microsoft_xbox_same_or_near_day(transaction, all_transactions),


        "z_score": get_transaction_z_score(transaction, all_transactions),
        "abs_z_score": abs(get_transaction_z_score(transaction, all_transactions)),
        # Frank's features
        "likely_same_amount": amount_similarity(transaction, all_transactions),
        "normalized_days_difference": normalized_days_difference(transaction, all_transactions),
        "amount_stability_score": amount_stability_score(all_transactions),
        "amount_z_score": amount_z_score(transaction, all_transactions),
        "weekly_spendings ": weekly_spending_cycle(all_transactions),
        "vendor_recurrence_trend": vendor_recurrence_trend(all_transactions),
        "seasonal_spending_cycle": seasonal_spending_cycle(transaction, all_transactions),
        "recurrence_interval_variance": recurrence_interval_variance(all_transactions),
        **frequency_features(all_transactions),
        **detect_non_recurring_pattern(all_transactions),  # Merges non-recurring pattern features
        **get_transaction_intervals(all_transactions),  # Merges new time-based features
        "amount_ratio": get_same_amount_ratio(transaction, all_transactions),
        "amount_coefficient_of_variation": amount_coefficient_of_variation(all_transactions),
        "proportional_timing_deviation": proportional_timing_deviation(transaction, all_transactions),
        **detect_recurring_company(transaction.name),  # Merges recurring company features
        **merchant_category_features(transaction.name),  # Merges merchant category features
        **one_time_features(all_transactions),  # Merges one-time purchase features
        **detect_subscription_pattern(all_transactions),  # Merges subscription-based features
        **get_enhanced_features(transaction, all_transactions, len(all_transactions)),  # Merges new enhanced features
        **get_transaction_stability_features(all_transactions),  # Merges new stability-based features
        # Christopher's features
        "n_transactions_same_name": len(all_transactions),
        "n_transactions_same_amount_chris": get_n_transactions_same_amount_chris(transaction, all_transactions),
        "percent_transactions_same_amount_chris": get_percent_transactions_same_amount_chris(
            transaction, all_transactions
        ),
        "transaction_frequency": get_transaction_frequency(all_transactions),
        "transaction_std_amount": get_transaction_std_amount(all_transactions),
        "follows_regular_interval": follows_regular_interval(all_transactions),
        "skipped_months": detect_skipped_months(all_transactions),
        "day_of_month_consistency": get_day_of_month_consistency(all_transactions),
        "coefficient_of_variation": get_coefficient_of_variation(all_transactions),
        "median_interval": get_median_interval(all_transactions),
        "is_known_recurring_company": is_known_recurring_company(transaction.name),
        "is_known_fixed_subscription": is_known_fixed_subscription(transaction),
        # Laurels' features
        "identical_transaction_ratio": identical_transaction_ratio_feature(
            transaction, all_transactions, merchant_trans
        ),
        "is_monthly_recurring": is_monthly_recurring_feature(merchant_trans),
        "recurrence_likelihood": recurrence_likelihood_feature(merchant_trans, interval_stats, amount_stats),
        "is_varying_amount_recurring": is_varying_amount_recurring_feature(interval_stats, amount_stats),
        "day_consistency_score": day_consistency_score_feature(merchant_trans),
        "is_near_periodic_interval": is_near_periodic_interval_feature(interval_stats),
        "merchant_amount_std": merchant_amount_std_feature(amount_stats),
        "merchant_interval_std": merchant_interval_std_feature(interval_stats),
        "merchant_interval_mean": merchant_interval_mean_feature(interval_stats),
        "time_since_last_transaction_same_merchant": time_since_last_transaction_same_merchant_feature(parsed_dates),
        "is_deposit": is_deposit_feature(transaction, merchant_trans),
        "day_of_week": day_of_week_feature(transaction),
        "transaction_month": transaction_month_feature(transaction),
        "rolling_amount_mean": rolling_amount_mean_feature(merchant_trans),
        "low_amount_variation": low_amount_variation_feature(amount_stats),
        "is_single_transaction": is_single_transaction_feature(merchant_trans),
        "interval_variability": interval_variability_feature(interval_stats),
        "merchant_amount_frequency": merchant_amount_frequency_feature(merchant_trans),
        "non_recurring_irregularity_score": non_recurring_irregularity_score(
            merchant_trans, interval_stats, amount_stats
        ),
        "transaction_pattern_complexity": transaction_pattern_complexity(merchant_trans, interval_stats),
        "date_irregularity_dominance": date_irregularity_dominance(merchant_trans, interval_stats, amount_stats),
        # Emmanuel Ezechukwu (2)'s features
        **get_recurrence_patterns(transaction, all_transactions),
        **get_recurring_consistency_score(transaction, all_transactions),
        "is_recurring": int(validate_recurring_transaction(transaction)),
        "subscription_tier": classify_subscription_tier(transaction),
        **get_amount_features_emmanuel2(transaction, all_transactions),
        **get_user_behavior_features(transaction, all_transactions),
        **get_refund_features(transaction, all_transactions),
        **get_monthly_spending_trend(transaction, all_transactions),
        # Nnanna's features
        "time_interval_between_transactions": get_time_interval_between_transactions(transaction, all_transactions),
        "mobile_company": get_mobile_transaction(transaction),
        "transaction_frequency_nnanna": get_transaction_frequency_nnanna(transaction, all_transactions),
        "transaction_amount_dispersion": get_dispersion_transaction_amount(transaction, all_transactions),
        "mad_transaction_amount": get_mad_transaction_amount(transaction, all_transactions),
        "coefficient_of_variation_nnanna": get_coefficient_of_variation_nnanna(transaction, all_transactions),
        "transaction_interval_consistency": get_transaction_interval_consistency(transaction, all_transactions),
        "average_transaction_amount": get_average_transaction_amount(transaction, all_transactions),
        # Ebenezer's features
        "n_transactions_same_name_ebenezer": get_n_transactions_same_name(transaction, all_transactions),
        "percent_transactions_same_name": get_percent_transactions_same_name(transaction, all_transactions),
        "avg_amount_same_name": get_avg_amount_same_name(transaction, all_transactions),
        "std_amount_same_name": get_std_amount_same_name(transaction, all_transactions),
        "n_transactions_same_month": get_n_transactions_same_month(transaction, all_transactions),
        "percent_transactions_same_month": get_percent_transactions_same_month(transaction, all_transactions),
        "avg_amount_same_month": get_avg_amount_same_month(transaction, all_transactions),
        "std_amount_same_month": get_std_amount_same_month(transaction, all_transactions),
        "n_transactions_same_user_id": get_n_transactions_same_user_id(transaction, all_transactions),
        "percent_transactions_same_user_id": get_percent_transactions_same_user_id(transaction, all_transactions),
        "percent_transactions_same_day_of_week": get_percent_transactions_same_day_of_week(
            transaction, all_transactions
        ),
        "avg_amount_same_day_of_week": get_avg_amount_same_day_of_week(transaction, all_transactions),
        "std_amount_same_day_of_week": get_std_amount_same_day_of_week(transaction, all_transactions),
        "n_transactions_within_amount_range": get_n_transactions_within_amount_range(transaction, all_transactions),
        "percent_transactions_within_amount_range": get_percent_transactions_within_amount_range(
            transaction, all_transactions
        ),
        # Praise's features
        "is_recurring_merchant": is_recurring_merchant(transaction),
        "avg_days_between_same_merchant_amount": get_avg_days_between_same_merchant_amount(
            transaction, all_transactions
        ),
        "average_transaction_amount_praise": get_average_transaction_amount_praise(all_transactions),
        "max_transaction_amount": get_max_transaction_amount(all_transactions),
        "min_transaction_amount": get_min_transaction_amount(all_transactions),
        "most_frequent_names": len(get_most_frequent_names(all_transactions)),
        "is_recurring_praise": is_recurring(transaction, all_transactions),
        "amount_ends_in_99": amount_ends_in_99(transaction),
        "amount_ends_in_00": amount_ends_in_00(transaction),
        "n_transactions_same_merchant_amount": get_n_transactions_same_merchant_amount(transaction, all_transactions),
        "percent_transactions_same_merchant_amount": get_percent_transactions_same_merchant_amount(
            transaction, all_transactions
        ),
        "interval_variance_coefficient": get_interval_variance_coefficient(transaction, all_transactions),
        "stddev_days_between_same_merchant_amount": get_stddev_days_between_same_merchant_amount(
            transaction, all_transactions
        ),
        "days_since_last_same_merchant_amount": get_days_since_last_same_merchant_amount(transaction, all_transactions),
        "is_expected_transaction_date": is_expected_transaction_date(transaction, all_transactions),
        "has_incrementing_numbers": has_incrementing_numbers(transaction, all_transactions),
        "has_consistent_reference_codes": has_consistent_reference_codes(transaction, all_transactions),
        # Emmanuel Ezechukwu (1)'s features
        "n_transactions_same_amount_emmanuel1": get_n_transactions_same_amount_emmanuel1(transaction, all_transactions),
        "percent_transactions_same_amount_emmanuel1": get_percent_transactions_same_amount_emmanuel1(
            transaction, all_transactions
        ),
        "days_between_std": get_days_between_std(transaction, all_transactions),
        "amount_cv": get_amount_cv(transaction, all_transactions),
        "day_of_month_consistency_emmanuel1": get_day_of_month_consistency_emmanuel1(transaction, all_transactions),
        "exact_amount_count": get_exact_amount_count(transaction, all_transactions),
        "has_recurring_keyword": get_has_recurring_keyword(transaction),
        "is_always_recurring_emmanuel1": int(get_is_always_recurring_emmanuel1(transaction)),
        "n_transactions_30_days_apart": get_n_transactions_days_apart_emmanuel1(transaction, all_transactions, 30, 2),
        "is_convenience_store_emmanuel1": get_is_convenience_store(transaction),
        "is_insurance_emmanuel1": int(get_is_insurance_emmanuel1(transaction)),
        "is_utility_emmanuel1": int(get_is_utility_emmanuel1(transaction)),
        "is_phone_emmanuel1": int(get_is_phone_emmanuel1(transaction)),
        # Asimi's features
        **get_amount_features_asimi(transaction),
        **get_user_recurring_vendor_count(transaction, all_transactions),
        **get_user_transaction_frequency(transaction, all_transactions),
        **get_vendor_amount_std(transaction, all_transactions),
        **get_vendor_recurring_user_count(transaction, all_transactions),
        **get_vendor_transaction_frequency(transaction, all_transactions),
        **get_user_vendor_transaction_count(transaction, all_transactions),
        **get_user_vendor_recurrence_rate(transaction, all_transactions),
        **get_user_vendor_interaction_count(transaction, all_transactions),
        **get_amount_category(transaction),
        **get_amount_pattern_features(transaction, all_transactions),
        **get_temporal_consistency_features(transaction, all_transactions),
        **get_vendor_recurrence_profile(transaction, all_transactions),
        **get_user_vendor_relationship_features(transaction, all_transactions),
        "is_recurring_asimi": is_valid_recurring_transaction(transaction),
        **get_user_specific_features(transaction, all_transactions),
        # Samuel's features
        "transaction_frequency_samuel": get_transaction_frequency_samuel(transaction, all_transactions),
        "amount_std_dev": get_amount_std_dev(transaction, all_transactions),
        "median_transaction_amount": get_median_transaction_amount(transaction, all_transactions),
        "is_weekend_transaction": get_is_weekend_transaction(transaction),
        "is_always_recurring_samuel": get_is_always_recurring_samuel(transaction),
        # Precious's features
        "amount_ends_in_00_precious": amount_ends_in_00_precious(transaction),
        "is_recurring_merchant_precious": is_recurring_merchant_precious(transaction),
        "n_transactions_same_merchant_amount_precious": get_n_transactions_same_merchant_amount_precious(
            transaction, all_transactions
        ),
        "percent_transactions_same_merchant_amount_precious": get_percent_transactions_same_merchant_amount_precious(
            transaction, all_transactions
        ),
        "avg_days_between_same_merchant_amount_precious": get_avg_days_between_same_merchant_amount_precious(
            transaction, all_transactions
        ),
        "stddev_days_between_same_merchant_amount_precious": get_stddev_days_between_same_merchant_amount_precious(
            transaction, all_transactions
        ),
        "days_since_last_same_merchant_amount_precious": get_days_since_last_same_merchant_amount_precious(
            transaction, all_transactions
        ),
        "recurring_frequency": get_recurring_frequency(transaction, all_transactions),
        "is_subscription_amount": is_subscription_amount(transaction),
        **get_additional_features(transaction, all_transactions),
        **get_amount_variation_features(transaction, all_transactions),
        # Happy's features
        "get_n_transactions_same_description": get_n_transactions_same_description(transaction, all_transactions),
        "get_percent_transactions_same_description": get_percent_transactions_same_description(
            transaction, all_transactions
        ),
        "get_transaction_same_frequency": get_transaction_frequency_happy(transaction, all_transactions),
        "get_day_of_month_consistency": get_day_of_month_consistency_happy(transaction, all_transactions),
        # Osasere's features
        "has_min_recurrence_period_osasere": has_min_recurrence_period(transaction, all_transactions),
        "day_of_month_consistency_osasere": get_day_of_month_consistency_osasere(transaction, all_transactions),
        "day_of_month_variability": get_day_of_month_variability(transaction, all_transactions),
        "recurrence_confidence": get_recurrence_confidence(transaction, all_transactions),
        "median_period_days": get_median_period(transaction, all_transactions),
        "is_weekday_consistent": is_weekday_consistent(transaction, all_transactions),
        # Felix's features
        "n_transactions_same_vendor": get_n_transactions_same_vendor(transaction, all_transactions),
        "max_transaction_amount_felix": get_max_transaction_amount_felix(all_transactions),
        "min_transaction_amount_felix": get_min_transaction_amount_felix(all_transactions),
        "is_phone_felix": get_is_phone_felix(transaction),
        "month": get_month(transaction),
        "day_felix": get_day_felix(transaction),
        "year": get_year(transaction),
        "is_insurance_felix": get_is_insurance_felix(transaction),
        "is_utility_felix": get_is_utility_felix(transaction),
        "is_always_recurring_felix": get_is_always_recurring_felix(transaction),
        "median_variation_transaction_amount": get_median_variation_transaction_amount(transaction, all_transactions),
        "variation_ratio": get_variation_ratio(transaction, all_transactions),
        "transactions_interval_stability": get_transactions_interval_stability(transaction, all_transactions),
        "average_transaction_amount_felix": get_average_transaction_amount_felix(transaction, all_transactions),
        "dispersion_transaction_amount_felix": get_dispersion_transaction_amount_felix(transaction, all_transactions),
        "transaction_rate": get_transaction_rate(transaction, all_transactions),
        **get_transaction_intervals_felix(all_transactions),
        # Adeyinka's features
        "avg_days_between_transactions_adeyinka": get_average_days_between_transactions(transaction, all_transactions),
        "time_regularity_score_adeyinka": get_time_regularity_score(transaction, all_transactions),
        "is_always_recurring_adeyinka": get_is_always_recurring_adeyinka(transaction),
        "transaction_amount_variance_adeyinka": get_transaction_amount_variance(transaction, all_transactions),
        "outlier_score_adeyinka": get_outlier_score(transaction, all_transactions),
        "recurring_confidence_score_adeyinka": get_recurring_confidence_score(transaction, all_transactions),
        "subscription_keyword_score_adeyinka": get_subscription_keyword_score(transaction),
        "same_amount_vendor_transactions_adeyinka": get_same_amount_vendor_transactions(transaction, all_transactions),
        "30_days_apart_exact_adeyinka": get_n_transactions_days_apart_adeyinka(transaction, all_transactions, 30, 0),
        "30_days_apart_off_by_1_adeyinka": get_n_transactions_days_apart_adeyinka(transaction, all_transactions, 30, 1),
        "14_days_apart_exact_adeyinka": get_n_transactions_days_apart_adeyinka(transaction, all_transactions, 14, 0),
        "14_days_apart_off_by_1_adeyinka": get_n_transactions_days_apart_adeyinka(transaction, all_transactions, 14, 1),
        "7_days_apart_exact_adeyinka": get_n_transactions_days_apart_adeyinka(transaction, all_transactions, 7, 0),
        "7_days_apart_off_by_1_adeyinka": get_n_transactions_days_apart_adeyinka(transaction, all_transactions, 7, 1),
        # Elliot's features
        "is_utility_elliot": is_utility_bill(transaction),
        "is_always_recurring_elliot": get_is_always_recurring_elliot(transaction),
        "is_auto_pay": is_auto_pay(transaction),
        "is_membership": is_membership(transaction),
        "is_near_same_amount": get_is_near_same_amount(transaction, all_transactions),
        "is_recurring_based_on_99": is_recurring_based_on_99(transaction, all_transactions),
        "transaction_similarity": get_transaction_similarity(transaction, all_transactions),
        "is_weekday_transaction": is_weekday_transaction(transaction),
        "is_split_transaction": is_split_transaction(transaction, all_transactions),
        "is_price_trending_5pct": is_price_trending(transaction, all_transactions, 5),
        "is_price_trending_10pct": is_price_trending(transaction, all_transactions, 10),
        # Freedom's features
        "day_of_week_freedom": get_day_of_week(transaction),
        "days_until_next_transaction": get_days_until_next_transaction(transaction, all_transactions),
        "periodicity_confidence_30d": get_periodicity_confidence(transaction, all_transactions, 30),
        "periodicity_confidence_7d": get_periodicity_confidence(transaction, all_transactions, 7),
        "recurrence_streak": get_recurrence_streak(transaction, all_transactions),
        # Tife's features
        "transaction_frequency_tife": get_transaction_frequency_tife(all_transactions),
        "interval_consistency": get_interval_consistency(all_transactions),
        "amount_variability": get_amount_variability(all_transactions),
        "amount_range": get_amount_range(all_transactions),
        "transaction_count": get_transaction_count(all_transactions),
        "interval_mode": get_interval_mode(all_transactions),
        "normalized_interval_consistency": get_normalized_interval_consistency(all_transactions),
        "days_since_last_same_amount": get_days_since_last_same_amount(transaction, all_transactions),
        "amount_relative_change": get_amount_relative_change(transaction, all_transactions),
        "merchant_name_frequency": get_merchant_name_frequency(transaction, all_transactions),
        "amount_stability_score_tife": get_amount_stability_score_tife(all_transactions),
        "dominant_interval_strength": get_dominant_interval_strength(all_transactions),
        "near_amount_consistency": get_near_amount_consistency(transaction, all_transactions),
        "merchant_amount_signature": get_merchant_amount_signature(transaction, all_transactions),
        "amount_cluster_count": get_amount_cluster_count(transaction, all_transactions),
        "transaction_density": get_transaction_density(all_transactions),
        "biweekly_interval": histogram["biweekly"],
        "monthly_interval": histogram["monthly"],
        # Bassey's features
        "is_subscription": get_is_subscription(transaction),
        "is_streaming_service": get_is_streaming_service(transaction),
        "is_gym_membership": get_is_gym_membership(transaction),
        # Raphael's features
        "same_day_exact_raphael": get_n_transactions_same_day_raphael(transaction, all_transactions, 0),
        "pct_transactions_same_day_raphael": get_pct_transactions_same_day_raphael(transaction, all_transactions, 0),
        "same_day_off_by_1_raphael": get_n_transactions_same_day_raphael(transaction, all_transactions, 1),
        "same_day_off_by_2_raphael": get_n_transactions_same_day_raphael(transaction, all_transactions, 2),
        "14_days_apart_exact_raphael": get_n_transactions_days_apart_raphael(transaction, all_transactions, 14, 0),
        "pct_14_days_apart_exact_raphael": get_pct_transactions_days_apart_raphael(
            transaction, all_transactions, 14, 0
        ),
        "14_days_apart_off_by_1_raphael": get_n_transactions_days_apart_raphael(transaction, all_transactions, 14, 1),
        "pct_14_days_apart_off_by_1_raphael": get_pct_transactions_days_apart_raphael(
            transaction, all_transactions, 14, 1
        ),
        "7_days_apart_exact_raphael": get_n_transactions_days_apart_raphael(transaction, all_transactions, 7, 0),
        "pct_7_days_apart_exact_raphael": get_pct_transactions_days_apart_raphael(transaction, all_transactions, 7, 0),
        "7_days_apart_off_by_1_raphael": get_n_transactions_days_apart_raphael(transaction, all_transactions, 7, 1),
        "pct_7_days_apart_off_by_1_raphael": get_pct_transactions_days_apart_raphael(
            transaction, all_transactions, 7, 1
        ),
        "is_common_subscription_amount": get_is_common_subscription_amount(transaction),
        "occurs_same_week": get_occurs_same_week(transaction, all_transactions),
        "is_similar_name": get_is_similar_name(transaction, all_transactions),
        "is_fixed_interval": get_is_fixed_interval(transaction, all_transactions),
        "has_irregular_spike": get_has_irregular_spike(transaction, all_transactions),
        "is_first_of_month": get_is_first_of_month(transaction),
        # Ernest's features
        "is_weekly": get_is_weekly(transaction, all_transactions),
        "is_monthly": get_is_monthly(transaction, all_transactions),
        "is_biweekly": get_is_biweekly(transaction, all_transactions),
        "vendor_transaction_count": get_vendor_transaction_count(transaction, all_transactions),
        "vendor_amount_variance": get_vendor_amount_variance(transaction, all_transactions),
        "is_round_amount": get_is_round_amount(transaction),
        "is_small_amount": get_is_small_amount(transaction),
        "transaction_gap_mean": get_transaction_gap_stats(transaction, all_transactions)[0],
        "transaction_frequency_ernest": get_transaction_frequency_ernest(transaction, all_transactions),
        "is_recurring_vendor": get_is_recurring_vendor(transaction),
        "is_fixed_amount": get_is_fixed_amount(transaction, all_transactions),
        "recurring_interval_score": get_recurring_interval_score(transaction, all_transactions),
        "is_weekend_transaction_ernest": get_is_weekend_transaction_ernest(transaction),
        "is_high_frequency_vendor": get_is_high_frequency_vendor(transaction, all_transactions),
        "is_same_day_of_month": get_is_same_day_of_month(transaction, all_transactions),
        "is_quarterly": get_is_quarterly(transaction, all_transactions),
        "average_transaction_amount_ernest": get_average_transaction_amount_ernest(transaction, all_transactions),
        "is_subscription_based": get_is_subscription_based(transaction),
        # Naomi's features
        "transaction_time_of_month": get_transaction_time_of_month(transaction),
        "transaction_amount_stability": get_transaction_amount_stability(transaction, all_transactions),
        "time_between_transactions": get_time_between_transactions(transaction, all_transactions),
        "transaction_frequency_naomi": get_transaction_frequency_naomi(transaction, all_transactions),
        "n_same_name_transactions": get_n_same_name_transactions(transaction, all_transactions),
        "irregular_periodicity": get_irregular_periodicity(transaction, all_transactions),
        "irregular_periodicity_with_tolerance": get_irregular_periodicity_with_tolerance(transaction, all_transactions),
        "user_transaction_frequency_naomi": get_user_transaction_frequency_naomi(transaction.user_id, all_transactions),
        "vendor_recurring_ratio": get_vendor_recurring_ratio(transaction, all_transactions),
        "vendor_recurrence_consistency": get_vendor_recurrence_consistency(transaction, all_transactions),
        # Adedotun's features
        "percent_transactions_same_amount_tolerant_at": get_percent_transactions_same_amount_tolerant(
            transaction, vendor_txns
        ),
        "is_always_recurring_at": get_is_always_recurring_at(transaction),
        "is_communication_or_energy_at": get_is_communication_or_energy_at(transaction),
        "is_recurring_monthly_at": is_recurring_core_at(transaction, vendor_txns, preprocessed, 30, 4, 2),
        "is_recurring_weekly_at": is_recurring_core_at(transaction, vendor_txns, preprocessed, 7, 2, 2),
        "is_recurring_user_vendor_at": is_recurring_core_at(transaction, user_vendor_txns, preprocessed, 30, 4, 2),
        "day_consistency": sum(1 for t in vendor_txns if abs(date_obj.day - preprocessed["date_objects"][t].day) <= 2)
        / total_txns
        if total_txns
        else 0.0,
        "amount_stability": (sum((t.amount - transaction.amount) ** 2 for t in vendor_txns) / total_txns) ** 0.5
        / transaction.amount
        if total_txns and transaction.amount
        else 0.0,
        "is_recurring_allowance_at": is_recurring_allowance_at(transaction, all_transactions, 30, 2, 2),
        # Segun's features
        "total_transaction_amount_segun": get_total_transaction_amount(all_transactions),
        "average_transaction_amount_segun": get_average_transaction_amount_segun(all_transactions),
        "max_transaction_amount_segun": get_max_transaction_amount_segun(all_transactions),
        "min_transaction_amount_segun": get_min_transaction_amount_segun(all_transactions),
        "transaction_amount_std_segun": get_transaction_amount_std(all_transactions),
        "transaction_amount_median_segun": get_transaction_amount_median(all_transactions),
        "transaction_amount_range_segun": get_transaction_amount_range_segun(all_transactions),
        "unique_transaction_amount_count": get_unique_transaction_amount_count(all_transactions),
        "transaction_amount_frequency": get_transaction_amount_frequency(transaction, all_transactions),
        "transaction_day_of_week_segun": get_transaction_day_of_week(transaction),
        "transaction_time_of_day": get_transaction_time_of_day(transaction),
        "average_transaction_interval": get_average_transaction_interval(all_transactions),
        # Victor's features
        "avg_days_between": get_avg_days_between(all_transactions),
main
    }
# def is_sub_company(): 
