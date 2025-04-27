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
from collections import defaultdict

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import shap
import xgboost as xgb
from loguru import logger
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import RFECV
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import GridSearchCV, GroupKFold, RandomizedSearchCV, train_test_split
from tqdm import tqdm

from recur_scan.features import get_features
from recur_scan.features_victor import get_new_features
from recur_scan.transactions import (
    group_transactions,
    read_labeled_transactions,
    write_labeled_transactions,
    write_transactions,
)

# %%
# configure the script

use_precomputed_features = True
model_type = "xgb"  # "rf" or "xgb"
n_cv_folds = 5  # number of cross-validation folds, could be 5
do_hyperparameter_optimization = False  # set to False to use the default hyperparameters
search_type = "random"  # "grid" or "random"
n_hpo_iters = 200  # number of hyperparameter optimization iterations
n_jobs = -1  # number of jobs to run in parallel (set to 1 if your laptop gets too hot)

in_path = "train_features.csv"
precomputed_features_path = "../../data/train_features.csv"
out_dir = "train_features.csv.gz"

# %%
# parse script arguments from command line
parser = argparse.ArgumentParser(description="Train a model to identify recurring transactions.")
parser.add_argument("--f", help="ignore; used by ipykernel_launcher")
parser.add_argument("--input", type=str, default=in_path, help="Path to the input CSV file containing transactions.")
parser.add_argument(
    "--use_precomputed_features",
    type=bool,
    default=use_precomputed_features,
    help="Use precomputed features instead of generating them from the input file.",
)
parser.add_argument(
    "--precomputed_features",
    type=str,
    default=precomputed_features_path,
    help="Path to the precomputed features CSV file.",
)
parser.add_argument("--output", type=str, default=out_dir, help="Path to the output directory.")
args = parser.parse_args()
in_path = args.input
use_precomputed_features = args.use_precomputed_features
precomputed_features_path = args.precomputed_features
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

user_ids = [transaction.user_id for transaction in transactions]

# %%
# get features

logger.info("Getting features")

if use_precomputed_features:
    # read the precomputed features
    features = pd.read_csv(precomputed_features_path).to_dict(orient="records")
    logger.info(f"Read {len(features)} precomputed features")
else:
    # feature generation is parallelized using joblib
    # Use backend that works better with shared memory
    with joblib.parallel_backend("loky", n_jobs=n_jobs):
        features = joblib.Parallel(verbose=1)(
            joblib.delayed(get_features)(transaction, grouped_transactions[(transaction.user_id, transaction.name)])
            for transaction in tqdm(transactions, desc="Processing transactions")
        )
    # save the features to a csv file
    pd.DataFrame(features).to_csv(precomputed_features_path, index=False)
    logger.info(f"Generated {len(features)} features")

# %%
# add new features
new_features = [
    get_new_features(
        grouped_transactions[(transaction.user_id, transaction.name)],  # all transactions for this user/vendor
        {},  # merchant scores (empty for now unless you have real scores)
        transaction,  # current transaction
    )
    for transaction in tqdm(transactions, desc="Processing transactions")
]


# add the new features to the existing features
for i, new_transaction_features in enumerate(new_features):
    features[i].update(new_transaction_features)  # type: ignore
logger.info(f"Added {len(new_features[0])} new features")

# %%
# convert all features to a matrix for machine learning
dict_vectorizer = DictVectorizer(sparse=False)
X = dict_vectorizer.fit_transform(features)
feature_names = dict_vectorizer.get_feature_names_out()  # Get feature names from the vectorizer
logger.info(f"Converted {len(features)} features into a {X.shape} matrix")


# %%
#
# HYPERPARAMETER OPTIMIZATION
#

# select the features tu use for hyperparameter optimizatino
# (we can uncomment the following line to use the selected features)

# X_hpo = X[:, selected_features]  # type: ignore
X_hpo = X
print(X_hpo.shape)

# %%

