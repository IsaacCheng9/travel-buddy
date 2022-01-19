"""
Tests for the carpool system and related functionality, such as validating carpool
requests.
"""

import sqlite3
from datetime import datetime

import travel_buddy.helpers.helper_carpool as helper_carpool
import travel_buddy.helpers.helper_general as helper_general
from pytest_steps import test_steps

DB_PATH = helper_general.get_database_path()


@test_steps(
    "valid",
    "invalid_passengers",
    "description_too_long",
    "pickup_datetime_in_past",
    "pickup_datetime_in_present",
)
def test_validate_carpool_request():
    """
    Tests whether the validation for carpool requests works for different
    types of valid and invalid requests.
    """
    num_passengers = 3
    starting_point = "University of Exeter Forum Library, Stocker Rd, Exeter EX4 4PT"
    destination = "Exeter Quay, Exeter EX2 4BZ"
    pickup_datetime = datetime(year=2030, month=1, day=1, hour=1, minute=1, second=1)
    description = "This is a test description."

    # Tests a valid carpool request.
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, description
    ) == (True, [])
    yield

    # Tests an invalid number of passengers.
    num_passengers = -1
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, description
    ) == (False, ["Please enter a valid number of passengers (>= 1)."])
    num_passengers = 0
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, description
    ) == (False, ["Please enter a valid number of passengers (>= 1)."])
    yield

    # Tests a description that is too long.
    num_passengers = 3
    description = "a" * 501
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, description
    ) == (
        False,
        [
            "Your description is too long - it contains 501 characters, and there is a "
            "500 character limit."
        ],
    )
    yield

    # Tests a pickup time that is in the past.
    description = "This is a test description."
    pickup_datetime = datetime(year=2020, month=1, day=1, hour=1, minute=1, second=1)
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, description
    ) == (False, ["The pickup time must be in the future."])
    yield

    # Tests a pickup time that is in the present.
    description = "This is a test description."
    pickup_datetime = datetime.now()
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, description
    ) == (False, ["The pickup time must be in the future."])
    yield


@test_steps(
    "valid",
    "invalid_driver",
    "invalid_seats_available",
    "description_too_long",
    "pickup_datetime_in_past",
    "pickup_datetime_in_present",
)
def test_validate_carpool_ride():
    """
    Tests whether the validation for carpool rides works for different
    types of valid and invalid requests.
    """
    print(DB_PATH)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        driver = "johndoe"
        seats_available = 3
        starting_point = (
            "University of Exeter Forum Library, Stocker Rd, Exeter EX4 4PT"
        )
        destination = "Exeter Quay, Exeter EX2 4BZ"
        pickup_datetime = datetime(
            year=2030, month=1, day=1, hour=1, minute=1, second=1
        )
        description = "This is a test description."

        # Tests a valid carpool request.
        assert (
            helper_carpool.validate_carpool_ride(
                cur,
                driver,
                seats_available,
                starting_point,
                destination,
                pickup_datetime,
                description,
            )
            == (True, [])
        )
        yield

        # Tests a driver that doesn't exist.
        driver = "a" * 50
        assert (
            helper_carpool.validate_carpool_ride(
                cur,
                driver,
                seats_available,
                starting_point,
                destination,
                pickup_datetime,
                description,
            )
            == (False, [f"The driver '{driver}' does not exist."])
        )
        yield

        # Tests an invalid number of seats available.
        driver = "johndoe"
        seats_available = -1
        assert (
            helper_carpool.validate_carpool_ride(
                cur,
                driver,
                seats_available,
                starting_point,
                destination,
                pickup_datetime,
                description,
            )
            == (False, ["Please enter a valid number of seats available (>= 1)."])
        )
        seats_available = 0
        assert (
            helper_carpool.validate_carpool_ride(
                cur,
                driver,
                seats_available,
                starting_point,
                destination,
                pickup_datetime,
                description,
            )
            == (False, ["Please enter a valid number of seats available (>= 1)."])
        )
        yield

        # Tests a description that is too long.
        seats_available = 3
        description = "a" * 501
        assert helper_carpool.validate_carpool_ride(
            cur,
            driver,
            seats_available,
            starting_point,
            destination,
            pickup_datetime,
            description,
        ) == (
            False,
            [
                "Your description is too long - it contains 501 characters, and there "
                "is a 500 character limit."
            ],
        )
        yield

        # Tests a pickup time that is in the past.
        description = "This is a test description."
        pickup_datetime = datetime(
            year=2020, month=1, day=1, hour=1, minute=1, second=1
        )
        assert (
            helper_carpool.validate_carpool_ride(
                cur,
                driver,
                seats_available,
                starting_point,
                destination,
                pickup_datetime,
                description,
            )
            == (False, ["The pickup time must be in the future."])
        )
        yield

        # Tests a pickup time that is in the present.
        description = "This is a test description."
        pickup_datetime = datetime.now()
        assert (
            helper_carpool.validate_carpool_ride(
                cur,
                driver,
                seats_available,
                starting_point,
                destination,
                pickup_datetime,
                description,
            )
            == (False, ["The pickup time must be in the future."])
        )
        yield
