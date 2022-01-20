"""
Handles the view for the route details check functionality
"""

import travel_buddy.helpers.helper_routes as helper_routes
from flask import Blueprint, redirect, render_template, request, session

import logging

routes_blueprint = Blueprint(
    "routes", __name__, static_folder="static", template_folder="templates"
)


@routes_blueprint.route("/routes", methods=["GET", "POST"])
def routes() -> object:
    """
    Generates information on route details utilising google maps api funtions in helper_routes.
    Returns view populated with data.
    """
    if request.method == "GET":
        return render_template("routes.html", distance_range=None, details=None,origin=None,destination=None)

    elif request.method == "POST":
        origins = request.form["start_point"]
        destinations = request.form["destination"]
        mode = request.form["mode"]
        print(origins, destinations, mode)

        API_KEY_FILE = "keys.json"
        KEYS = helper_routes.get_keys(API_KEY_FILE)
        map_client = helper_routes.generate_client(KEYS["google_maps"])
        if map_client is None:
            # TODO error
            return
        route_data = {}
        modes = ("walking","driving","bicycling","transit")

        route_data = {m: helper_routes.run_api(map_client, origins, destinations, m) for m in modes}

        details = {
            "origin": helper_routes.safeget(
                route_data, "walking", "origin_addresses", 0
            ),
            "destination": helper_routes.safeget(
                route_data, "walking", "destination_addresses", 0
            ),
            "modes": {}
        }

        data = ("distance","duration")

        details["modes"] = {m: {d: helper_routes.safeget(route_data, m, "rows", 0, "elements", 0, d) for d in data} for m in modes}

        print(details)

        distances = {
            k: helper_routes.safeget(v, "distance", "value")
            for k, v in helper_routes.safeget(details, "modes").items()
            if helper_routes.safeget(v, "distance", "value") is not None
        }
        try:
            sorted_keys = sorted(distances, key=distances.get)
            lowest, highest = helper_routes.safeget(
                details, "modes", sorted_keys[0], "distance", "text"
            ), helper_routes.safeget(
                details, "modes", sorted_keys[-1], "distance", "text"
            )
            distance_range = f"{lowest} - {highest}"
        except Exception as e:
            distance_range = "Unknown"
            logging.warning(f"Failed to find shortest and longest distances - {e}")

        address1, address2 = helper_routes.safeget(
            details, "origin"
        ), helper_routes.safeget(details, "destination")

        return render_template(
            "routes.html",
            distance_range=distance_range,
            details=details,
            origin=address1,
            destination=address2,
        )
