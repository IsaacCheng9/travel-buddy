"""
Handles the view for the user registration system and related functionality.
"""

import sqlite3

import bcrypt
import travel_buddy.helpers.helper_register as helper_register
from flask import Blueprint, redirect, render_template, request, session

register_blueprint = Blueprint(
    "register", __name__, static_folder="static", template_folder="templates"
)


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
        verified = 0

        # Connects to the database to perform validation.
        with sqlite3.connect("db.sqlite3") as conn:
            cur = conn.cursor()
            valid, message = helper_register.validate_registration(
                cur,
                username,
                first_name,
                last_name,
                password,
                password_confirm,
            )
            # Registers the user if the details are valid.
            if valid is True:
                hash_password = bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt()
                )
                # Creates the user account in the database.
                cur.execute(
                    "INSERT INTO account (username, password, verified) "
                    "VALUES (?, ?, ?);",
                    (
                        username,
                        hash_password,
                        verified,
                    ),
                )
                # Creates the user profile in the database.
                cur.execute(
                    "INSERT into profile (username, first_name, last_name) "
                    "VALUES (?, ?, ?);",
                    (
                        username,
                        first_name,
                        last_name,
                    ),
                )
                conn.commit()

                session["username"] = username
                return redirect("/register")
            # Displays error message(s) stating why their details are invalid.
            else:
                details = [username, first_name, last_name]
                session["register_details"] = details
                session["error"] = message
                return redirect("/register")
