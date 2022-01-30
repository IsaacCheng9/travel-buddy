"""
Tests for the user account system and related functionality, such as user
registration and user login.
"""

import random
import string

import travel_buddy.helpers.helper_login as helper_login
import travel_buddy.helpers.helper_register as helper_register


def test_password_hashing():
    """
    Tests five random passwords consisting of letters, numbers, and punctuation
    to check that they are hashed and can be checked properly for user account
    registration and login.
    """
    for _ in range(5):
        password = "".join(
            random.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(14)
        )
        hashed_password = helper_register.hash_password(password)
        is_valid = helper_login.authenticate_password(password, hashed_password)
        assert is_valid is True
