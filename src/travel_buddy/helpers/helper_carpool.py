"""
Helper functions for the carpool system and related functionality.
"""


from datetime import datetime
from typing import List, Tuple


def validate_carpool_request(
    num_passengers: int,
    starting_point: str,
    destination: str,
    pickup_datetime: datetime,
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
    ):
        valid = False
        error_messages.append("Please fill in all required fields (marked with *).")

    # Validates that the user has entered a valid number of passengers.
    if num_passengers < 1:
        valid = False
        error_messages.append("Please enter a valid number of passengers (>= 1).")

    # Validates that the description is not too long.
    if len(description) > 500:
        valid = False
        error_messages.append(
            f"Your description is too long - it contains {len(description)} "
            "characters, and there is a 500 character limit."
        )

    # TODO: Validate that the user has entered a valid starting point and destination.

    # Validates that the user has entered a future start date and time.
    if pickup_datetime <= datetime.now():
        valid = False
        error_messages.append("The pickup time must be in the future.")

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
    cur,
    driver: str,
    seats_available: int,
    starting_point: str,
    destination: str,
    pickup_datetime: datetime,
    description: str,
) -> Tuple[bool, List[str]]:
    """
    Validates that a carpool ride has valid details.

    Args:
        driver: The username of the driver for the carpool.
        seats_available: The remaining seats available for the carpool.
        starting_point: The starting location of the carpool.
        destination: The end location of the carpool.
        pickup_datetime: The datetime to get picked up for the carpool.
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
    ):
        valid = False
        error_messages.append("Please fill in all required fields (marked with *).")

    # Validates that the driver exists in the database.
    cur.execute(
        "SELECT * FROM account WHERE username=?;",
        (driver,),
    )
    if cur.fetchone() is None:
        valid = False
        error_messages.append(f"The driver '{driver}' does not exist.")

    # Validates that the user has entered a valid number of seats available.
    if seats_available < 1:
        valid = False
        error_messages.append("Please enter a valid number of seats available (>= 1).")

    # Validates that the description is not too long.
    if len(description) > 500:
        valid = False
        error_messages.append(
            f"Your description is too long - it contains {len(description)} "
            "characters, and there is a 500 character limit."
        )

    # TODO: Validate that the user has entered a valid starting point and destination.

    # Validates that the user has entered a future start date and time.
    if pickup_datetime <= datetime.now():
        valid = False
        error_messages.append("The pickup time must be in the future.")

    return valid, error_messages


def add_carpool_ride(
    cur,
    driver: str,
    seats_available: int,
    starting_point: str,
    destination: str,
    pickup_datetime: datetime,
    description: str,
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
        description: A description of the carpool.
    """
    # Adds the carpool ride to the database.
    cur.execute(
        "INSERT INTO carpool_ride (driver, seats_available, starting_point, "
        "destination, pickup_datetime, description) VALUES (?, ?, ?, ?, ?, ?);",
        (
            driver,
            seats_available,
            starting_point,
            destination,
            pickup_datetime,
            description,
        ),
    )



def get_carpool_list(cur, driver_username) -> List[Tuple[str, str, str, str, str, str, str, str, str, str]]:
    """
    Gets all the carpools in the database and ratings.

    Args:
        cur: Cursor for the SQLite database.
        driver_username: The username of the driver for the carpool.

    Returns:
        A list of tuples containing the carpool information.
    """
    cur.execute(
        """SELECT c.journey_id,
                  c.driver,
                  c.seats_available,
                  c.starting_point,
                  c.destination,
                  c.pickup_datetime,
                  c.description,
        
                  AVG(r.rating_given),
                  COUNT(r.rating_given)

        FROM carpool_ride c
        JOIN rating r ON c.driver = r.rated_username
        WHERE is_complete=0
        GROUP BY c.journey_id
        ORDER BY pickup_datetime ASC;"""
    )

    carpools = cur.fetchall()

    return carpools
