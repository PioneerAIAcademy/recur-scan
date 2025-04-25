#!/usr/bin/env python
"""
Gather questionable labels from transaction data.

This script analyzes labeled transaction data to identify transactions where
labelers have marked with a '?' indicating uncertainty. These transactions
are collected for further review and analysis to improve model quality.
"""

# %%
import os
from collections import defaultdict
from datetime import date
from typing import Any

import pandas as pd
from loguru import logger

# %%

input_dir = "../../data/in_process"
output_dir = "../../data/questions"

# %%
# read all the files in the input directory

files: list[str] = os.listdir(input_dir)
logger.info(f"Found {len(files)} files in {input_dir}")

# %%
# identify the questions in each file

questions: dict[str, list[tuple[str, float, str]]] = {}
for file in files:
    # print the filename and the number of labels
    logger.info(f"Processing {file}")
    # First try reading without specifying dtype for amount to see which rows fail conversion (if any)
    df: pd.DataFrame | None = None
    try:
        df = pd.read_csv(os.path.join(input_dir, file))
        # Now attempt to convert amount column to float to find problematic row
        pd.to_numeric(df["amount"], errors="raise")
    except ValueError as e:
        logger.error(f"Error converting amount to float in file {file}:")
        logger.error(e)
        # Get the problematic rows
        if df is not None:
            mask = pd.to_numeric(df["amount"], errors="coerce").isna()
            logger.error("\nProblematic rows:")
            logger.error(df[mask])

    # Now read with proper dtypes
    df = pd.read_csv(
        os.path.join(input_dir, file),
        dtype={"user_id": str, "name": str, "date": str, "amount": float, "recurring": str},
    )
    # create a dictionary whose key is "user_id/name" and whose value is a list of (amount, recurring) tuples
    labels: dict[str, list[tuple[str, float, str]]] = defaultdict(list)
    for _, row in df.iterrows():
        user_id: str = row["user_id"]
        name: str = row["name"]
        _date: str = row["date"]
        amount: float = row["amount"]
        recurring: str = row["recurring"].strip() if pd.notna(row["recurring"]) else ""
        labels[f"{user_id}/{name}"].append((_date, amount, recurring))
    # keep only the labels where at least one of the recurring values is a '?'
    labels = {k: v for k, v in labels.items() if any(recurring == "?" for _, _, recurring in v)}
    # add the labels to the questions dictionary
    questions.update(labels)
    # print the filename and the number of labels
    logger.info(f"Found {len(labels)} labels in {file}")
# print the number of keys in the questions dictionary and the total number of labels
logger.info(f"Found {len(questions)} keys in the questions dict and {sum(len(v) for v in questions.values())} labels")

# %%
# save the questions to a dataframe where the (date, amount, recurring) tuples are in separate columns,

# only save each name once
seen_names: set[str] = set()
# Create list of rows with user_id, name, date, amount, recurring
rows: list[dict[str, Any]] = []
for key, tuples in questions.items():
    user_id, name = key.split("/", maxsplit=1)
    if name in seen_names:
        continue
    seen_names.add(name)
    for _date, amount, recurring in tuples:
        rows.append({"user_id": user_id, "name": name, "date": _date, "amount": amount, "recurring": recurring})
df = pd.DataFrame(rows)

# %%
# save the dataframe to a csv file

today = date.today().strftime("%Y-%m-%d")
df.to_csv(os.path.join(output_dir, f"{today}.csv"), index=False)

# %%
