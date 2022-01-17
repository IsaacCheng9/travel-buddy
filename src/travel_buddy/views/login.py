"""
Handles the view for the user login system and related functionality.
"""

import sqlite3

import travel_buddy.helpers.helper_login as helper_login
from flask import Blueprint, redirect, render_template, request, session

login_blueprint = Blueprint(
    "login", __name__, static_folder="static", template_folder="templates"
)

@login_blueprint.route("/", methods=["GET", "POST"])
def login_page() -> object:
    """
    Renders the login page and validates the user's login details.

    Returns:
         GET: The web page for user login.
         POST: Redirection depending on whether login was successful or not.
    """
    if request.method == "GET":
        errors = []
        if "username" in session:
            return redirect("/profile")
        else:
            if "error" in session:
                errors = session["error"]
            session["prev-page"] = request.url
            # Clear error session variables.
            session.pop("error", None)
            return render_template("login.html", errors=errors)

    elif request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        with sqlite3.connect("db.sqlite3") as conn:
            cur = conn.cursor()
            # Gets user from database using username.
            cur.execute("SELECT password FROM account WHERE username=?;", (username,))
            conn.commit()
            row = cur.fetchone()
        # Gets the password if it exists, otherwise returns an error as the
        # username doesn't exist.
        if row:
            hashed_password = row[0]
        else:
            session["error"] = ["login"]
            return render_template("login.html")

        if hashed_password:
            # Checks whether the password is correct for that user.
            if helper_login.authenticate_password(password, hashed_password):
                session["username"] = username
                session["prev-page"] = request.url
                return redirect("/profile")
            else:
                session["error"] = ["login"]
                return render_template("login.html")
        else:
            session["error"] = ["login"]
            return render_template("login.html")
