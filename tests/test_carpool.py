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
    "pickup_datetime_in_past",
    "pickup_datetime_in_present",
    "negative_price",
    "description_too_long",
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
    price = 10.0
    description = "This is a test description."

    # Tests a valid carpool request.
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, price, description
    ) == (True, [])
    yield

    # Tests an invalid number of passengers.
    num_passengers = -1
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, price, description
    ) == (False, ["Please enter a valid number of passengers (>= 1)."])
    num_passengers = 0
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, price, description
    ) == (False, ["Please enter a valid number of passengers (>= 1)."])
    yield

    # Tests a pickup time that is in the past.
    num_passengers = 3
    pickup_datetime = datetime(year=2020, month=1, day=1, hour=1, minute=1, second=1)
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, price, description
    ) == (False, ["The pickup time must be in the future."])
    yield

    # Tests a pickup time that is in the present.
    pickup_datetime = datetime.now()
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, price, description
    ) == (False, ["The pickup time must be in the future."])
    yield

    # Tests a negative price.
    pickup_datetime = datetime(year=2030, month=1, day=1, hour=1, minute=1, second=1)
    price = -0.01
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, price, description
    ) == (False, ["The price must not be a negative number."])
    yield

    # Tests a description that is too long.
    price = 10.0
    description = "a" * 501
    assert helper_carpool.validate_carpool_request(
        num_passengers, starting_point, destination, pickup_datetime, price, description
    ) == (
        False,
        [
            "Your description is too long - it contains 501 characters, and there is a "
            "500 character limit."
        ],
    )
    yield


@test_steps(
    "valid",
    "invalid_driver",
    "invalid_seats_available",
    "pickup_datetime_in_past",
    "pickup_datetime_in_present",
    "negative_price",
    "description_too_long",
)
def test_validate_carpool_ride():
    """
    Tests whether the validation for carpool rides works for different
    types of valid and invalid requests.
    """
    driver = "johndoe"
    seats_available = 3
    starting_point = "University of Exeter Forum Library, Stocker Rd, Exeter EX4 4PT"
    destination = "Exeter Quay, Exeter EX2 4BZ"
    pickup_datetime = datetime(year=2030, month=1, day=1, hour=1, minute=1, second=1)
    price = 10.0
    description = "This is a test description."
    distance = 1000
    duration = 28000
    co2 = 3.142

    # Tests a valid carpool request.
    assert helper_carpool.validate_carpool_ride(
        driver,
        seats_available,
        starting_point,
        destination,
        pickup_datetime,
        price,
        description,
        distance,
        duration,
        co2,
    ) == (True, [])
    yield

    # Tests a driver that doesn't exist.
    driver = "a" * 50
    assert helper_carpool.validate_carpool_ride(
        driver,
        seats_available,
        starting_point,
        destination,
        pickup_datetime,
        price,
        description,
        distance,
        duration,
        co2,
    ) == (False, [f"The driver '{driver}' does not exist."])
    yield

    # Tests an invalid number of seats available.
    driver = "johndoe"
    seats_available = -1
    assert helper_carpool.validate_carpool_ride(
        driver,
        seats_available,
        starting_point,
        destination,
        pickup_datetime,
        price,
        description,
        distance,
        duration,
        co2,
    ) == (False, ["Please enter a valid number of seats available (>= 1)."])
    seats_available = 0
    assert helper_carpool.validate_carpool_ride(
        driver,
        seats_available,
        starting_point,
        destination,
        pickup_datetime,
        price,
        description,
        distance,
        duration,
        co2,
    ) == (False, ["Please enter a valid number of seats available (>= 1)."])
    yield

    # Tests a pickup time that is in the past.
    seats_available = 3
    pickup_datetime = datetime(year=2020, month=1, day=1, hour=1, minute=1, second=1)
    assert helper_carpool.validate_carpool_ride(
        driver,
        seats_available,
        starting_point,
        destination,
        pickup_datetime,
        price,
        description,
        distance,
        duration,
        co2,
    ) == (False, ["The pickup time must be in the future."])
    yield

    # Tests a pickup time that is in the present.
    pickup_datetime = datetime.now()
    assert helper_carpool.validate_carpool_ride(
        driver,
        seats_available,
        starting_point,
        destination,
        pickup_datetime,
        price,
        description,
        distance,
        duration,
        co2,
    ) == (False, ["The pickup time must be in the future."])
    yield

    # Tests a negative price.
    pickup_datetime = datetime(year=2030, month=1, day=1, hour=1, minute=1, second=1)
    price = -0.01
    assert helper_carpool.validate_carpool_ride(
        driver,
        seats_available,
        starting_point,
        destination,
        pickup_datetime,
        price,
        description,
        distance,
        duration,
        co2,
    ) == (False, ["The price must not be a negative number."])
    yield

    # Tests a description that is too long.
    price = 10.0
    description = "a" * 501
    assert helper_carpool.validate_carpool_ride(
        driver,
        seats_available,
        starting_point,
        destination,
        pickup_datetime,
        price,
        description,
        distance,
        duration,
        co2,
    ) == (
        False,
        [
            "Your description is too long - it contains 501 characters, and there "
            "is a 500 character limit."
        ],
    )
    yield

    # TODO: Add tests for distance, duration, co2.


@test_steps(
    "invalid_journey_id",
    "invalid_driver",
)
def test_validate_joining_carpool():
    """
    Tests whether checks when joining a carpool work correctly.
    """
    # Tests joining a carpool with a negative journey ID, which never exists.
    assert helper_carpool.validate_joining_carpool(-1, "johndoe") == (
        False,
        "Carpool journey does not exist.",
    )
    yield

    # Tests joining a carpool with a driver with a username containing symbols,
    # which never exists.
    assert helper_carpool.validate_joining_carpool(-1, "@@@@@@@@") == (
        False,
        "Carpool journey does not exist.",
    )
    yield


def test_get_total_carpools_joined():
    """
    Tests whether the number of total carpools joined is calculated correctly.
    """
    # The username '@' isn't allowed, so it should have no carpools joined.
    assert helper_carpool.get_total_carpools_joined("@") == 0


def test_get_total_carpools_drove():
    """
    Tests whether the number of total carpools drove is calculated correctly.
    """
    # The username '@' isn't allowed, so it should have no carpools drove.
    assert helper_carpool.get_total_carpools_drove("@") == 0


def test_get_total_distance_carpooled():
    """
    Tests whether the number of total distance carpooled is calculated
    correctly.
    """
    # The username '@' isn't allowed, so it should have 0 km carpooled.
    assert helper_carpool.get_total_distance_carpooled("@") == 0
