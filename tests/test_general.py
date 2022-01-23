"""
Tests integrity of general helper functions.
"""
import datetime

import travel_buddy.helpers.helper_general as helper_general


def test_string_to_date():
    """
    Tests whether converting to string to date is performed correctly.
    """
    string_date = "2020-01-01T23:00"
    datetime_date = helper_general.string_to_date(string_date)
    assert datetime.datetime.strftime(datetime_date, "%Y-%m-%dT%H:%M") == string_date
