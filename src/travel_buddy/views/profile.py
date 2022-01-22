"""
Handles the view for user profiles and related functionality.
"""

import sqlite3

import travel_buddy.helpers.helper_general as helper_general
from flask import Blueprint, redirect, render_template, request, session

profile_blueprint = Blueprint(
    "profile", __name__, static_folder="static", template_folder="templates"
)
DB_PATH = helper_general.get_database_path()


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
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT first_name, last_name, is_driver, bio, photo, verified "
            "FROM profile WHERE username=?;",
            (username,),
        )
        row = cur.fetchall()

        # Returns an error if the user doesn't exist.
        if len(row) == 0:
            message.append(
                f"The username {username} does not exist. Please ensure you "
                "have entered the name correctly."
            )
            session["prev-page"] = request.url
            session["error"] = message
            # TODO: Add HTML template for error page.
            return "<h1>Error</h1>"

        first_name, last_name, is_driver, bio, photo, verified = row[0]

    return render_template(
        "profile.html",
        first_name=first_name,
        last_name=last_name,
        is_driver=is_driver,
        bio=bio,
        avatar=photo,
        verified=verified,
    )
