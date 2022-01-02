import sqlite3

import travel_buddy.helpers.helper_register as helper_register
from flask import Blueprint, redirect, render_template, request, session
from passlib.hash import sha256_crypt

register_blueprint = Blueprint(
    "register", __name__, static_folder="static", template_folder="templates"
)


@register_blueprint.route("/register", methods=["GET", "POST"])
def register() -> object:
    """
    Renders the user registration page.

    Returns:
        The web page for user registration.
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
                hash_password = sha256_crypt.hash(password)
                cur.execute(
                    "INSERT INTO account (username, first_name, last_name, password, "
                    "verified) VALUES (?, ?, ?, ?, ?);",
                    (
                        username,
                        first_name,
                        last_name,
                        hash_password,
                        verified,
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
