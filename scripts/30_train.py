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
import matplotlib.pyplot as plt
import shap
from loguru import logger
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import RFECV
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split

from recur_scan.features import get_features
from recur_scan.transactions import group_transactions, read_labeled_transactions, write_transactions

# %%
# configure the script

n_cv_folds = 3  # number of cross-validation folds, could be 5
do_hyperparameter_optimization = False  # set to False to use the default hyperparameters
n_hpo_iters = 20  # number of hyperparameter optimization iterations
n_jobs = -1  # number of jobs to run in parallel (set to 1 if your laptop gets too hot)

in_path = csv_path = os.path.join(os.path.dirname(__file__), "../recur_scan_train.csv")
out_dir = "/mnt/c/User/user/Desktop/happy_output_transaction"

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

logger.info("Getting features")
features = [
    get_features(transaction, grouped_transactions[(transaction.user_id, transaction.name)])
    for transaction in transactions
]

# convert features to a matrix for machine learning
dict_vectorizer = DictVectorizer(sparse=False)
X = dict_vectorizer.fit_transform(features)
feature_names = dict_vectorizer.get_feature_names_out()  # Get feature names from the vectorizer
logger.info(f"Converted {len(features)} features into a {X.shape} matrix")

# %%
#
# HYPERPARAMETER OPTIMIZATION
#

if do_hyperparameter_optimization:
    # Define parameter grid
    param_dist = {
        "n_estimators": [10, 20, 50, 100, 200, 500, 1000],
        "max_depth": [10, 20, 30, None],
        "min_samples_split": [2, 5, 10, 20, 50],
        "min_samples_leaf": [1, 2, 4],
        "max_features": ["sqrt", "log2", None],
        "bootstrap": [True, False],
    }

    # Random search
    model = RandomForestClassifier(random_state=42, n_jobs=n_jobs)
    random_search = RandomizedSearchCV(
        model, param_dist, n_iter=n_hpo_iters, cv=n_cv_folds, scoring="f1", n_jobs=n_jobs, verbose=3
    )
    random_search.fit(X, y)

    print("Best Hyperparameters:")
    for param, value in random_search.best_params_.items():
        print(f"  {param}: {value}")

    best_params = random_search.best_params_
else:
    # default hyperparameters
    best_params = {
        "n_estimators": 100,
        "min_samples_split": 10,
        "min_samples_leaf": 1,
        "max_features": "sqrt",
        "max_depth": None,
        "bootstrap": False,
    }

# %%
#
# TRAIN THE MODEL
#

# now that we have the best hyperparameters, train a model with them

logger.info("Training the model")
model = RandomForestClassifier(random_state=42, **best_params, n_jobs=n_jobs)
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

cv = StratifiedKFold(n_splits=n_cv_folds, shuffle=True, random_state=42)
misclassified = []
precisions = []
recalls = []
f1s = []

for fold, (train_idx, val_idx) in enumerate(cv.split(X, y)):
    logger.info(f"Fold {fold + 1} of {n_cv_folds}")
    # Get training and validation data
    X_train = [X[i] for i in train_idx]  # type: ignore
    X_val = [X[i] for i in val_idx]  # type: ignore
    y_train = [y[i] for i in train_idx]
    y_val = [y[i] for i in val_idx]
    transactions_val = [transactions[i] for i in val_idx]  # Keep the original transaction instances for this fold

    # Train the model
    model = RandomForestClassifier(random_state=42, **best_params, n_jobs=n_jobs)
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
#
# analyze the features using SHAP
# this step takes a LONG time and is optional

# create a tree explainer
# explainer = shap.TreeExplainer(model)
# Faster approximation using PermutationExplainer
X_sample = X[:10000]  # type: ignore
explainer = shap.explainers.Permutation(model.predict, X_sample)

logger.info("Calculating SHAP values")
shap_values = explainer.shap_values(X_sample)

# Plot SHAP summary
shap.summary_plot(shap_values, X_sample, feature_names=feature_names)

# %%
#
# do recursive feature elimination to identify the most important features
# this step also takes a LONG time and is optional

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)


# RFECV performs recursive feature elimination with cross-validation
# to find the optimal number of features
logger.info("Performing recursive feature elimination")
rfecv = RFECV(
    estimator=model,
    step=1,  # Remove one feature at a time
    cv=cv,
    scoring="f1",  # Metric to evaluate the model
    min_features_to_select=1,  # Minimum number of features to select
    n_jobs=n_jobs,
)

# Fit the RFECV
rfecv.fit(X_train, y_train)
logger.info(f"Optimal number of features: {rfecv.n_features_}")

# Get the selected features
selected_features = [i for i, selected in enumerate(rfecv.support_) if selected]
print(f"Selected features: {selected_features}")

# If you have feature names
selected_feature_names = [feature_names[i] for i in selected_features]
print(f"Selected feature names: {selected_feature_names}")

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

X_train_selected = X_train[:, selected_features]  # type: ignore
X_test_selected = X_test[:, selected_features]  # type: ignore

rf_selected = RandomForestClassifier(random_state=42, **best_params, n_jobs=n_jobs)
rf_selected.fit(X_train_selected, y_train)

# Evaluate model with selected features
y_pred_selected = rf_selected.predict(X_test_selected)
precision = precision_score(y_test, y_pred_selected)
recall = recall_score(y_test, y_pred_selected)
f1 = f1_score(y_test, y_pred_selected)
print("Selected Features:")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")

# %%
# Compare with model using all features

rf_all = RandomForestClassifier(random_state=42, **best_params, n_jobs=n_jobs)
rf_all.fit(X_train, y_train)
y_pred_all = rf_all.predict(X_test)
precision = precision_score(y_test, y_pred_all)
recall = recall_score(y_test, y_pred_all)
f1 = f1_score(y_test, y_pred_all)
print("All Features:")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")
