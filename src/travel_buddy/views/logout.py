"""
Handles the view for the user registration system and related functionality.
"""

import sqlite3

import bcrypt
from flask import Blueprint, redirect, render_template, request, session

logout_blueprint = Blueprint(
    "logout", __name__, static_folder="static", template_folder="templates"
)


@logout_blueprint.route("/logout", methods=["GET", "POST"])
def logout() -> object:
    """
    Logs the user out and redirects them to the home page

    Returns:
        Redirect for the home page
    """

    if "username" in session:
        session.pop("username", None)

    return redirect("/")
