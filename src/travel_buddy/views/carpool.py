"""
Handles the view for carpool and related functionality, such as requesting a
carpool, offering carpooling, viewing carpools available, and viewing history
of carpools participated in.
"""

import sqlite3

import travel_buddy.helpers.helper_carpool as helper_carpool
import travel_buddy.helpers.helper_general as helper_general
from flask import Blueprint, render_template, request
from travel_buddy.helpers.helper_limiter import limiter

carpool_blueprint = Blueprint(
    "carpool", __name__, static_folder="static", template_folder="templates"
)
DB_PATH = helper_general.get_database_path()


@carpool_blueprint.route("/carpools", methods=["GET"])
@limiter.limit("15/minute")
def carpools():
    """
    Displays carpools available to participate in.

    Returns:
        GET: The web page for viewing carpools.
        POST: Redirection to the page for the selected carpool listing.
    """
    if request.method == "GET":
        return render_template("carpools.html")

    elif request.method == "POST":
        return "<h1>Carpool listing here</h1>"
