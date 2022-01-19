"""
Tests for the carpool system and related functionality, such as validating carpool
requests.
"""

from datetime import datetime

import travel_buddy.helpers.helper_carpool as helper_carpool


def test_validate_carpool_request():
    """
    Tests whether the validation for carpool requests works for different
    type of valid and invalid requests.
    """
    location_from = "University of Exeter Forum Library, Stocker Rd, Exeter EX4 4PT"
    location_to = "Exeter Quay, Exeter EX2 4BZ"
    pickup_datetime = datetime(year=2030, month=1, day=1, hour=1, minute=1, second=1)
    description = "This is a test description."

    # Tests an invalid number of passengers.
    num_passengers = -1
    assert helper_carpool.validate_carpool_request(
        num_passengers, location_from, location_to, pickup_datetime, description
    ) == (False, ["Please enter a valid number of passengers (>= 1)."])
    num_passengers = 0
    assert helper_carpool.validate_carpool_request(
        num_passengers, location_from, location_to, pickup_datetime, description
    ) == (False, ["Please enter a valid number of passengers (>= 1)."])

    # Tests a valid number of passengers.
    num_passengers = 3
    assert helper_carpool.validate_carpool_request(
        num_passengers, location_from, location_to, pickup_datetime, description
    ) == (True, [])

    # Tests a description that is too long.
    description = "a" * 501
    assert helper_carpool.validate_carpool_request(
        num_passengers, location_from, location_to, pickup_datetime, description
    ) == (
        False,
        [
            "Your description is too long - it contains 501 characters, and there is a "
            "500 character limit."
        ],
    )

    # Tests a pickup time that is in the past.
    description = "This is a test description."
    pickup_datetime = datetime(year=2020, month=1, day=1, hour=1, minute=1, second=1)
    assert helper_carpool.validate_carpool_request(
        num_passengers, location_from, location_to, pickup_datetime, description
    ) == (False, ["The pickup time must be in the future."])

    # Tests a pickup time that is in the present.
    description = "This is a test description."
    pickup_datetime = datetime.now()
    assert helper_carpool.validate_carpool_request(
        num_passengers, location_from, location_to, pickup_datetime, description
    ) == (False, ["The pickup time must be in the future."])
