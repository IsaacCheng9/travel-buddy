from flask import Flask

import travel_buddy.helpers.helper_general as helper_general
import travel_buddy.views.carpool as carpool
import travel_buddy.views.login as login
import travel_buddy.views.profile as profile
import travel_buddy.views.register as register
import travel_buddy.views.routes as routes
import travel_buddy.views.settings as settings
import travel_buddy.views.trends as trends
from travel_buddy.helpers.helper_limiter import limiter

API_KEY_FILE = "keys.json"
KEYS = helper_general.get_keys(API_KEY_FILE)


def create_app() -> Flask:
    """
    Creates an instance of the Flask web application.

    Returns:
        An instance of the web application with the blueprints configured.
    """
    app = Flask(__name__)
    limiter.init_app(app)
    app.register_blueprint(register.register_blueprint, url_prefix="")
    app.register_blueprint(login.login_blueprint, url_prefix="")
    app.register_blueprint(profile.profile_blueprint, url_prefix="")
    app.register_blueprint(routes.routes_blueprint, url_prefix="")
    app.register_blueprint(settings.settings_blueprint, url_prefix="")
    app.register_blueprint(carpool.carpool_blueprint, url_prefix="")
    app.register_blueprint(trends.trends_blueprint, url_prefix="")

    app.url_map.strict_slashes = False
    app.secret_key = KEYS["app_secret_key"]
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
