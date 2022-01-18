"""
Helper functions for the carpool system and related functionality.
"""


from datetime import datetime
from typing import List, Tuple


def validate_carpool_request(
    num_passengers: int,
    location_from: str,
    location_to: str,
    datetime_from: str,
    datetime_to: str,
    description: str,
) -> Tuple[bool, List[str]]:
    """
    Validates that a carpool request has valid details.

    Args:
        num_passengers: The number of passengers in the carpool.
        location_from: The starting location of the carpool.
        location_to: The ending location of the carpool.
        datetime_from: The starting time of the carpool.
        datetime_to: The ending time of the carpool.
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
        or not location_from
        or not location_to
        or not datetime_from
        or not datetime_to
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
    # TODO: Validate that the user has entered a future date and time for the journey to and from.

    return valid, error_messages


def add_carpool_request(
    cur,
    num_passengers: int,
    location_from: str,
    location_to: str,
    datetime_from: datetime,
    datetime_to: datetime,
    description: str,
) -> None:
    """
    Adds a valid carpool request to the database.

    Args:
        cur: Cursor for the SQLite database.
        num_passengers: The number of passengers in the carpool.
        location_from: The starting location of the carpool.
        location_to: The ending location of the carpool.
        datetime_from: The starting time of the carpool.
        datetime_to: The ending time of the carpool.
        description: A description of the carpool.
    """
    # Adds the carpool request to the database.
    cur.execute(
        "INSERT INTO carpool_request (num_passengers, location_from, location_to, "
        "datetime_from, datetime_to, description) VALUES (?, ?, ?, ?, ?, ?);",
        (
            num_passengers,
            location_from,
            location_to,
            datetime_from,
            datetime_to,
            description,
        ),
    )
