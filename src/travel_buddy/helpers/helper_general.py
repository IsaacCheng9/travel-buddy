"""
Handles helper functions for general use cases, such as getting database path.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_database_path() -> str:
    """
    Gets the directory path to the database.

    Returns:
        The directory path to the SQLite3 database.
    """
    DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")
    return DB_PATH