if do_hyperparameter_optimization:
    # Define parameter grid
    if model_type == "rf":
        param_dist = {
            "n_estimators": [200, 300, 400, 500],  # [10, 20, 50, 100, 200, 500, 1000],
            "max_depth": [20, 30, 40, 50],  # [10, 20, 30, 40, 50, None],
            "min_samples_split": [5],  # [2, 5, 10],
            "min_samples_leaf": [8],  # [1, 2, 4, 8, 16],
            "max_features": ["sqrt"],
            "bootstrap": [False],
        }
    elif model_type == "xgb":
        param_dist = {
            "scale_pos_weight": [24, 26, 28],  # Adjust based on class imbalance
            "max_depth": [5, 6, 7, 8, 9, 10],
            "learning_rate": [0.01, 0.025, 0.05, 0.1],
            "n_estimators": [600, 700, 800, 900, 1000],
            "min_child_weight": [1, 3, 5],
        }
    # search for the best hyperparameters
    if model_type == "rf":
        model = RandomForestClassifier(random_state=42, n_jobs=n_jobs)
    elif model_type == "xgb":
        model = xgb.XGBClassifier(random_state=42, n_jobs=n_jobs)

    cv = GroupKFold(n_splits=n_cv_folds)
    if search_type == "grid":
        search = GridSearchCV(model, param_dist, cv=cv, scoring="f1", n_jobs=n_jobs, verbose=3)
    else:
        search = RandomizedSearchCV(
            model, param_dist, n_iter=n_hpo_iters, cv=cv, scoring="f1", n_jobs=n_jobs, verbose=3
        )
    print(f"Searching for best hyperparameters for {model_type} with {search_type} search")
    search.fit(X_hpo, y, groups=user_ids)
    logger.info(f"Best F1 score: {search.best_score_}")

    print("Best Hyperparameters:")
    for param, value in search.best_params_.items():
        print(f"  {param}: {value}")

    best_params = search.best_params_
else:
    # default hyperparameters
    if model_type == "rf":
        best_params = {
            "n_estimators": 500,
            "min_samples_split": 5,
            "min_samples_leaf": 8,
            "max_features": "sqrt",
            "max_depth": 40,
            "bootstrap": False,
        }
    elif model_type == "xgb":
        best_params = {
            "scale_pos_weight": 24,
            "max_depth": 8,
            "learning_rate": 0.1,
            "n_estimators": 600,
            "min_child_weight": 1,
        }

# %%
#
# TRAIN THE MODEL
#

# now that we have the best hyperparameters, train a model with them

logger.info(f"Training the {model_type} model with {best_params}")
if model_type == "rf":
    model = RandomForestClassifier(random_state=42, **best_params, n_jobs=n_jobs)
elif model_type == "xgb":
    model = xgb.XGBClassifier(random_state=42, **best_params, n_jobs=n_jobs)
model.fit(X, y)
logger.info("Model trained")

# %%
# review feature importances

importances = model.feature_importances_

# sort the importances
sorted_importances = sorted(zip(importances, feature_names, strict=True), key=lambda x: x[0], reverse=True)

# print the features and their importances
for importance, feature in sorted_importances:
    print(f"{feature}: {importance}")

# %%
# save the model using joblib

logger.info(f"Saving the {model_type} model to {out_dir}")
joblib.dump(model, os.path.join(out_dir, "model.joblib"))
# save the dict vectorizer as well
joblib.dump(dict_vectorizer, os.path.join(out_dir, "dict_vectorizer.joblib"))
# save the best params to a json file
with open(os.path.join(out_dir, "best_params.json"), "w") as f:
    json.dump(best_params, f)
logger.info(f"Model saved to {out_dir}")

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
print(f"F1 Score: {f1}")
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

# select the features tu use for cross-validation
# (we can uncomment the following line to use the selected features)

# X_cv = X[:, selected_features]
X_cv = X
print(X_cv.shape)

# %%

cv = GroupKFold(n_splits=n_cv_folds)

misclassified = []
false_positives = set()
false_negatives = set()
precisions = []
recalls = []
f1s = []

