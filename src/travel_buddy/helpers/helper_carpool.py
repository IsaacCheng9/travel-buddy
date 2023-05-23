"""
Helper functions for the carpool system and related functionality.
"""


import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple

import travel_buddy.helpers.helper_general as helper_general
import travel_buddy.helpers.helper_routes as helper_routes

DB_PATH = helper_general.get_database_path()


def get_icons(description):
    """
    Get the icons for the carpool description
    """

    description = description.lower()

    icons = ""

    if "no smoking" in description:
        icons += '<i class="fa-solid fa-ban-smoking"></i>'

    return icons


def validate_carpool_request(
    num_passengers: int,
    starting_point: str,
    destination: str,
    pickup_datetime: datetime,
    desired_price: float,
    description: str,
) -> Tuple[bool, List[str]]:
    """
    Validates that a carpool request has valid details.

    Args:
        num_passengers: The number of passengers in the carpool.
        starting_point: The starting location of the carpool.
        destination: The end location of the carpool.
        pickup_datetime: The datetime to get picked up for the carpool.
        description: A description of the carpool.
        desired_price: The price they are willing to pay for the carpool.

    Returns:
        Whether the request was valid, and the error messages to display
        if not.
    """
    valid = True
    error_messages = []

    # Validates that no required fields are missing.
    if (
        not num_passengers
        and num_passengers != 0
        or not starting_point
        or not destination
        or not pickup_datetime
        or not desired_price
    ):
        valid = False
        error_messages.append("Please fill in all required fields (marked with *).")

    # Validates that the user has entered a valid number of passengers.
    if num_passengers < 1:
        valid = False
        error_messages.append("Please enter a valid number of passengers (>= 1).")

    # Validates that the user has entered a future start date and time.
    if pickup_datetime <= datetime.now():
        valid = False
        error_messages.append("The pickup time must be in the future.")

    # Checks that the user has entered a valid price.
    if desired_price < 0:
        valid = False
        error_messages.append("The price must not be a negative number.")

    # Validates that the description is not too long.
    if len(description) > 500:
        valid = False
        error_messages.append(
            f"Your description is too long - it contains {len(description)} "
            "characters, and there is a 500 character limit."
        )

    # TODO: Validate that the user has entered a valid starting point and destination.

    return valid, error_messages


def add_carpool_request(
    cur,
    num_passengers: int,
    starting_point: str,
    destination: str,
    pickup_datetime: datetime,
    description: str,
) -> None:
    """
    Adds a valid carpool request to the database.

    Args:
        cur: Cursor for the SQLite database.
        num_passengers: The number of passengers in the carpool.
        starting_point: The starting location of the carpool.
        destination: The end location of the carpool.
        pickup_datetime: The datetime to get picked up for the carpool.
        description: A description of the carpool.
    """
    # Adds the carpool request to the database.
    cur.execute(
        "INSERT INTO carpool_request (num_passengers, starting_point, destination, "
        "pickup_datetime, description) VALUES (?, ?, ?, ?, ?);",
        (
            num_passengers,
            starting_point,
            destination,
            pickup_datetime,
            description,
        ),
    )


def validate_carpool_ride(
    driver: str,
    seats_available: int,
    starting_point: str,
    destination: str,
    pickup_datetime: datetime,
    price: float,
    description: str,
    distance: str,
    duration: str,
    co2: str,
) -> Tuple[bool, List[str]]:
    """
    Validates that a carpool ride has valid details.

    Args:
        driver: The username of the driver for the carpool.
        seats_available: The remaining seats available for the carpool.
        starting_point: The starting location of the carpool.
        destination: The end location of the carpool.
        pickup_datetime: The datetime to get picked up for the carpool.
        price: The price they are charging passengers for the ride.
        description: A description of the carpool.

    Returns:
        Whether the carpool ride was valid, and the error messages to display
        if not.
    """
    valid = True
    error_messages = []

    # Validates that no required fields are missing.
    if (
        not driver
        or not seats_available
        and seats_available != 0
        or not starting_point
        or not destination
        or not pickup_datetime
        or not price
    ):
        valid = False
        error_messages.append("Please fill in all required fields (marked with *).")

    # Validates that the driver exists in the database.
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT username FROM account WHERE username=? LIMIT 1;",
            (driver,),
        )
        if cur.fetchone() is None:
            valid = False
            error_messages.append(f"The driver '{driver}' does not exist.")

    # Validates that the user has entered a valid number of seats available.
    if seats_available < 1:
        valid = False
        error_messages.append("Please enter a valid number of seats available (>= 1).")

    # Checks that the user has entered a valid price.
    if price < 0:
        valid = False
        error_messages.append("The price must not be a negative number.")

    # Validates that the user has entered a future start date and time.
    if pickup_datetime <= datetime.now():
        valid = False
        error_messages.append("The pickup time must be in the future.")

    # Validates that the description is not too long.
    if len(description) > 500:
        valid = False
        error_messages.append(
            f"Your description is too long - it contains {len(description)} "
            "characters, and there is a 500 character limit."
        )

    return valid, error_messages


