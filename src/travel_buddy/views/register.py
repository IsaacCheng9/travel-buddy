import sqlite3

from flask import Blueprint, redirect, render_template, request, session

register_blueprint = Blueprint(
    "register", __name__, static_folder="static", template_folder="templates"
)


@register_blueprint.route("/register", methods=["GET, POST"])
def register() -> object:
    """
    Renders the user registration page.

    Returns:
        The web page for user registration.
    """
    if request.method == "GET":
        pass

    else:
        pass
