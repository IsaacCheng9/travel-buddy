"""
Handles the view for user profiles and related functionality.
"""

import sqlite3

import travel_buddy.helpers.helper_general as helper_general
import travel_buddy.helpers.helper_register as helper_register
from flask import Blueprint, redirect, render_template, request, session
from travel_buddy.helpers.helper_limiter import limiter

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
@limiter.limit("30/minute")
def profile(username: str) -> object:
    """
    Displays the user's profile page and fills in all of the necessary
    details.

    Args:
        username: The user to view the profile of.

    Returns:
        The updated web page based on whether the details provided were valid.
    """

    if "username" not in session:
        return redirect("/")

    message = []

    # Gets the user's details from the database.
    with sqlite3.connect(DB_PATH) as conn:

        profile_data, message = get_profile(conn, username, message)
        profile_stats, message = get_stats(conn, username, message)

        if message:
            # TODO: Add HTML template for error page.
            return "".join([f"<h1>{m}</h1>" for m in message])

        search_count = helper_register.get_route_search_count(conn, username)

    first_name, last_name, is_driver, bio, photo, verified = profile_data
    (
        distance_travelled,
        carpools_driven,
        carpools_rode,
        money_saved,
        co2_saved,
        join_date,
    ) = profile_stats
    tree_offset = helper_general.co2_to_trees(co2_saved, 365)

    return render_template(
        "profile.html",
        first_name=first_name,
        last_name=last_name,
        is_driver=is_driver,
        bio=bio,
        avatar=photo,
        verified=verified,
        distance_travelled=distance_travelled,
        carpools_driven=carpools_driven,
        carpools_rode=carpools_rode,
        money_saved=money_saved,
        co2_saved=co2_saved,
        join_date=join_date,
        search_count=search_count,
        tree_offset=tree_offset,
    )


def get_stats(conn, username, message):
    cur = conn.cursor()
    cur.execute(
        "SELECT distance_travelled, carpools_driven, carpools_rode, money_saved, co2_saved, join_date "
        "FROM stats WHERE username=?;",
        (username,),
    )
    row = cur.fetchone()
    # Returns an error if the user doesn't exist.
    if not row:
        message.append(
            f"The username {username} does not exist. Please ensure you "
            "have entered the name correctly."
        )
        session["prev-page"] = request.url

    return row, message


def get_profile(conn, username, message):
    cur = conn.cursor()
    cur.execute(
        "SELECT first_name, last_name, is_driver, bio, photo, verified "
        "FROM profile WHERE username=?;",
        (username,),
    )
    row = cur.fetchone()
    # Returns an error if the user doesn't exist.
    if not row:
        message.append(
            f"The username {username} does not exist. Please ensure you "
            "have entered the name correctly."
        )
        session["prev-page"] = request.url
        # session["error"] = message

    return row, message