def add_carpool_ride(
    driver: str,
    seats_initial: int,
    starting_point: str,
    destination: str,
    pickup_datetime: datetime,
    price: float,
    description: str,
    distance: int,
    distance_text: str,
    duration: int,
    duration_text: str,
    co2_pp: float,
    co2_saved: float,
) -> None:
    """
    Adds a valid carpool request to the database.

    Args:
        driver: The username of the driver for the carpool.
        cur: Cursor for the SQLite database.
        num_passengers: The number of passengers in the carpool.
        starting_point: The starting location of the carpool.
        destination: The end location of the carpool.
        pickup_datetime: The datetime to get picked up for the carpool.
        price: The price they are charging passengers for the ride.
        description: A description of the carpool.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # Adds the carpool ride to the database.
        cur.execute(
            "INSERT INTO carpool_ride (driver, seats_initial, seats_available, starting_point, "
            "destination, pickup_datetime, price, description, distance, distance_text, "
            "estimate_duration, estimate_duration_text, estimate_co2_per_person, estimate_co2_saved) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
            (
                driver,
                seats_initial,
                seats_initial,
                starting_point,
                destination,
                pickup_datetime,
                price,
                description,
                distance,
                distance_text,
                duration,
                duration_text,
                co2_pp,
                co2_saved,
            ),
        )


def get_incomplete_carpools() -> (
    List[
        Tuple[
            int, str, int, str, str, str, float, str, float, int, float, float, str, int
        ]
    ]
):
    """
    Gets all incomplete carpools in the database and ratings for the driver.

    Returns:
        A list of tuples containing the carpool information.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT c.journey_id,
                    c.driver,
                    c.seats_available,
                    c.starting_point,
                    c.destination,
                    c.pickup_datetime,
                    c.price,
                    c.description,
                    c.distance,
                    c.distance_text,
                    c.estimate_duration,
                    c.estimate_duration_text,
                    c.estimate_co2_per_person,
                    c.estimate_co2_saved,

                    AVG(r.rating_given),
                    COUNT(r.rating_given)

            FROM carpool_ride c
            LEFT JOIN rating r ON c.driver = r.rated_username
            WHERE c.is_complete=0
            AND CURRENT_TIMESTAMP < c.pickup_datetime
            GROUP BY c.journey_id
            ORDER BY pickup_datetime ASC;"""
        )
        incomplete_carpools = cur.fetchall()
    return incomplete_carpools


def get_user_interested_carpools(username: str) -> list:
    """
    Gets all carpools that the user is interested in.

    Args:
        username: The username of the user.

    Returns:
        A list of tuples containing the carpool ids.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT journey_id FROM carpool_interest
            WHERE username=?;""",
            (username,),
        )
        interested_carpools = cur.fetchall()

    # change list of tupples [('22',), ('23',)] to list of ints [22, 23]
    return list(map(lambda x: int(x[0]), interested_carpools))


def get_carpool_details(journey_id: int) -> list:
    """
    Gets the details of a carpool journey from the database if not expired.

    Args:
        journey_id: The unique identifier for the selected carpool.

    Returns:
        The details of the carpool, such as the driver and seats available.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT driver, is_complete, seats_initial, seats_available, starting_point, "
            "destination, pickup_datetime, price, description, distance_text, estimate_duration, "
            "estimate_duration_text, estimate_co2_per_person, estimate_co2_saved "
            "FROM carpool_ride WHERE journey_id=?;",
            (journey_id,),
        )
        carpool_details = cur.fetchone()
        return carpool_details


