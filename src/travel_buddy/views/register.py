"""
Handles the view for the user registration system and related functionality.
"""

import travel_buddy.helpers.helper_general as helper_general
import travel_buddy.helpers.helper_register as helper_register
from flask import Blueprint, redirect, render_template, request, session
from travel_buddy.helpers.helper_limiter import limiter

register_blueprint = Blueprint(
    "register", __name__, static_folder="static", template_folder="templates"
)
DB_PATH = helper_general.get_database_path()


@register_blueprint.route("/register", methods=["GET", "POST"])
def register() -> object:
    """
    Renders the user registration page, and registers an account using the
    user's input from the registration form.

    Returns:
        GET: The web page for user registration.
        POST: The web page based on whether the details provided were valid.
    """
    if request.method == "GET":
        errors = ""
        if "username" in session:
            return redirect("/profile")
        else:
            if "error" in session:
                errors = session["error"]
            session.pop("error", None)
            session["prev-page"] = request.url

            if "register_details" in session:
                details = session["register_details"]
            else:
                details = ["", "", ""]
            return render_template(
                "register.html",
                errors=errors,
                details=details,
            )

    elif request.method == "POST":
        # Obtains user input from the account registration form.
        username = request.form["username"].lower()
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        password = request.form["password1"]
        password_confirm = request.form["password2"]

        valid, message = helper_register.validate_registration(
            username,
            first_name,
            last_name,
            password,
            password_confirm,
        )
        # Registers the user if the details are valid.
        if valid is True:
            # Hashes the password using bcrypt.
            hashed_password = helper_register.hash_password(password)
            # Inserts the user to the database tables.
            helper_register.register_user(
                username, hashed_password, first_name, last_name
            )
            session["username"] = username
            return redirect("/register")
        # Displays error message(s) stating why their details are invalid.
        else:
            details = [username, first_name, last_name]
            session["register_details"] = details
            session["error"] = message
            return redirect("/register")
