"""
Handles the view for carpool and related functionality, such as requesting a
carpool, offering carpooling, viewing carpools available, and viewing history
of carpools participated in.
"""

import travel_buddy.helpers.helper_carpool as helper_carpool
import travel_buddy.helpers.helper_general as helper_general
from flask import Blueprint, redirect, render_template, request, session
from travel_buddy.helpers.helper_limiter import limiter

carpool_blueprint = Blueprint(
    "carpool", __name__, static_folder="static", template_folder="templates"
)
DB_PATH = helper_general.get_database_path()


@carpool_blueprint.route("/carpools", methods=["GET", "POST"])
@limiter.limit("15/minute")
def show_available_carpools():
    """
    Displays carpools available to participate in, and handles user input for
    adding a new offer for carpool ride.

    Returns:
        GET: The web page for viewing available carpools.
        POST: Adds the carpool ride to the database and redirects to the
              updated list of available carpools.
    """

    if "username" not in session:
        return redirect("/")

    autocomplete_query = helper_general.get_autocomplete_query(
        filename="keys.json", func="autocomplete_no_map"
    )

    if request.method == "GET":
        incomplete_carpools = helper_carpool.get_incomplete_carpools()
        return render_template(
            "carpools.html",
            username=session.get("username"),
            carpools=incomplete_carpools,
            autocomplete_query=autocomplete_query,
        )

    if request.method == "POST":
        starting_point = request.form["location-from"].strip()
        destination = request.form["location-to"].strip()
        # Converts from date string input to date object.
        pickup_datetime = helper_general.string_to_date(request.form["date-from"])
        price = int(request.form["price"])
        description = request.form["description"]
        num_seats = int(request.form["seats"])

        valid, errors = helper_carpool.validate_carpool_ride(
            session["username"],
            num_seats,
            starting_point,
            destination,
            pickup_datetime,
            price,
            description,
        )
        incomplete_carpools = helper_carpool.get_incomplete_carpools()

        # Displays errors if the submitted carpool ride is invalid.
        if valid:
            (
                distance,
                distance_text,
                duration,
                duration_text,
                co2_pp,
                co2_saved,
            ) = helper_carpool.estimate_carpool_details(
                starting_point, destination, num_seats + 1, "keys.json"
            )
            helper_carpool.add_carpool_ride(
                session["username"],
                num_seats,
                starting_point,
                destination,
                pickup_datetime,
                price,
                description,
                distance,
                distance_text,
                duration,
                duration_text,
                co2_pp,
                co2_saved,
            )
            return redirect("/carpools")
        return render_template(
            "carpools.html",
            username=session.get("username"),
            errors=errors,
            carpools=incomplete_carpools,
            autocomplete_query=autocomplete_query,
        )


@carpool_blueprint.route("/carpools/<journey_id>", methods=["GET"])
@limiter.limit("15/minute")
def view_carpool_journey(journey_id: int):
    """
    Displays the carpool journey selected by the user so that they can interact
    with it.

    Args:
        journey_id: The unique identifier for the selected carpool journey.

    Returns:
        The web page for viewing the selected carpool journey.
    """
    carpool_details = helper_carpool.get_carpool_details(journey_id)
    # Gets the carpool details if the journey ID exists, otherwise returns
    # an error.
    if not carpool_details:
        session["error"] = "Carpool journey does not exist."
        return render_template("view_carpool.html")
    (
        driver,
        is_complete,
        seats_initial,
        seats_available,
        starting_point,
        destination,
        pickup_datetime,
        price,
        description,
        distance_text,
        duration_text,
        co2_pp,
        co2_saved,
    ) = carpool_details

    # Displays price with two decimal places.
    price = format(price, ".2f")

    # Gets the list of passengers for the carpool.
    passenger_list = helper_carpool.get_passenger_list(journey_id)

    return render_template(
        "view_carpool.html",
        username=session.get("username"),
        driver=driver,
        is_complete=is_complete,
        seats_initial=seats_initial,
        seats_available=seats_available,
        starting_point=starting_point,
        destination=destination,
        pickup_datetime=pickup_datetime,
        price=price,
        description=description,
        distance_text=distance_text,
        duration_text=duration_text,
        co2_pp=co2_pp,
        co2_saved=co2_saved,
        passenger_list=passenger_list,
    )


@carpool_blueprint.route("/carpools/<journey_id>/join", methods=["POST"])
@limiter.limit("15/minute")
def join_carpool_journey(journey_id: int):
    """
    Adds the user as a passenger to the carpool journey.

    Args:
        journey_id: The unique identifier for the selected carpool.

    Returns:
        Redirection to the updated view of the carpool journey.
    """
    username = session["username"]

    # Checks whether the carpool can be joined by the user.
    valid, error_messages = helper_carpool.validate_joining_carpool(
        journey_id, username
    )
    if not valid:
        session["error"] = error_messages
        return redirect("/carpools/{journey_id}/")
    # Adds the user as a passenger to the carpool journey if validation
    # passed.
    helper_carpool.add_passenger_to_carpool_journey(journey_id, username)

    return redirect("/carpools/{journey_id}/")
