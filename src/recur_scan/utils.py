from datetime import date, datetime
from functools import lru_cache


@lru_cache(maxsize=1024)
def parse_date(date_str: str) -> date:
    """Parse a date string strictly in 'YYYY-MM-DD' format."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def get_day(date: str) -> int:
    """Get the day of the month from a transaction date."""
    return int(date.split("-")[2])
