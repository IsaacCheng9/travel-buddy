"""
Handles the view for the user registration system and related functionality.
"""

from fileinput import filename
import sqlite3

import uuid
from flask import Blueprint, redirect, render_template, request, session

settings_blueprint = Blueprint(
    "settings", __name__, static_folder="static", template_folder="templates"
)


@settings_blueprint.route("/settings", methods=["GET", "POST"])
def settings() -> object:
    """
    Renders the user registration page, and registers an account using the
    user's input from the registration form.

    Returns:
        GET: The web page for user profile settings.
        POST: Modify the user settings and save them.
    """

    if not "username" in session:
        return redirect("/")

    with sqlite3.connect("db.sqlite3") as conn:
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
        avatar=photo,
        verified=verified,
    )


@settings_blueprint.route("/API_SetUserInfo", methods=["POST", "GET"])
def API_SetBio() -> object:
    """
    Modifies the user's bio and saves it to the database.

    Returns:
        200 - OK
        403 - FORBIDDEN PERMISSIONS
        405 - METHOD NOT ALLOWED
    """

    if not "username" in session:
        return "403"

    target_bio = request.args.get("bio")
    new_f_name = request.args.get("f_name")
    new_l_name = request.args.get("l_name")

    if len(target_bio) > 180:
        return "405"

    if len(new_f_name) > 20 or " " in new_f_name:
        return "405"

    if len(new_l_name) > 20 or " " in new_l_name:
        return "405"

    with sqlite3.connect("db.sqlite3") as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE profile SET bio=?, first_name=?, last_name=? WHERE username=?;",
            (target_bio, new_f_name, new_l_name, session["username"]),
        )

    return "200"


@settings_blueprint.route("/API_UploadAvatar", methods=["POST", "GET"])
def API_UploadAvatar() -> object:
    """
    Uploads the user's avatar to the database.

    Returns:
        200 - OK
        403 - FORBIDDEN PERMISSIONS
        405 - METHOD NOT ALLOWED (invalid file type)
    """

    if not "username" in session:
        return "403"

    file = request.files["file"]

    file_name = str(uuid.uuid4()) + ".png"

    file.save("static/avatars/" + file_name)

    with sqlite3.connect("db.sqlite3") as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE profile SET photo=? WHERE username=?;",
            (file_name, session["username"]),
        )

    return "200"