def validate_joining_carpool(journey_id: int, username: str) -> bool:
    """
    Validates whether the carpool can be joined by the user.

    Args:
        journey_id: The unique identifier for the selected carpool.
        username: The user who wants to join the carpool.

    Returns:
        Whether all checks have passed (True/False).
    """
    valid = True
    error_messages = []

    carpool_details = get_carpool_details(journey_id)
    if not carpool_details:
        return False, "Carpool journey does not exist."

    (
        driver,
        is_complete,
        seats_available,
        _,
        _,
        _,
        _,
        _,
    ) = carpool_details[0]
    # The user cannot join their own carpool.
    if driver == username:
        valid = False
        error_messages.append("You cannot join your own carpool.")
    # The user may only join a carpool that hasn't been completed.
    if is_complete:
        valid = False
        error_messages.append("You cannot join a completed carpool.")
    # The carpool must have at least one seat available.
    if seats_available < 1:
        valid = False
        error_messages.append("There are not enough seats available in this carpool.")

    return valid, error_messages


def add_passenger_to_carpool_journey(journey_id: int, username: str):
    """
    Adds the passenger to the carpool journey by creating a carpool request
    with a journey ID attached to it and updating the journey.

    Args:
        journey_id: The unique identifier for the selected carpool.
        username: The user to add to the carpool journey.
    """
    carpool_details = get_carpool_details(journey_id)
    (
        _,
        _,
        _,
        starting_point,
        destination,
        pickup_datetime,
        price,
        _,
    ) = carpool_details[0]

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # Creates a carpool request with the journey ID attached to it, as this
        # indicates that there is a matching carpool ride listing.
        cur.execute(
            "INSERT INTO carpool_request "
            "(requester, journey_id, num_passengers, starting_point, destination, "
            "pickup_datetime, price, description) VALUES (?, ?, ?, ?, ?, ?, ?);",
            (
                username,
                journey_id,
                1,
                starting_point,
                destination,
                pickup_datetime,
                price,
                "Joined from the carpool listing.",
            ),
        )
        # Decrements the number of available seats in the carpool ride.
        cur.execute(
            "UPDATE carpool_ride SET seats_available=seats_available-1 "
            "WHERE journey_id=?;",
            (journey_id,),
        )
        conn.commit()


def estimate_carpool_details(
    start_point: str, end_point: str, seats: int, filename: str
) -> Tuple[int, str, int, str, str]:
    """
    Fetch the estimated distance, duration, and co2 emissions of a carpooling journey
    """
    key = helper_general.get_keys(filename).get("google_maps")
    map_client = helper_routes.generate_client(key)
    details = helper_routes.run_api(map_client, start_point, end_point, "driving")
    distance = helper_routes.safeget(
        details, "rows", 0, "elements", 0, "distance", "value"
    )
    distance_text = helper_routes.safeget(
        details, "rows", 0, "elements", 0, "distance", "text"
    )
    duration = helper_routes.safeget(
        details, "rows", 0, "elements", 0, "duration", "value"
    )
    duration_text = helper_routes.safeget(
        details, "rows", 0, "elements", 0, "duration", "text"
    )
    co2 = helper_routes.generate_co2_emissions(
        helper_routes.safeget(details, "rows", 0, "elements", 0, "distance", "value"),
        "driving",
        "petrol",
    )
    co2_pp = round(co2 / (seats), 2)
    co2_saved = round(co2 - (co2 / (seats)), 2)
    return (distance, distance_text, duration, duration_text, co2_pp, co2_saved)


def get_passenger_list(journey_id: int) -> list:
    """
    Gets the list of passengers for a carpool journey from the database.

    Args:
        journey_id: The unique identifier for the selected carpool.

    Returns:
        The list of passengers for the carpool.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT requester FROM carpool_request WHERE journey_id=?;", (journey_id,)
        )
        conn.commit()
        passenger_list = cur.fetchall()
    return passenger_list


def get_total_carpools_joined(username: str) -> int:
    """
    Gets the total number of carpools joined by the user.
    Args:
        username: The user to calculate the statistic for.
    Returns:
        The number of carpools joined by the user.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(request_id) FROM carpool_request "
            "WHERE requester=? AND journey_id IS NOT NULL;",
            (username,),
        )
        total_carpools_joined = cur.fetchone()[0]
    return total_carpools_joined


