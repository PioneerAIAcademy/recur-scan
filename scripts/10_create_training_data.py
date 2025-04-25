#!/usr/bin/env python
"""
Create training datasets for transaction labeling.

This script processes raw transaction data from Plaid and internal sources,
selecting accounts and distributing them to labelers in a balanced way.
Each account is assigned to multiple labelers to establish consensus.
"""

# %%
import argparse
import random
import sys

import pandas as pd
from loguru import logger

# %%
# configure script arguments

n_labelers = 40
n_repetitions = 3
n_accounts = 200  # must be a multiple of n_labelers
n_accounts_per_labeler = n_accounts // n_labelers * n_repetitions
min_transactions_per_account = 500
max_transactions_per_account = 4000
min_transactions_per_labeler = 16000
max_transactions_per_labeler = 24000

plaid_filename = "../../data/plaid.csv"
internal_filename = "../../data/internal.csv"
output_dir = "../../data/to_label"

# %%
# parse script arguments from command line

parser = argparse.ArgumentParser(description="Create training data for the labelers")
parser.add_argument("--f", help="used by ipykernel_launcher")
parser.add_argument("--plaid", type=str, default=plaid_filename, help="Plaid transactions file")
parser.add_argument("--internal", type=str, default=internal_filename, help="Internal transactions file")
args = parser.parse_args()
plaid_filename, internal_filename = args.plaid, args.internal

# %%
# load the plaid transactions
try:
    plaid_df = pd.read_csv(plaid_filename)
    logger.info(f"Loaded {len(plaid_df)} plaid transactions")
    logger.info(f"Sample transactions:\n{plaid_df.head(3)}")
except FileNotFoundError:
    logger.error(f"Plaid transactions file not found: {plaid_filename}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Error loading plaid transactions: {e}")
    sys.exit(1)

# %%
# count the number of empty cells in each column
for column in plaid_df.columns:
    n_empty = plaid_df[column].isna().sum()
    logger.info(f"{column}: {n_empty} empty cells")

# %%
# load the internal transactions
try:
    internal_df = pd.read_csv(internal_filename)
    logger.info(f"Loaded {len(internal_df)} internal transactions")
    logger.info(f"Sample transactions:\n{internal_df.head(3)}")
except FileNotFoundError:
    logger.error(f"Internal transactions file not found: {internal_filename}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Error loading internal transactions: {e}")
    sys.exit(1)

# %%
# count the number of empty cells in each column
for column in internal_df.columns:
    n_empty = internal_df[column].isna().sum()
    logger.info(f"{column}: {n_empty} empty cells")

# %%
# catenate the plaid and internal transactions

transactions_df = pd.concat([plaid_df, internal_df])
logger.info(f"Combined dataset contains {len(transactions_df)} transactions")

# %%
# select user_id,
#        merchant_name as name,
#        transaction_timestamp as date,
#        transaction_amount as amount

transactions_df = transactions_df[["user_id", "merchant_name", "transaction_timestamp", "transaction_amount"]]
# rename the columns
transactions_df = transactions_df.rename(
    columns={
        "user_id": "user_id",
        "merchant_name": "name",
        "transaction_timestamp": "date",
        "transaction_amount": "amount",
    }
)
# convert the date from various formats to YYYY-MM-DD
try:
    transactions_df["date"] = pd.to_datetime(transactions_df["date"], format="mixed", utc=True).dt.date.astype(str)
    logger.info(f"Sample of processed transactions:\n{transactions_df.head(3)}")
except Exception as e:
    logger.error(f"Error converting date format: {e}")
    sys.exit(1)

# %%
# drop the rows with empty cells
initial_count = len(transactions_df)
transactions_df = transactions_df.dropna()
dropped_count = initial_count - len(transactions_df)
logger.info(f"Dropped {dropped_count} rows with missing values. Remaining: {len(transactions_df)} transactions")

# %%
# create a dictionary of user_id to number of transactions
user_id_to_n_transactions = transactions_df["user_id"].value_counts().to_dict()
print(len(user_id_to_n_transactions))

