#!/usr/bin/env python
"""
This script merges the labeled transactions from multiple labelers into a single
file with the consensus label and splits the transactions into train and test sets.
"""

# %%
# import dependencies
import csv
import os
import random
from collections import defaultdict

import matplotlib.pyplot as plt
from loguru import logger

from recur_scan.metrics import LabelerMetrics
from recur_scan.transactions import Transaction, read_labeled_transactions

# %%
# configure

min_vote_threshold = 1.8
train_ratio = 0.65

in_dir = "../../data/labeled"
train_path = "../../data/train.csv"
test_path = "../../data/test.csv"

# %%
# read the labeled transactions from each file in in_dir

transactions = []
labels = []
labelers = []
for path in os.listdir(in_dir):
    logger.info(f"Reading {path}")
    labeler = path.split(".")[0].split("-")[0]
    # set id's to 0 so transactions from different files get merged; use raw_labels so we don't convert the labels
    txs, ls = read_labeled_transactions(os.path.join(in_dir, path), set_id=False, raw_labels=True)
    logger.info(f"   read {len(txs)} transactions")
    transactions.extend(txs)
    labels.extend(ls)
    labelers.extend([labeler] * len(txs))
logger.info(f"Read {len(transactions)} transactions from {len(set(labelers))} labelers")
logger.info(f"Labelers: {set(labelers)}")

# %%
# gather the transactions into votes

tx_votes: dict[Transaction, dict[str, str]] = defaultdict(dict)
for tx, label, labeler in zip(transactions, labels, labelers, strict=True):
    tx_votes[tx][labeler] = str(label)
logger.info(f"Gathered {len(tx_votes)} unique transactions into votes")

# %%
# remove all votes with less than 3 votes that are 0 or 1

tx_votes = {
    tx: votes
    for tx, votes in tx_votes.items()
    if len([vote for vote in votes.values() if vote == "0" or vote == "1"]) >= 3
}
logger.info(f"Removed transactions with less than 3 (0 or 1) votes; {len(tx_votes)} transactions remaining")

# %%
# calculate labeler metrics


def get_majority_vote_and_score(votes: dict[str, str], labeler_metrics: dict[str, LabelerMetrics]) -> tuple[str, float]:
    """majority vote = the vote with the highest sum of labeler_metrics.score for the labelers who voted for the vote"""
    vote_scores = {
        vote: sum(labeler_metrics[labeler].score for labeler in votes if votes[labeler] == vote) for vote in ["0", "1"]
    }
    majority_vote = max(vote_scores, key=lambda k: vote_scores.get(k, 0))
    return majority_vote, vote_scores[majority_vote]


# initialize metrics for each labeler
labeler_metrics = {}
for labeler in set(labelers):
    labeler_metrics[labeler] = LabelerMetrics(
        fp=0,
        fn=0,
        tp=0,
        tn=0,
        precision=0,
        recall=0,
        score=1.0,
    )

# Loop through this process several times to ensure that the metrics are stable
for ix in range(5):
    logger.info(f"Calculating metrics: {ix}")
    # reset tp, fp, fn, and tn for each labeler
    for labeler in set(labelers):
        labeler_metrics[labeler].tp = 0
        labeler_metrics[labeler].fp = 0
        labeler_metrics[labeler].fn = 0
        labeler_metrics[labeler].tn = 0

    # calculate tp, fp, fn, and tn for each labeler
    for votes in tx_votes.values():
        majority_vote, _ = get_majority_vote_and_score(votes, labeler_metrics)
        for labeler, vote in votes.items():
            if majority_vote == "1":
                if vote == "1":
                    labeler_metrics[labeler].tp += 1
                else:
                    labeler_metrics[labeler].fn += 1
            else:
                if vote == "0":
                    labeler_metrics[labeler].tn += 1
                else:
                    labeler_metrics[labeler].fp += 1

    # calculate precision, recall, and f1 score for each labeler
    for labeler in labeler_metrics:
        labeler_metrics[labeler].precision = labeler_metrics[labeler].tp / (
            labeler_metrics[labeler].tp + labeler_metrics[labeler].fp
        )
        labeler_metrics[labeler].recall = labeler_metrics[labeler].tp / (
            labeler_metrics[labeler].tp + labeler_metrics[labeler].fn
        )
        labeler_metrics[labeler].score = (
            2
            * labeler_metrics[labeler].precision
            * labeler_metrics[labeler].recall
            / (labeler_metrics[labeler].precision + labeler_metrics[labeler].recall)
        )

    # print the metrics for each labeler sorted by score
    print("Labeler metrics:")
    for labeler, metrics in sorted(labeler_metrics.items(), key=lambda x: x[1].score, reverse=True):
        print(f"Labeler {labeler} p:{metrics.precision:.2f}, r:{metrics.recall:.2f}, s:{metrics.score:.2f}")

# %%
# get the score of the majority vote for each transaction and graph the distribution

majority_vote_scores = []
for votes in tx_votes.values():
    majority_vote, majority_vote_score = get_majority_vote_and_score(votes, labeler_metrics)
    majority_vote_scores.append(majority_vote_score)

plt.hist(majority_vote_scores, bins=20)
plt.show()

# %%
# consensus transactions have a majority vote score greater than or equal to min_vote_threshold

consensus_txs = []
consensus_labels = []
for tx, votes in tx_votes.items():
    majority_vote, majority_vote_score = get_majority_vote_and_score(votes, labeler_metrics)
    if majority_vote_score >= min_vote_threshold:
        consensus_txs.append(tx)
        consensus_labels.append(majority_vote)
logger.info(f"Consensus transactions: {len(consensus_txs)}")

# %%
# split the transactions into train and test based on user_id

user_ids = {tx.user_id for tx in consensus_txs}

train_user_ids = set(random.sample(list(user_ids), int(len(user_ids) * train_ratio)))
test_user_ids = set(user_ids) - train_user_ids

logger.info(f"Train user ids: {len(train_user_ids)}, Test user ids: {len(test_user_ids)}")

train_rows = []
test_rows = []
for tx, label in zip(consensus_txs, consensus_labels, strict=True):
    row = {
        "user_id": tx.user_id,
        "name": tx.name,
        "date": tx.date,
        "amount": tx.amount,
        "recurring": label,
    }
    if tx.user_id in train_user_ids:
        train_rows.append(row)
    else:
        test_rows.append(row)

logger.info(f"Train rows: {len(train_rows)}, Test rows: {len(test_rows)}")

# %%
# sort the train and test rows by user_id, then name, then date

# When sorting with a tuple key, Python compares elements in order:
# First compares user_id, if equal then compares name, if equal then compares date
train_rows.sort(key=lambda x: (x["user_id"], x["name"], x["date"]))
test_rows.sort(key=lambda x: (x["user_id"], x["name"], x["date"]))

# %%
# write the train and test rows to csv: user_id, name, date, amount, recurring

with open(train_path, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["user_id", "name", "date", "amount", "recurring"])
    for row in train_rows:
        writer.writerow([row["user_id"], row["name"], row["date"], row["amount"], row["recurring"]])

with open(test_path, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["user_id", "name", "date", "amount", "recurring"])
    for row in test_rows:
        writer.writerow([row["user_id"], row["name"], row["date"], row["amount"], row["recurring"]])

# %%
