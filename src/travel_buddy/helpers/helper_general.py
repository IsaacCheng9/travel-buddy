"""
Handles helper functions for general use cases, such as getting database path.
"""
import os
import pathlib
from base64 import b64decode
import json

def get_keys(file_name: str) -> dict:
    """
    Reads and decodes api keys from given json file.
    Return dictionary of keys
    """
    with open(file_name, "r") as f:
        keys = json.loads(f.read())
    keys = {k: b64decode(v.encode()).decode() for (k, v) in keys.items()}
    return keys

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
