import numpy as np

from recur_scan.transactions import Transaction
from recur_scan.utils import parse_date


def get_is_always_recurring(transaction: Transaction) -> bool:
    """Check if the transaction is always recurring because of the vendor name - check lowercase match"""
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
    return sum(1 for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip())


def get_amount_std_dev(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    amounts = [t.amount for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()]
    return float(np.std(amounts, ddof=0)) if amounts else 0.0


def get_median_transaction_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    amounts = [t.amount for t in all_transactions if t.name.lower().strip() == transaction.name.lower().strip()]
    return float(np.median(amounts)) if amounts else 0.0


def get_is_weekend_transaction(transaction: Transaction) -> bool:
    return parse_date(transaction.date).weekday() >= 5