# %%
# filter the users with less than min_transactions or more than max_transactions
user_ids = [
    user_id
    for user_id in user_id_to_n_transactions
    if user_id_to_n_transactions[user_id] >= min_transactions_per_account
    and user_id_to_n_transactions[user_id] <= max_transactions_per_account
]
print(len(user_ids))

# %%
# select n_accounts random users

selected_user_ids = random.sample(user_ids, n_accounts)
print(len(selected_user_ids))

# %%
# count the total number of transactions for the selected user_ids
total_transactions = sum(user_id_to_n_transactions[uid] for uid in selected_user_ids)
print(total_transactions, total_transactions / n_accounts, total_transactions / n_labelers * n_repetitions)

# %%
# we have n_labelers labelers, and each labeler will label n_accounts_per_labeler accounts
# randomly assign the user_ids to labelers
# under the constraint that each labeler gets n_accounts_per_labeler
# each user_id should be assigned to exactly n_repetitions labelers
# and the total number of transactions for the accounts assigned to a labeler should be between
# min_transactions_per_labeler and max_transactions_per_labeler

constraints_satisfied = False
while not constraints_satisfied:
    # Initialize dictionaries and sets
    user_id_to_labelers: dict[str, list[int]] = {user_id: [] for user_id in selected_user_ids}
    labeler_to_user_ids: dict[int, list[str]] = {i: [] for i in range(n_labelers)}

    # For each labeler
    for labeler in range(n_labelers):
        # randomly select n_accounts_per_labeler user_ids from the selectable set
        # but prefer to select user_ids that have been assigned to the least number of labelers
        candidate_user_ids: list[str] = []
        for repetition in range(n_repetitions):
            available_user_ids = [uid for uid in selected_user_ids if len(user_id_to_labelers[uid]) == repetition]
            select_count = min(n_accounts_per_labeler - len(candidate_user_ids), len(available_user_ids))
            candidate_user_ids.extend(random.sample(available_user_ids, select_count))
            if len(candidate_user_ids) == n_accounts_per_labeler:
                break
        # add the total number of transactions for the accounts assigned to this labeler
        total_transactions = sum(user_id_to_n_transactions[uid] for uid in candidate_user_ids)
        # add the user_ids to the labeler's list
        labeler_to_user_ids[labeler] = candidate_user_ids
        # add the labeler to the user_ids's list
        for uid in candidate_user_ids:
            user_id_to_labelers[uid].append(labeler)
    # check if the total number of transactions is between min_transactions and max_transactions
    constraints_satisfied = True
    for labeler in range(n_labelers):
        total_transactions = sum(user_id_to_n_transactions[uid] for uid in labeler_to_user_ids[labeler])
        if total_transactions < min_transactions_per_labeler or total_transactions > max_transactions_per_labeler:
            constraints_satisfied = False
            print(f"labeler {labeler} has {total_transactions} transactions")
            break
    # check if each user_id is assigned to n_repetitions labelers
    for user_id in selected_user_ids:
        if len(user_id_to_labelers[user_id]) != n_repetitions:
            constraints_satisfied = False
            print(f"user_id {user_id} is assigned to {len(user_id_to_labelers[user_id])} labelers")
            break
    # check if each labeler has n_accounts_per_labeler user_ids
    for labeler in range(n_labelers):
        if len(labeler_to_user_ids[labeler]) != n_accounts_per_labeler:
            constraints_satisfied = False
            print(f"labeler {labeler} has {len(labeler_to_user_ids[labeler])} user_ids")
            break
print("constraints satisfied")


# %%
# print the number of transactions for each labeler

for labeler in range(n_labelers):
    print(f"{labeler} has {sum(user_id_to_n_transactions[uid] for uid in labeler_to_user_ids[labeler])} transactions")

# %%
# create files for each labeler containing the transactions for the accounts assigned to the labeler

for labeler in range(n_labelers):
    # get transactions for this labeler's assigned user_ids
    labeler_df = transactions_df[transactions_df["user_id"].isin(labeler_to_user_ids[labeler])]
    # sort by user_id, name, date, amount
    labeler_df = labeler_df.sort_values(["user_id", "name", "date", "amount"])
    # save the dataframe to a csv file
    labeler_df.to_csv(f"{output_dir}/labeler_{labeler}.csv", index=False)

# %%
