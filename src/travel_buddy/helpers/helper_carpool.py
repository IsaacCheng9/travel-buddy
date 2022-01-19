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
        Whether the registration was valid, and the error messages to display
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

    # Validate that the user has entered a valid number of passengers.
    if num_passengers < 1:
        valid = False
        error_messages.append("Please enter a valid number of passengers (>= 1).")

    # Validate that the description is not too long.
    if len(description) > 500:
        valid = False
        error_messages.append(
            f"Your description is too long - it contains {len(description)} "
            "characters, and there is a 500 character limit."
        )

    # TODO: Validate that the user has entered a valid location for the journey to and from.

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