logger.info(f"Starting cross-validation with {n_cv_folds} folds and {best_params}")
for fold, (train_idx, val_idx) in enumerate(cv.split(X_cv, y, groups=user_ids)):
    logger.info(f"Fold {fold + 1} of {n_cv_folds}")
    # Get training and validation data
    X_train = [X_cv[i] for i in train_idx]  # type: ignore
    X_val = [X_cv[i] for i in val_idx]  # type: ignore
    y_train = [y[i] for i in train_idx]  # type: ignore
    y_val = [y[i] for i in val_idx]  # type: ignore
    transactions_val = [transactions[i] for i in val_idx]  # Keep the original transaction instances for this fold

    # Train the model
    if model_type == "rf":
        model = RandomForestClassifier(random_state=42, **best_params, n_jobs=n_jobs)
    elif model_type == "xgb":
        model = xgb.XGBClassifier(random_state=42, **best_params, n_jobs=n_jobs)
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_val)

    # Find misclassified instances
    misclassified_fold = [transactions_val[i] for i in range(len(y_val)) if y_val[i] != y_pred[i]]
    misclassified.extend(misclassified_fold)

    # track false positives and false negatives
    false_positives.update([transactions_val[i] for i in range(len(y_val)) if y_val[i] != y_pred[i] and y_val[i] == 0])
    false_negatives.update([transactions_val[i] for i in range(len(y_val)) if y_val[i] != y_pred[i] and y_val[i] == 1])

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
print(f"Model type: {model_type}")
print(f"\nAverage Metrics Across {n_cv_folds} Folds:")
print(f"Precision: {sum(precisions) / len(precisions):.3f}")
print(f"Recall: {sum(recalls) / len(recalls):.3f}")
print(f"F1 Score: {sum(f1s) / len(f1s):.3f}")

# %%
# save the misclassified transactions to a csv file in the output directory

logger.info(f"Found {len(misclassified)} misclassified transactions (variance errors)")

write_transactions(os.path.join(out_dir, "variance_errors.csv"), misclassified, y)

# %%
# count false positives and false negatives

print(f"False positives: {len(false_positives)}")
print(f"False negatives: {len(false_negatives)}")

# %%
# count the number of misclassified transactions by transaction.name

# print the misclassified transactions by name
print("Misclassified transactions by name:")
misclassified_by_name: dict[str, int] = defaultdict(int)
for transaction in misclassified:
    misclassified_by_name[transaction.name] += 1
for name, count in sorted(misclassified_by_name.items(), key=lambda x: x[1], reverse=True):
    print(f"{name}: {count}")

# print the false positives and false negatives by name
print("\nFalse positives by name:")
false_positives_by_name: dict[str, int] = defaultdict(int)
for transaction in false_positives:
    false_positives_by_name[transaction.name] += 1
for name, count in sorted(false_positives_by_name.items(), key=lambda x: x[1], reverse=True):
    print(f"{name}: {count}")

print("\nFalse negatives by name:")
false_negatives_by_name: dict[str, int] = defaultdict(int)
for transaction in false_negatives:
    false_negatives_by_name[transaction.name] += 1
for name, count in sorted(false_negatives_by_name.items(), key=lambda x: x[1], reverse=True):
    print(f"{name}: {count}")

# %%
# for each user_id, name pair in misclassified transactions,
# save all of the transactions with that user_id and name to a transactions_to_review.csv file
# include a new column "label" that is either "fp" for false positive or "fn" for false negative
# or empty if the transaction is correctly classified

# create a dictionary of names -> user_id's with misclassified transactions for that name
misclassified_name_to_user_ids = defaultdict(set)
for transaction in misclassified:
    misclassified_name_to_user_ids[transaction.name].add(transaction.user_id)

transactions_to_review = []
labels = []
# loop through the names in reverse order of misclassified transactions
for name, _ in sorted(misclassified_by_name.items(), key=lambda x: x[1], reverse=True):
    for user_id in misclassified_name_to_user_ids[name]:
        for transaction in transactions:
            if transaction.name == name and transaction.user_id == user_id:
                transactions_to_review.append(transaction)
                label = ""
                if transaction in false_positives:
                    label = "fp"
                elif transaction in false_negatives:
                    label = "fn"
                labels.append(label)

