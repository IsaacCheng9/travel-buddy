import os

from flask import Flask, redirect, request, session

import travel_buddy.views.carpool as carpool
import travel_buddy.views.login as login
import travel_buddy.views.profile as profile
import travel_buddy.views.register as register
import travel_buddy.views.settings as settings


def create_app() -> Flask:
    """
    Creates an instance of the Flask web application.

    Returns:
        An instance of the web application with the blueprints configured.
    """
    app = Flask(__name__)
    app.register_blueprint(register.register_blueprint, url_prefix="")
    app.register_blueprint(login.login_blueprint, url_prefix="")
    app.register_blueprint(profile.profile_blueprint, url_prefix="")
    app.register_blueprint(settings.settings_blueprint, url_prefix="")
    app.register_blueprint(carpool.carpool_blueprint, url_prefix="")

    app.url_map.strict_slashes = False
    app.secret_key = (
        "i09kd0owe671gdyfjkzmpaopmrionfkwep]l[';fkvfoiejiojd1u232e23fkeorincuiwkdu"
    )
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
