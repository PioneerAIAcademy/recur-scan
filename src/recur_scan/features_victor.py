from datetime import datetime

from recur_scan.transactions import Transaction


def get_avg_days_between(all_transactions: list[Transaction]) -> float:
    dates = sorted([t.date for t in all_transactions])
    if len(dates) > 1:
        deltas = [
            (datetime.strptime(dates[i + 1], "%Y-%m-%d") - datetime.strptime(dates[i], "%Y-%m-%d")).days
            for i in range(len(dates) - 1)
        ]
        return sum(deltas) / len(deltas)
    else:
        return 0.0
