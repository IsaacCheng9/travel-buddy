"""
Helper functions for the user login system and related functionality.
"""

import bcrypt


def authenticate_password(password: str, hashed_password: str) -> str:
    """
    Authenticates the password using bcrypt.

    Args:
        password: The password input by the user in the form.
        hashed_password: The password stored in the database for that user.

    Returns:
        Whether the password matches the password for the user.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)
