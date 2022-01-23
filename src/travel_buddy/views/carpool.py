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
    Displays carpools available to participate in, and handles user input for
    adding a new offer for carpool ride.

    Returns:
        GET: The web page for viewing available carpools.
        POST: Adds the carpool ride to the database and redirects to the
              updated list of available carpools.
    """
    if request.method == "GET":
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            incomplete_carpools = helper_carpool.get_incomplete_carpools(cur)
            return render_template("carpools.html", carpools=incomplete_carpools)

    if request.method == "POST":
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            location_from = request.form["location-from"]
            location_to = request.form["location-to"]
            # Converts from date string input to date object.
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
            incomplete_carpools = helper_carpool.get_incomplete_carpools(cur)

            # Displays errors if the submitted carpool ride is invalid.
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
                return render_template("carpools.html", carpools=incomplete_carpools)
            return render_template(
                "carpools.html", errors=errors, carpools=incomplete_carpools
            )
