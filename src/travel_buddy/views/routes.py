"""
Handles the view for the route details check functionality
"""

import travel_buddy.helpers.helper_routes as helper_routes
import travel_buddy.helpers.helper_general as helper_general
from flask import Blueprint, render_template, request

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

    API_KEY_FILE = "keys.json"
    KEYS = helper_general.get_keys(API_KEY_FILE)
    AUTOCOMPLETE_QUERY = f"https://maps.googleapis.com/maps/api/js?key={KEYS['google_maps']}&callback=initMap&libraries=places&v=weekly"

    if request.method == "GET":
        MAP_QUERY = f"https://www.google.com/maps/embed/v1/view?key={KEYS['google_maps']}&center=50.9,-1.4&zoom=8"

        return render_template(
            "routes.html", MAP_QUERY=MAP_QUERY, AUTOCOMPLETE_QUERY=AUTOCOMPLETE_QUERY
        )

    elif request.method == "POST":
        origins = request.form["start_point"].strip()
        destinations = request.form["destination"].strip()
        travel_mode = request.form["mode"]
        if travel_mode == "cycling":
            travel_mode = "bicycling"

        map_client = helper_routes.generate_client(KEYS["google_maps"])
        if map_client is None:
            # TODO error
            logging.warning(f"Failed to generate maps api client")
            return
        route_data = {}
        modes = ("walking", "driving", "bicycling", "transit")

        route_data = {
            m: helper_routes.run_api(map_client, origins, destinations, m)
            for m in modes
        }

        details = {
            "origin": helper_routes.safeget(
                route_data, "walking", "origin_addresses", 0
            ),
            "destination": helper_routes.safeget(
                route_data, "walking", "destination_addresses", 0
            ),
            "modes": {},
        }

        data = ("distance", "duration")

        details["modes"] = {
            m: {
                d: helper_routes.safeget(route_data, m, "rows", 0, "elements", 0, d)
                for d in data
            }
            for m in modes
        }

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
            if lowest == highest:
                distance_range = lowest
            else:
                distance_range = f"{lowest} - {highest}"
        except Exception as e:
            distance_range = "Unknown"
            logging.warning(f"Failed to find shortest and longest distances - {e}")

        address1, address2 = helper_routes.safeget(
            details, "origin"
        ), helper_routes.safeget(details, "destination")

        origin_convert = address1.replace(" ", "+")
        destination_convert = address2.replace(" ", "+")

        MAP_QUERY = f"https://www.google.com/maps/embed/v1/directions?key={KEYS['google_maps']}&origin={origin_convert}&destination={destination_convert}&mode={travel_mode}&units=metric"

        return render_template(
            "routes_display.html",
            distance_range=distance_range,
            details=details,
            origin=address1,
            destination=address2,
            MAP_QUERY=MAP_QUERY,
            AUTOCOMPLETE_QUERY=AUTOCOMPLETE_QUERY,
        )
