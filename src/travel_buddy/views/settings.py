"""
Handles the view for changing user settings and related functionality.
"""

import sqlite3

import travel_buddy.helpers.helper_general as helper_general
from flask import Blueprint, redirect, render_template, request, session
from travel_buddy.helpers.helper_limiter import limiter

settings_blueprint = Blueprint(
    "settings", __name__, static_folder="static", template_folder="templates"
)
DB_PATH = helper_general.get_database_path()


@settings_blueprint.route("/settings", methods=["GET", "POST"])
def settings() -> object:
    """
    Renders the settings page, and makes the changes accordingly.

    Returns:
        GET: The web page for user profile settings.
        POST: Modify the user settings and save them.
    """

    if "username" not in session:
        return redirect("/")

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT first_name, last_name, is_driver, bio, photo, verified, home, work "
            "FROM profile WHERE username=?;",
            (session["username"],),
        )
        (
            first_name,
            last_name,
            is_driver,
            bio,
            photo,
            verified,
            home,
            work,
        ) = cur.fetchone()
        cur.execute(
            "SELECT make, mpg, fuel_type, engine_size " "FROM car WHERE owner=?;",
            (session["username"],),
        )
        make, mpg, fuel_type, engine_size = cur.fetchone()
        autocomplete_query = helper_general.get_autocomplete_query(
            filename="keys.json", func="autocomplete_no_map"
        )
    return render_template(
        "settings.html",
        username=session.get("username"),
        autocomplete_query=autocomplete_query,
        bio=bio,
        first_name=first_name,
        last_name=last_name,
        is_driver=is_driver,
        avatar=photo,
        verified=verified,
        make=make,
        mpg=mpg,
        fuel_type=fuel_type,
        engine_size=engine_size,
        home=home,
        work=work,
    )


@settings_blueprint.route("/settings/edit-user-details", methods=["POST", "GET"])
def edit_user_details() -> object:
    """
    Modifies the user's profile details and saves it to the database.

    Returns:
        200 - OK
        403 - FORBIDDEN PERMISSIONS
        405 - METHOD NOT ALLOWED
    """

    if "username" not in session:
        return "403"

    new_bio = request.args.get("bio")
    new_f_name = request.args.get("f_name")
    new_l_name = request.args.get("l_name")
    new_home = request.args.get("home")
    new_work = request.args.get("work")

    if len(new_bio) > 180:
        return "405"

    if len(new_f_name) > 20 or " " in new_f_name:
        return "405"

    if len(new_l_name) > 20 or " " in new_l_name:
        return "405"

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        if new_home is not None and new_work is not None:
            cur.execute(
                "UPDATE profile SET bio=?, first_name=?, last_name=?, home=?, work=? WHERE username=?;",
                (
                    new_bio,
                    new_f_name,
                    new_l_name,
                    new_home,
                    new_work,
                    session["username"],
                ),
            )
        else:
            cur.execute(
                "UPDATE profile SET bio=?, first_name=?, last_name=? WHERE username=?;",
                (new_bio, new_f_name, new_l_name, session["username"]),
            )

    return "200"


@settings_blueprint.route("/settings/edit-car-details", methods=["POST", "GET"])
def edit_car_details() -> object:
    """
    Modifies the user's car details and saves it to the database.

    Returns:
        200 - OK
        403 - FORBIDDEN PERMISSIONS
        405 - METHOD NOT ALLOWED
    """

    if "username" not in session:
        return "403"

    make = request.args.get("make")
    mpg = request.args.get("mpg")
    fuel_type = request.args.get("fuel")
    engine_size = request.args.get("engine_size")

    if len(make) > 50:
        return "405"

    if len(mpg) > 3 or " " in mpg:
        return "405"

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE car SET make=?, mpg=?, fuel_type=?, engine_size=? WHERE owner=?;",
            (make, mpg, fuel_type, engine_size, session["username"]),
        )
    return "200"


@settings_blueprint.route("/settings/upload-avatar", methods=["POST", "GET"])
def edit_avatar() -> object:
    """
    Uploads the user's avatar to the database.

    Returns:
        200 - OK
        403 - FORBIDDEN PERMISSIONS
        405 - METHOD NOT ALLOWED (invalid file type)
    """
    if "username" not in session:
        return "403"

    file = request.files["file"]
    valid, message, file_name_hashed = helper_general.hash_image(file)

    if valid:
        # Adds the user's avatar to the database.
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE profile SET photo=? WHERE username=?;",
                (file_name_hashed, session["username"]),
            )
            conn.commit()
        return "200"

    session["error"] = message
    return "400"
