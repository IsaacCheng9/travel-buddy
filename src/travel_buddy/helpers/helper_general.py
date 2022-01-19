"""
Handles helper functions for general use cases, such as getting database path.
"""
import os
import pathlib


def get_database_path() -> str:
    """
    Gets the directory path to the database.

    Returns:
        The directory path to the SQLite3 database.
    """
    # Gets the root directory of the project, 'travel-buddy'.
    BASE_DIR = pathlib.Path(__file__).parent.parent.parent.parent
    DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")
    return DB_PATH
