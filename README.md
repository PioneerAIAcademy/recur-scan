# recur-scan

A machine learning system for identifying recurring financial transactions from bank data.

## Overview

Recur-scan analyzes transaction history to automatically detect recurring payments, subscriptions, and other regular financial commitments. It uses a combination of pattern recognition and machine learning to identify:

- Monthly subscriptions (streaming services, memberships, etc.)
- Regular bill payments (utilities, rent, etc.)
- Periodic deposits (paychecks, dividends, etc.)
- Varying-amount recurring transactions

The system processes transaction data from multiple sources, extracts relevant features, and trains models to classify transactions as recurring or non-recurring with high accuracy.

## Development instructions

### Pre-requisites

- Requires [uv](https://github.com/astral-sh/uv) - follow the instructions on that page to install uv.

### Install or sync dependencies

`make install`

Re-run make install whenever new dependencies have been added

#### Add dependency

`uv add <package>`

#### Remove dependency

`uv remove <package>`

### Check code before commit

`make check`

### Run tests

`make test`

### Run a script

`uv run scripts/<script_name>.py`

#### or

`source .venv/bin/activate` # activate the virtual environment

`python scripts/<script_name>.py` # run the script

## Project Structure

- **src/recur_scan/** - Core library for feature extraction and model implementation
- **scripts/** - Data processing, training, and evaluation scripts
  - **10_create_training_data.py** - Prepares transaction data for labeling
  - **15_gather_questions.py** - Identifies ambiguous labels for review
  - **30_train.py** - Trains the recurring transaction detection model
- **tests/** - Unit and integration tests

## Data Flow

1. Raw transaction data is processed by `10_create_training_data.py` into balanced datasets
2. Labelers mark transactions as recurring or non-recurring
3. `15_gather_questions.py` identifies ambiguous cases for review
4. Features are extracted using `recur_scan.features.get_features()`
5. Model is trained using `30_train.py`

## License

This project is licensed under the Apache License - see LICENSE file for details.
