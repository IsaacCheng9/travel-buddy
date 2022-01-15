"""
Handles the view for user profiles and related functionality.
"""

import sqlite3

from flask import Blueprint, redirect, render_template, request, session

profile_blueprint = Blueprint(
    "profile", __name__, static_folder="static", template_folder="templates"
)


@profile_blueprint.route("/profile", methods=["GET"])
def my_profile() -> object:
    """
    Checks the user is logged in before viewing their profile page.

    Returns:
        Redirection to their profile if they're logged in.
    """
    if "username" in session:
        return redirect("/profile/" + session["username"])

    return redirect("/")


@profile_blueprint.route("/profile/<username>", methods=["GET"])
def profile(username: str) -> object:
    """
    Displays the user's profile page and fills in all of the necessary
    details.

    Args:
        username: The user to view the profile of.

    Returns:
        The updated web page based on whether the details provided were valid.
    """
    message = []

    # Gets the user's details from the database.
    with sqlite3.connect("db.sqlite3") as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT first_name, last_name, is_driver, bio, photo FROM profile "
            "WHERE username=?;",
            (username,),
        )
        row = cur.fetchall()
        if len(row) == 0:
            message.append(
                f"The username {username} does not exist. Please ensure you "
                "have entered the name correctly."
            )
            session["prev-page"] = request.url
            session["error"] = message
            # TODO: Add HTML template for error page.
            return "<h1>Error</h1>"
        else:
            first_name, last_name, is_driver, bio, photo = row[0]

    return render_template("profile.html")
