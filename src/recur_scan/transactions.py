import csv
from collections import defaultdict
from dataclasses import asdict, dataclass, fields

from loguru import logger


@dataclass(frozen=True)
class Transaction:
    id: int  # unique identifier
    user_id: str  # user id
    name: str  # vendor name
    date: str  # date of the transaction
    amount: float  # amount of the transaction


# Create a type alias for grouped transactions that maps a tuple of (user_id, name) to a list of transactions
type GroupedTransactions = dict[tuple[str, str], list[Transaction]]


def _parse_transactions(
    path: str, extract_labels: bool = False, set_id: bool = True, raw_labels: bool = False
) -> tuple[list[Transaction], list[str | int]]:
    """
    Parse transactions from a CSV file, optionally extracting labels.
    """
    transactions = []
    labels = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for ix, row in enumerate(reader):
            try:
                transactions.append(
                    Transaction(
                        id=ix if set_id else 0,
                        user_id=row["user_id"],
                        name=row["name"],
                        date=row["date"],
                        amount=float(row["amount"]),
                    )
                )
            except ValueError as e:
                logger.warning(f"Error parsing transaction amount {row['amount']} in {path} at row {ix}: {e}")
                continue
            if extract_labels:
                label = row["recurring"].strip()
                if raw_labels:
                    labels.append(label if len(label) > 0 else "0")
                else:
                    labels.append(1 if label == "1" else 0)

    return transactions, labels


def read_labeled_transactions(
    path: str, set_id: bool = True, raw_labels: bool = False
) -> tuple[list[Transaction], list[str | int]]:
    """
    Read labeled transactions from a CSV file.
    """
    transactions, labels = _parse_transactions(path, extract_labels=True, set_id=set_id, raw_labels=raw_labels)
    return transactions, labels


def read_unlabeled_transactions(path: str) -> list[Transaction]:
    """
    Read unlabeled transactions from a CSV file.
    """
    transactions, _ = _parse_transactions(path)
    return transactions


def group_transactions(transactions: list[Transaction]) -> GroupedTransactions:
    """
    Group transactions by user_id and name.
    """
    grouped_transactions = defaultdict(list)
    for transaction in transactions:
        grouped_transactions[(transaction.user_id, transaction.name)].append(transaction)
    return dict(grouped_transactions)


def write_transactions(output_path: str, transactions: list[Transaction], y: list[int | str]) -> None:
    """
    Save transactions to a CSV file.

    Args:
        output_path: Path to save the CSV file
        misclassified_transactions: List of Transaction objects
        y: List of true labels
    """
    with open(output_path, "w", newline="") as f:
        if transactions:
            # Get all fields from the Transaction dataclass plus the label
            fieldnames = [field.name for field in fields(Transaction)]
            fieldnames.extend(["recurring"])
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for transaction in transactions:
                # convert transaction to dictionary using asdict()
                row = asdict(transaction)
                row["recurring"] = y[transaction.id]
                writer.writerow(row)
