from datetime import date

import pytest

from recur_scan.utils import get_day, parse_date


def test_parse_date():
    """Test parse_date function."""
    # Test with valid date format
    assert parse_date("2024-01-01") == date(2024, 1, 1)

    # Test with invalid date format
    with pytest.raises(ValueError, match=r"does not match format"):
        parse_date("01/01/2024")


def test_get_day():
    """Test get_day function."""
    assert get_day("2024-01-01") == 1
    assert get_day("2024-01-02") == 2
    assert get_day("2024-01-03") == 3
