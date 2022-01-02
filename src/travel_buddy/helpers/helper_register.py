from typing import List, Tuple


def validate_registration(
    cur,
    username: str,
    first_name: str,
    last_name: str,
    password: str,
    password_confirm: str,
) -> Tuple[bool, List[str]]:
    """
    Validates the registration details to ensure that the requirements have
    been met.

    Args:
        cur: Cursor for the SQLite database.
        username: The username input by the user in the form.
        first_name: The first name input by the user in the form.
        last_name: The last name input by the user in the form.
        password: The password input by the user in the form.
        password_confirm: The password confirmation input by the user in the
                          form.

    Returns:
        Whether the registration was valid, and the error message(s) if not.
    """
    # Registration remains valid as long as it isn't caught by any checks. If
    # not, error messages will be provided to the user.
    valid = True
    message = []

    # Checks that there are no null inputs.
    if (
        username == ""
        or first_name == ""
        or last_name == ""
        or password == ""
        or password_confirm == ""
    ):
        message.append("Not all fields have been filled in!")
        valid = False

    # Checks that the username only contains valid characters.
    if username.isalnum() is False:
        message.append("Username must only contain letters and numbers!")
        valid = False
    # Checks that the username hasn't already been registered.
    cur.execute("SELECT * FROM account WHERE username=?;", (username,))
    if cur.fetchone() is not None:
        message.append("Username has already been registered!")
        valid = False

    # Checks that the first and last names don't exceed 20 characters.
    if len(first_name) > 20:
        message.append("First name exceeds 20 characters!")
        valid = False
    if len(last_name) > 20:
        message.append("Last name  exceeds 20 characters!")
        valid = False
    # Checks that the first and last names only contains valid characters.
    if not all(x.isalpha() or x.isspace() for x in first_name):
        message.append("First name must only contain letters and spaces!")
        valid = False
    if not all(x.isalpha() or x.isspace() for x in last_name):
        message.append("Last name must only contain letters and spaces!")
        valid = False

    # Checks that the password has a minimum length of 8 characters, and at
    # least one number.
    if len(password) <= 7 or any(char.isdigit() for char in password) is False:
        message.append(
            "Password does not meet requirements! It must contain "
            "at least eight characters, including at least one "
            "number."
        )
        valid = False
    # Checks that the passwords match.
    if password != password_confirm:
        message.append("Passwords do not match!")
        valid = False

    return valid, message