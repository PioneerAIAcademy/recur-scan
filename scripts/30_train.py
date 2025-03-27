#!/usr/bin/env python
"""
Train a model to identify recurring transactions.

This script extracts features from transaction data and trains a machine learning
model to predict which transactions are recurring. It uses the feature extraction
module from recur_scan.features to prepare the input data.
"""

# %%
import argparse
import json
import os

import joblib
from loguru import logger
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold

from recur_scan.features import get_features
from recur_scan.transactions import group_transactions, read_labeled_transactions, write_transactions

# %%
# configure the script

n_cv_folds = 3  # number of cross-validation folds, could be 5
n_hpo_iters = 20  # number of hyperparameter optimization iterations

in_path = "your csv file goes here"
out_dir = "your output directory goes here"

# %%
# parse script arguments from command line
parser = argparse.ArgumentParser(description="Train a model to identify recurring transactions.")
parser.add_argument("--f", help="ignore; used by ipykernel_launcher")
parser.add_argument("--input", type=str, default=in_path, help="Path to the input CSV file containing transactions.")
parser.add_argument("--output", type=str, default=out_dir, help="Path to the output directory.")
args = parser.parse_args()
in_path = args.input
out_dir = args.output

# Create output directory if it doesn't exist
os.makedirs(out_dir, exist_ok=True)

# %%
#
# LOAD AND PREPARE THE DATA
#

# read labeled transactions

transactions, y = read_labeled_transactions(in_path)
logger.info(f"Read {len(transactions)} transactions with {len(y)} labels")

# %%
# group transactions by user_id and name

grouped_transactions = group_transactions(transactions)
logger.info(f"Grouped {len(transactions)} transactions into {len(grouped_transactions)} groups")
# %%
# get features

features = [
    get_features(transaction, grouped_transactions[(transaction.user_id, transaction.name)])
    for transaction in transactions
]

# convert features to a matrix for machine learning
X = DictVectorizer(sparse=False).fit_transform(features)
logger.info(f"Converted {len(features)} features into a {X.shape} matrix")

# %%
#
# HYPERPARAMETER OPTIMIZATION
#

# Define parameter grid
param_dist = {
    "n_estimators": [100, 200, 500, 1000],
    "max_depth": [10, 20, 30, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "max_features": ["sqrt", "log2", None],
    "bootstrap": [True, False],
}

# Random search
model = RandomForestClassifier(random_state=42)
random_search = RandomizedSearchCV(
    model, param_dist, n_iter=n_hpo_iters, cv=n_cv_folds, scoring="f1", n_jobs=-1, verbose=1
)
random_search.fit(X, y)

print("Best Hyperparameters:")
for param, value in random_search.best_params_.items():
    print(f"  {param}: {value}")

best_params = random_search.best_params_

# consider setting the best params yourself someday instead of using the random search
# best_params = {
#     "n_estimators": 500,
#     "min_samples_split": 5,
#     "min_samples_leaf": 2,
#     "max_features": None,
#     "max_depth": 20,
#     "bootstrap": False,
# }

# %%
#
# TRAIN THE MODEL
#

# now that we have the best hyperparameters, train a model with them

model = RandomForestClassifier(random_state=42, **best_params)
model.fit(X, y)

# %%
# save the model using joblib
joblib.dump(model, os.path.join(out_dir, "model.joblib"))
# save the best params to a json file
with open(os.path.join(out_dir, "best_params.json"), "w") as f:
    json.dump(best_params, f)

# %%
#
# PREDICT ON THE TRAINING DATA
#

y_pred = model.predict(X)

# %%
#
# EVALUATE THE PREDICTIONS
#

# calculate the precision, recall, and f1 score for the positive class

precision = precision_score(y, y_pred)
recall = recall_score(y, y_pred)
f1 = f1_score(y, y_pred)

print(f"Precision: {precision}")
print(f"Recall: {recall}")
print("Confusion Matrix:")

print("                Predicted Non-Recurring  Predicted Recurring")
print("Actual Non-Recurring", end="")
cm = confusion_matrix(y, y_pred)
print(f"     {cm[0][0]:<20} {cm[0][1]}")
print("Actual Recurring    ", end="")
print(f"     {cm[1][0]:<20} {cm[1][1]}")


# %%
# get the misclassified transactions

misclassified = [transactions[i] for i, yp in enumerate(y_pred) if yp != y[i]]
logger.info(f"Found {len(misclassified)} misclassified transactions (bias error)")

# save the misclassified transactions to a csv file in the output directory
write_transactions(os.path.join(out_dir, "bias_errors.csv"), misclassified, y)

# %%
#
# USE CROSS-VALIDATION TO GET THE VARIANCE ERRORS
#

kf = StratifiedKFold(n_splits=n_cv_folds, shuffle=True, random_state=42)
misclassified = []
precisions = []
recalls = []
f1s = []

for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
    logger.info(f"Fold {fold + 1} of {n_cv_folds}")
    # Get training and validation data
    X_train = [X[i] for i in train_idx]  # type: ignore
    X_val = [X[i] for i in val_idx]  # type: ignore
    y_train = [y[i] for i in train_idx]
    y_val = [y[i] for i in val_idx]
    transactions_val = [transactions[i] for i in val_idx]  # Keep the original transaction instances for this fold

    # Train the model
    model = RandomForestClassifier(random_state=42, **best_params)
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_val)

    # Find misclassified instances
    misclassified_fold = [transactions_val[i] for i in range(len(y_val)) if y_val[i] != y_pred[i]]
    misclassified.extend(misclassified_fold)

    # Report recall, precision, and f1 score
    precision = precision_score(y_val, y_pred)
    recall = recall_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred)
    precisions.append(precision)
    recalls.append(recall)
    f1s.append(f1)
    print(f"Fold {fold + 1} Precision: {precision:.2f}, Recall: {recall:.2f}, F1 Score: {f1:.2f}")
    print(f"Misclassified Instances in Fold {fold + 1}: {len(misclassified_fold)}")

# print the average precision, recall, and f1 score for all folds
print(f"\nAverage Metrics Across {n_cv_folds} Folds:")
print(f"Precision: {sum(precisions) / len(precisions):.2f}")
print(f"Recall: {sum(recalls) / len(recalls):.2f}")
print(f"F1 Score: {sum(f1s) / len(f1s):.2f}")

# %%
# save the misclassified transactions to a csv file in the output directory

logger.info(f"Found {len(misclassified)} misclassified transactions (variance errors)")

write_transactions(os.path.join(out_dir, "variance_errors.csv"), misclassified, y)

# %%