def get_total_carpools_drove(username: str) -> int:
    """
    Gets the total number of carpools drove by the user.
    Args:
        username: The user to calculate the statistic for.
    Returns:
        The number of carpools drove by the user.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(journey_id) FROM carpool_ride "
            "WHERE driver=? AND is_complete=1;",
            (username,),
        )
        total_carpools_drove = cur.fetchone()[0]
    return total_carpools_drove


def get_total_distance_carpooled(username: str) -> int:
    """
    Gets the total distance carpooled (joined and drove) by the user.
    Args:
        username: The user to calculate the statistic for.
    Returns:
        The total distance carpooled by the user.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # Gets total distance drove by the user for a carpool.
        cur.execute(
            "SELECT SUM(distance) FROM carpool_ride "
            "WHERE driver=? AND is_complete=1;",
            (username,),
        )
        total_distance_drove = cur.fetchone()[0]
        if total_distance_drove:
            total_distance_drove /= 1000
        else:
            total_distance_drove = 0

        # Gets total distance rode by the user for a carpool that they joined.
        cur.execute(
            "SELECT SUM(distance) FROM carpool_request "
            "WHERE requester=? AND journey_id IS NOT NULL;",
            (username,),
        )
        total_distance_joined = cur.fetchone()[0]
        if total_distance_joined:
            total_distance_joined /= 1000
        else:
            total_distance_joined = 0

        total_distance_carpooled = round(
            total_distance_drove + total_distance_joined, 2
        )
    return total_distance_carpooled


def get_total_co2_saved(username: str) -> float:
    """
    Gets the total co2 saved from carpooling (joined and drove) by the user.
    Args:
        username: The user to calculate the statistic for.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # Gets total distance drove by the user for a carpool.
        cur.execute(
            "SELECT SUM(estimate_co2_saved) FROM carpool_ride "
            "WHERE driver=? AND is_complete=1;",
            (username,),
        )
        total_co2_saved_driver = cur.fetchone()[0]
        if not total_co2_saved_driver:
            total_co2_saved_driver = 0

        # Gets total distance rode by the user for a carpool that they joined.
        cur.execute(
            "SELECT SUM(estimate_co2_saved) FROM carpool_request "
            "WHERE requester=? AND journey_id IS NOT NULL;",
            (username,),
        )
        total_co2_saved_passenger = cur.fetchone()[0]
        if not total_co2_saved_passenger:
            total_co2_saved_passenger = 0

        total_co2_saved = round(total_co2_saved_driver + total_co2_saved_passenger, 2)
    return total_co2_saved


def get_money_saved(username: str) -> float:
    """
    Gets an estimate for the total fuel money saved from carpooling (joined and drove) by the user.
    Args:
        username: The user to calculate the statistic for.
    """
    # TODO: Calculate cost savings based on car used for each trip rather than
    # just the user's car
    _, car_mpg, fuel_type, _ = helper_routes.get_car(username)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # Gets total distance drove by the user for a carpool.
        cur.execute(
            "SELECT distance, seats_initial FROM carpool_ride "
            "WHERE driver=? AND is_complete=1;",
            (username,),
        )
        carpools_driven = cur.fetchall()
        money_saved_driving = 0
        if carpools_driven:
            for c in carpools_driven:
                if all(c):
                    money_saved_driving += helper_routes.calculate_total_fuel_cost(
                        c[0], car_mpg, fuel_type
                    )[1]

        # Gets total distance rode by the user for a carpool that they joined.
        cur.execute(
            "SELECT distance, num_passengers FROM carpool_request "
            "WHERE requester=? AND journey_id IS NOT NULL;",
            (username,),
        )
        carpools_joined = cur.fetchall()
        money_saved_joining = 0
        if carpools_joined:
            for c in carpools_joined:
                if all(c):
                    money_saved_joining += helper_routes.calculate_total_fuel_cost(
                        c[0], car_mpg, fuel_type
                    )[1]

    total_money_saved = round(money_saved_driving + money_saved_joining, 2)

    return total_money_saved


def get_datetime_obj(t: str) -> object:
    """
    Return a datetime object from a datetime string
    """
    return datetime.strptime(t, "%Y-%m-%d %H:%M:%S")


def format_start_time(start_time: object) -> str:
    """
    Return hours and minutes from a datetime object
    """
    return datetime.strftime(start_time, "%e/%m %H:%M")


def get_end_time_obj(start_time: object, duration: int) -> object:
    """
    Return the estimated end time object based on the start time and duration in seconds
    """
    return start_time + timedelta(seconds=round(duration / 60) * 60)


def get_end_time(emd_time_obj: object) -> str:
    """
    Return the estimated end time string
    """
    return datetime.strftime(emd_time_obj, "%e/%m %H:%M")
