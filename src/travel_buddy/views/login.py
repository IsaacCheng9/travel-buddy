"""
Handles the view for the user login system and related functionality.
"""

import sqlite3

from flask import Blueprint, redirect, render_template, request, session
import bcrypt

login_blueprint = Blueprint(
    "login", __name__, static_folder="static", template_folder="templates"
)


@login_blueprint.route("/", methods=["GET", "POST"])
def login_page() -> object:
    """
    Renders the login page and validates the user's login details.

    Returns:
         GET: The web page for user login.
         POST: Redirection depending on whether login was successful or not.
    """
    if request.method == "GET":
        errors = []
        if "username" in session:
            return redirect("/profile")
        else:
            if "error" in session:
                errors = session["error"]
            session["prev-page"] = request.url
            # Clear error session variables.
            session.pop("error", None)
            return render_template("login.html", errors=errors)

    elif request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"].encode("utf-8")

        with sqlite3.connect("db.sqlite3") as conn:
            cur = conn.cursor()
            # Gets user from database using username.
            cur.execute("SELECT password FROM account WHERE username=?;", (username,))
            conn.commit()
            row = cur.fetchone()

        if row:
            hashed_password = row[0]
        else:
            session["error"] = ["login"]
            return redirect("/")

        if hashed_password:
            if bcrypt.checkpw(password, hashed_password):
                session["username"] = username
                session["prev-page"] = request.url
                return redirect("/profile")
            else:
                session["error"] = ["login"]
                return redirect("/")
        else:
            session["error"] = ["login"]
            return redirect("/")