# save the transactions to a csv file
write_labeled_transactions(os.path.join(out_dir, "transactions_to_review.csv"), transactions_to_review, y, labels)

# %%
#
# analyze the features using SHAP
# this step takes a LONG time and is optional

# create a tree explainer
# explainer = shap.TreeExplainer(model)
# Faster approximation using PermutationExplainer
X_sample = X[:10000]  # type: ignore
explainer = shap.TreeExplainer(model)

logger.info("Calculating SHAP values")
shap_values = explainer.shap_values(X_sample)

# Plot SHAP summary
shap.summary_plot(shap_values, X_sample, feature_names=feature_names)

# %%
#
# do recursive feature elimination to identify the most important features
# this step also takes a LONG time and is optional

print("Best params:", best_params)
if model_type == "rf":
    model = RandomForestClassifier(random_state=42, **best_params, n_jobs=n_jobs)
elif model_type == "xgb":
    model = xgb.XGBClassifier(random_state=42, **best_params, n_jobs=n_jobs)


# RFECV performs recursive feature elimination with cross-validation
# to find the optimal number of features
logger.info("Performing recursive feature elimination")
cv = GroupKFold(n_splits=n_cv_folds)
rfecv = RFECV(
    estimator=model,
    step=1,
    cv=cv,
    scoring="f1",  # Metric to evaluate the model
    min_features_to_select=50,  # Minimum number of features to select
    n_jobs=n_jobs,
)

# Fit the RFECV
rfecv.fit(X, y, groups=user_ids)
logger.info(f"Optimal number of features: {rfecv.n_features_}")

# Get the selected features
selected_features = [i for i, selected in enumerate(rfecv.support_) if selected]
selected_feature_names = [feature_names[i] for i in selected_features]
print("Selected feature names")
for feature in selected_feature_names:
    print(feature)

# get the eliminated features
eliminated_features = [feature_names[i] for i in range(len(feature_names)) if i not in selected_features]
print("Eliminated feature names")
for feature in eliminated_features:
    print(feature)

# %%
# plot the RFECV results

# Plot the CV scores vs number of features
plt.figure(figsize=(10, 6))
plt.plot(range(1, len(rfecv.cv_results_["mean_test_score"]) + 1), rfecv.cv_results_["mean_test_score"], "o-")
plt.xlabel("Number of features")
plt.ylabel("Cross-validation accuracy")
plt.title("Accuracy vs. Number of Features")
plt.grid(True)
plt.show()

# %%
# Train a new model with only the selected features

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

X_train_selected = X_train[:, selected_features]  # type: ignore
X_test_selected = X_test[:, selected_features]  # type: ignore

if model_type == "rf":
    model_selected = RandomForestClassifier(random_state=42, **best_params, n_jobs=n_jobs)
elif model_type == "xgb":
    model_selected = xgb.XGBClassifier(random_state=42, **best_params, n_jobs=n_jobs)
model_selected.fit(X_train_selected, y_train)

# Evaluate model with selected features
y_pred_selected = model_selected.predict(X_test_selected)
precision = precision_score(y_test, y_pred_selected)
recall = recall_score(y_test, y_pred_selected)
f1 = f1_score(y_test, y_pred_selected)
print("Selected Features:")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")

# %%
# Compare with model using all features

if model_type == "rf":
    model_all = RandomForestClassifier(random_state=42, **best_params, n_jobs=n_jobs)
elif model_type == "xgb":
    model_all = xgb.XGBClassifier(random_state=42, **best_params, n_jobs=n_jobs)
model_all.fit(X_train, y_train)
y_pred_all = model_all.predict(X_test)
precision = precision_score(y_test, y_pred_all)
recall = recall_score(y_test, y_pred_all)
f1 = f1_score(y_test, y_pred_all)
print("All Features:")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")

# %%
