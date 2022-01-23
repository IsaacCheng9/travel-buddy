"""
Handles the view for carpool and related functionality, such as requesting a
carpool, offering carpooling, viewing carpools available, and viewing history
of carpools participated in.
"""

import sqlite3

import travel_buddy.helpers.helper_carpool as helper_carpool
import travel_buddy.helpers.helper_general as helper_general
from flask import Blueprint, render_template, request, session
from travel_buddy.helpers.helper_limiter import limiter

carpool_blueprint = Blueprint(
    "carpool", __name__, static_folder="static", template_folder="templates"
)
DB_PATH = helper_general.get_database_path()


@carpool_blueprint.route("/carpools", methods=["GET", "POST"])
@limiter.limit("15/minute")
def carpools():
    """
    Displays carpools available to participate in.

    Returns:
        GET: The web page for viewing carpools.
        POST: Redirection to the page for the selected carpool listing.
    """
    if request.method == "GET":
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            carpools = helper_carpool.get_carpool_list(cur, session["username"])
            return render_template("carpools.html", carpools=carpools)

    if request.method == "POST":
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            location_from = request.form["location-from"]
            location_to = request.form["location-to"]
            # from date string to date object
            date_from = helper_general.string_to_date(request.form["date-from"])
            description = request.form["description"]
            seats = int(request.form["seats"])

            valid, errors = helper_carpool.validate_carpool_ride(
                cur,
                session["username"],
                seats,
                location_from,
                location_to,
                date_from,
                description,
            )
            carpools = helper_carpool.get_carpool_list(cur, session["username"])

            if valid:
                helper_carpool.add_carpool_ride(
                    cur,
                    session["username"],
                    seats,
                    location_from,
                    location_to,
                    date_from,
                    description,
                )
                return render_template("carpools.html", carpools=carpools)

            return render_template("carpools.html", errors=errors, carpools=carpools)
