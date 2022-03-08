"""
Handles the view for user profiles and related functionality.
"""

import sqlite3
from typing import List, Tuple

import travel_buddy.helpers.helper_general as helper_general
import travel_buddy.helpers.helper_carpool as helper_carpool
import travel_buddy.helpers.helper_routes as helper_routes
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
        if message:
            # TODO: Add HTML template for error page.
            return "".join([f"<h1>{m}</h1>" for m in message])

    first_name, last_name, is_driver, bio, photo, verified, join_date = profile_data

    carpools_joined = helper_carpool.get_total_carpools_joined(username)
    carpools_driven = helper_carpool.get_total_carpools_drove(username)
    distance_travelled = helper_carpool.get_total_distance_carpooled(username)
    co2_saved = helper_carpool.get_total_co2_saved(username)
    fuel_money_saved = helper_carpool.get_money_saved(username)
    tree_offset = helper_general.co2_to_trees(co2_saved, 365)
    routes_searched, unique_routes_searched = helper_routes.get_total_routes_searched(
        username
    )

    return render_template(
        "profile.html",
        username=session.get("username"),
        first_name=first_name,
        last_name=last_name,
        is_driver=is_driver,
        bio=bio,
        avatar=photo,
        verified=verified,
        distance_travelled=distance_travelled,
        carpools_driven=carpools_driven,
        carpools_joined=carpools_joined,
        fuel_money_saved=fuel_money_saved,
        co2_saved=co2_saved,
        join_date=join_date,
        routes_searched=routes_searched,
        unique_routes_searched=unique_routes_searched,
        tree_offset=tree_offset,
    )


def get_profile(
    conn, username: str, message: List[str]
) -> Tuple[Tuple[str, str, int, str, str, int, str], List[str]]:
    """
    Fetch the profile details of the user from the 'profile' table
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT first_name, last_name, is_driver, bio, photo, verified, join_date "
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
