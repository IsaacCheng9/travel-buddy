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


@carpool_blueprint.route("/carpools/<journey_id>", methods=["GET"])
@limiter.limit("15/minute")
def view_carpool_journey(journey_id: int):
    """
    Displays the carpool journey selected by the user so that they can interact
    with it.

    Args:
        journey_id: The unique identifier for the selected carpool.

    Returns:
        The web page for viewing the selected carpool.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM carpool_ride WHERE journey_id=?;", (journey_id,))
        conn.commit()
        carpool_details = cur.fetchone()

        # Gets the carpool details if the journey ID exists, otherwise returns
        # an error.
        if not carpool_details:
            session["error"] = ["login"]
            return render_template("view_carpool.html")
        (
            driver,
            is_complete,
            seats_available,
            starting_point,
            destination,
            pickup_datetime,
            description,
        ) = carpool_details[0]

    return render_template(
        "view_carpool.html",
        driver=driver,
        is_complete=is_complete,
        seats_available=seats_available,
        starting_point=starting_point,
        destination=destination,
        pickup_datetime=pickup_datetime,
        description=description,
    )
