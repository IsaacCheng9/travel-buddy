"""
Handles the view for carpool and related functionality, such as requesting a
carpool, offering carpooling, viewing carpools available, and viewing history
of carpools participated in.
"""

import travel_buddy.helpers.helper_carpool as helper_carpool
import travel_buddy.helpers.helper_general as helper_general

from flask import Blueprint, redirect, render_template, request, session
from travel_buddy.helpers.helper_limiter import limiter

import sqlite3

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

    interested_list = helper_carpool.get_user_interested_carpools(session["username"])

    if request.method == "GET":
        incomplete_carpools = [
            list(c) for c in helper_carpool.get_incomplete_carpools()
        ]
        for i, c in enumerate(incomplete_carpools):
            incomplete_carpools[i][6] = format(c[6], ".2f")
            start_time_obj = helper_carpool.get_datetime_obj(c[5])
            incomplete_carpools[i][5] = helper_carpool.format_start_time(start_time_obj)
            incomplete_carpools[i].append(
                helper_carpool.get_end_time(
                    helper_carpool.get_end_time_obj(start_time_obj, c[10])
                )
            )

        return render_template(
            "carpools.html",
            username=session.get("username"),
            carpools=incomplete_carpools,
            autocomplete_query=autocomplete_query,
            interested_list=interested_list,
        )

    if request.method == "POST":
        starting_point = request.form["location-from"].strip()
        destination = request.form["location-to"].strip()
        # Converts from date string input to date object.
        pickup_datetime = helper_general.string_to_date(request.form["date-from"])
        price = int(request.form["price"])
        description = request.form["description"]
        num_seats = int(request.form["seats"])
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

        valid, errors = helper_carpool.validate_carpool_ride(
            session["username"],
            num_seats,
            starting_point,
            destination,
            pickup_datetime,
            price,
            description,
            distance,
            duration,
            co2_saved,
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
            interested_list=interested_list,
        )


@carpool_blueprint.route("/toggle_carpool_interest/<id>", methods=["GET"])
@limiter.limit("2/second")
def toggle_carpool_interest(id):
    """
    Toggles whether the user is interested in carpooling.

    Args:
        id: The id of the carpool ride.

    Returns:
        New current state of the interest
    """
    if "username" not in session:
        return "null"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM carpool_interest WHERE journey_id=?", (id,))
        interested = cursor.fetchone()

        if interested:
            cursor.execute("DELETE FROM carpool_interest WHERE journey_id=?", (id,))
        else:
            cursor.execute(
                "INSERT INTO carpool_interest (journey_id, username) VALUES (?, ?)",
                (id, session["username"]),
            )

        conn.commit()

    return str(not interested)


@carpool_blueprint.route("/carpools/<journey_id>", methods=["GET"])
@limiter.limit("1/sec")
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
        duration,
        duration_text,
        co2_pp,
        co2_saved,
    ) = carpool_details

    pickup_datetime_obj = helper_carpool.get_datetime_obj(pickup_datetime)
    if 4 <= pickup_datetime_obj.day <= 20 or 24 <= pickup_datetime_obj.day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][pickup_datetime_obj.day % 10 - 1]
    end_datetime = helper_carpool.get_end_time_obj(pickup_datetime_obj, duration)
    end_hour, end_minute = end_datetime.hour, end_datetime.minute
    pickup_datetime = pickup_datetime_obj.strftime(
        f"%e{suffix} %B %Y %H:%M - {end_hour}:{end_minute}"
    )

    # Displays price with two decimal places.
    price = format(price, ".2f")

    # Gets the list of passengers for the carpool.
    passenger_list = helper_carpool.get_passenger_list(journey_id)

    average_rating, total_ratings = helper_general.get_user_rating(driver)

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
        journey_id=journey_id,
        avatar=helper_general.get_user_avatar(driver),
        rating_average=average_rating,
        rating_count=total_ratings,
        icons=helper_carpool.get_icons(description),
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
