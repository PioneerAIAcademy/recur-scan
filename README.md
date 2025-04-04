# recur-scan

A machine learning system for identifying recurring financial transactions from bank data.

[![Apache License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://github.com/PioneerAIAcademy/recur-scan/blob/main/LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data Flow](#data-flow)
- [Development Guide](#development-guide)
  - [Development Setup](#development-setup)
  - [Adding/Removing Dependencies](#addingremoving-dependencies)
  - [Code Quality](#code-quality)
  - [Running Tests](#running-tests)
  - [Running Scripts](#running-scripts)
- [Contributing](#contributing)
- [License](#license)
- [Contributors](#contributors)

## Overview

Recur-scan analyzes transaction history to automatically detect recurring payments, subscriptions, and other regular financial commitments. It uses a combination of pattern recognition and machine learning to identify:

- Monthly subscriptions (streaming services, memberships, etc.)
- Regular bill payments (utilities, rent, etc.)
- Periodic deposits (paychecks, dividends, etc.)
- Varying-amount recurring transactions

The system processes transaction data from multiple sources, extracts relevant features, and trains models to classify transactions as recurring or non-recurring with high accuracy.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/PioneerAIAcademy/recur-scan.git
   cd recur-scan
   ```

2. Install dependencies:
   ```bash
   make install
   ```

## Usage

Here's how to use recur-scan to analyze transaction data:

```python
from recur_scan.transactions import Transaction
from recur_scan.features import get_features

# Example transaction
transaction = Transaction(
    id=1,
    user_id="user_123",
    name="vendor_456",
    amount=19.99,
    date="2023-01-15",
)

# Get all transactions for this user
all_transactions = [transaction, ...]  # Your transaction history

# Extract features
features = get_features(transaction, all_transactions)

# Use the features with a trained model
# model.predict([list(features.values())])
```

## Project Structure

- **src/recur_scan/** - Core library for feature extraction and model implementation
- **scripts/** - Data processing, training, and evaluation scripts
  - **10_create_training_data.py** - Prepares transaction data for labeling
  - **15_gather_questions.py** - Identifies ambiguous labels for review
  - **20_merge_labeled_transactions.py** - Combines labeled data from multiple sources
  - **30_train.py** - Trains the recurring transaction detection model
- **tests/** - Unit and integration tests

## Data Flow

1. Raw transaction data is processed by `10_create_training_data.py` into balanced datasets
2. Labelers mark transactions as recurring or non-recurring
3. `15_gather_questions.py` identifies ambiguous cases for review
4. `20_merge_labeled_transactions.py` combines and cleans labeled data
5. Features are extracted using `recur_scan.features.get_features()`
6. Model is trained using `30_train.py`

## Development Guide

### Development Setup

Prerequisites:

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Adding/Removing Dependencies

Add a dependency:

```bash
uv add <package>
```

Remove a dependency:

```bash
uv remove <package>
```

### Code Quality

Check code quality before committing:

```bash
make check
```

This runs mypy type checking, ruff linting, and other quality tools.

### Running Tests

Run all tests:

```bash
make test
```

Run a specific test:

```bash
uv run python -m pytest tests/path_to_test.py::test_name -v
```

### Running Scripts

Method 1:

```bash
uv run scripts/<script_name>.py
```

Method 2:

```bash
source .venv/bin/activate
python scripts/<script_name>.py
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`) and quality checks (`make check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the Apache License - see LICENSE file for details.

## Contributors

<table>
  <tr>
    <td align="center"><a href="https://github.com/aghadiayeamayanvboernest"><img src="https://github.com/aghadiayeamayanvboernest.png" width="100px;" alt=""/><br /><sub><b>aghadiayeamayanvboernest</b></sub></a></td>
    <td align="center"><a href="https://github.com/Asimi1234"><img src="https://github.com/Asimi1234.png" width="100px;" alt=""/><br /><sub><b>Asimi1234</b></sub></a></td>
    <td align="center"><a href="https://github.com/chrisedeson"><img src="https://github.com/chrisedeson.png" width="100px;" alt=""/><br /><sub><b>chrisedeson</b></sub></a></td>
    <td align="center"><a href="https://github.com/clack391"><img src="https://github.com/clack391.png" width="100px;" alt=""/><br /><sub><b>clack391</b></sub></a></td>
    <td align="center"><a href="https://github.com/Daveralphy"><img src="https://github.com/Daveralphy.png" width="100px;" alt=""/><br /><sub><b>Daveralphy</b></sub></a></td>
    <td align="center"><a href="https://github.com/devemmanuel1"><img src="https://github.com/devemmanuel1.png" width="100px;" alt=""/><br /><sub><b>devemmanuel1</b></sub></a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/Ebenezerbanky"><img src="https://github.com/Ebenezerbanky.png" width="100px;" alt=""/><br /><sub><b>Ebenezerbanky</b></sub></a></td>
    <td align="center"><a href="https://github.com/Elliot-Nzei"><img src="https://github.com/Elliot-Nzei.png" width="100px;" alt=""/><br /><sub><b>Elliot-Nzei</b></sub></a></td>
    <td align="center"><a href="https://github.com/erubamif"><img src="https://github.com/erubamif.png" width="100px;" alt=""/><br /><sub><b>erubamif</b></sub></a></td>
    <td align="center"><a href="https://github.com/Evena07"><img src="https://github.com/Evena07.png" width="100px;" alt=""/><br /><sub><b>Evena07</b></sub></a></td>
    <td align="center"><a href="https://github.com/francis-2008-happy"><img src="https://github.com/francis-2008-happy.png" width="100px;" alt=""/><br /><sub><b>francis-2008-happy</b></sub></a></td>
    <td align="center"><a href="https://github.com/G-KnowsMoney"><img src="https://github.com/G-KnowsMoney.png" width="100px;" alt=""/><br /><sub><b>G-KnowsMoney</b></sub></a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/gbemi001"><img src="https://github.com/gbemi001.png" width="100px;" alt=""/><br /><sub><b>gbemi001</b></sub></a></td>
    <td align="center"><a href="https://github.com/laurells"><img src="https://github.com/laurells.png" width="100px;" alt=""/><br /><sub><b>laurells</b></sub></a></td>
    <td align="center"><a href="https://github.com/narvas12"><img src="https://github.com/narvas12.png" width="100px;" alt=""/><br /><sub><b>narvas12</b></sub></a></td>
    <td align="center"><a href="https://github.com/ndukanice"><img src="https://github.com/ndukanice.png" width="100px;" alt=""/><br /><sub><b>ndukanice</b></sub></a></td>
    <td align="center"><a href="https://github.com/Nehiz"><img src="https://github.com/Nehiz.png" width="100px;" alt=""/><br /><sub><b>Nehiz</b></sub></a></td>
    <td align="center"><a href="https://github.com/NnatuanyaFrankOguguo"><img src="https://github.com/NnatuanyaFrankOguguo.png" width="100px;" alt=""/><br /><sub><b>NnatuanyaFrankOguguo</b></sub></a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/Nwasir"><img src="https://github.com/Nwasir.png" width="100px;" alt=""/><br /><sub><b>Nwasir</b></sub></a></td>
    <td align="center"><a href="https://github.com/Praise-Enato"><img src="https://github.com/Praise-Enato.png" width="100px;" alt=""/><br /><sub><b>Praise-Enato</b></sub></a></td>
    <td align="center"><a href="https://github.com/Samuel-Innocent"><img src="https://github.com/Samuel-Innocent.png" width="100px;" alt=""/><br /><sub><b>Samuel-Innocent</b></sub></a></td>
    <td align="center"><a href="https://github.com/SegunOladeinde"><img src="https://github.com/SegunOladeinde.png" width="100px;" alt=""/><br /><sub><b>SegunOladeinde</b></sub></a></td>
    <td align="center"><a href="https://github.com/seregheik"><img src="https://github.com/seregheik.png" width="100px;" alt=""/><br /><sub><b>seregheik</b></sub></a></td>
    <td align="center"><a href="https://github.com/T-FEH"><img src="https://github.com/T-FEH.png" width="100px;" alt=""/><br /><sub><b>T-FEH</b></sub></a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/taiwo-stack"><img src="https://github.com/taiwo-stack.png" width="100px;" alt=""/><br /><sub><b>taiwo-stack</b></sub></a></td>
    <td align="center"><a href="https://github.com/Victorprovost"><img src="https://github.com/Victorprovost.png" width="100px;" alt=""/><br /><sub><b>Victorprovost</b></sub></a></td>
    <td align="center"><a href="https://github.com/WilsonGbedemah"><img src="https://github.com/WilsonGbedemah.png" width="100px;" alt=""/><br /><sub><b>WilsonGbedemah</b></sub></a></td>
    <td align="center"><a href="https://github.com/yinkid28"><img src="https://github.com/yinkid28.png" width="100px;" alt=""/><br /><sub><b>yinkid28</b></sub></a></td>
  </tr>
</table>
