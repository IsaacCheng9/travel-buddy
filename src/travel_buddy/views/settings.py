"""
Handles the view for changing user settings and related functionality.
"""

import sqlite3
import uuid

import travel_buddy.helpers.helper_general as helper_general
from travel_buddy.helpers.helper_limiter import limiter
from flask import Blueprint, redirect, render_template, request, session

settings_blueprint = Blueprint(
    "settings", __name__, static_folder="static", template_folder="templates"
)
limiter.limit("1/second")(settings_blueprint)
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
            "SELECT first_name, last_name, is_driver, bio, photo, verified "
            "FROM profile WHERE username=?;",
            (session["username"],),
        )
        first_name, last_name, is_driver, bio, photo, verified = cur.fetchone()

    return render_template(
        "settings.html",
        bio=bio,
        first_name=first_name,
        last_name=last_name,
        is_driver=is_driver,
        avatar=photo,
        verified=verified,
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

    if len(new_bio) > 180:
        return "405"

    if len(new_f_name) > 20 or " " in new_f_name:
        return "405"

    if len(new_l_name) > 20 or " " in new_l_name:
        return "405"

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE profile SET bio=?, first_name=?, last_name=? WHERE username=?;",
            (new_bio, new_f_name, new_l_name, session["username"]),
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
    file_name = str(uuid.uuid4()) + ".png"
    file.save("static/avatars/" + file_name)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE profile SET photo=? WHERE username=?;",
            (file_name, session["username"]),
        )

    return "200"
