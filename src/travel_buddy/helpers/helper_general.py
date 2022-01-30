"""
Handles helper functions for general use cases, such as getting database path.
"""
import datetime
import json
import os
import pathlib
import uuid
from base64 import b64decode
from typing import List, Tuple

from PIL import Image


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


def string_to_date(date_string: str) -> datetime:
    """
    Converts a string of the form 'YYYY-MM-DDTHH:MM' to a datetime object.

    Args:
        date_string: The string to convert.

    Returns:
        The converted date object.
    """
    return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M")


def is_allowed_image_file(file_name) -> bool:
    """
    Checks if the file is an allowed type.

    Args:
        file_name: The name of the file uploaded by the user.

    Returns:
        Whether the file is allowed or not (True/False).
    """
    return "." in file_name and file_name.rsplit(".", 1)[1].lower() in {
        "png",
        "jpg",
        "jpeg",
        "gif",
    }


def hash_image(file) -> Tuple[bool, List[str], str]:
    """
    Hashes the file to avoid duplicate names for storage in the database.

    Args:
        file: The file uploaded by the user.

    Returns:
        Validity of the image (True/False), error messages if invalid, and the
        hashed file name.
    """
    valid = True
    message = []

    # Hashes the name of the file and resizes it.
    if is_allowed_image_file(file.filename):
        file_name_hashed = str(uuid.uuid4()) + ".jpg"
        directory = pathlib.Path(__file__).parent.parent
        file_path = os.path.join(f"{directory}/static/avatars/", file_name_hashed)
        img = Image.open(file)
        img = img.resize((1000, 1000))
        img = img.convert("RGB")
        img.save(file_path)
    elif file:
        valid = False
        message.append("Your file must be an image.")
        file_name_hashed = ""

    return valid, message, file_name_hashed
