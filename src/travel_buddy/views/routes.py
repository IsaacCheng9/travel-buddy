"""
Handles the view for the route details check functionality
"""

import travel_buddy.helpers.helper_routes as helper_routes
from flask import Blueprint, redirect, render_template, request, session

routes_blueprint = Blueprint(
    "routes", __name__, static_folder="static", template_folder="templates"
)


@routes_blueprint.route("/routes", methods=["GET", "POST"])
def routes() -> object:
    if request.method == "GET":
        return render_template("routes.html", distance_range="", details={})

    elif request.method == "POST":
        origins = request.form["start_point"]
        destinations = request.form["destination"]
        mode = request.form["mode"]
        print(origins, destinations, mode)

        API_KEY_FILE = "keys.json"
        KEYS = helper_routes.get_keys(API_KEY_FILE)
        map_client = helper_routes.generate_client(KEYS["google_maps"])
        route_data = {}
        route_data["walking"] = helper_routes.run_api(
            map_client, origins, destinations, "walking"
        )
        print("route", route_data)
        route_data["driving"] = helper_routes.run_api(
            map_client, origins, destinations, "driving"
        )
        route_data["cycling"] = helper_routes.run_api(
            map_client, origins, destinations, "bicycling"
        )
        route_data["transit"] = helper_routes.run_api(
            map_client, origins, destinations, "transit"
        )

        details = {
            "walking": {
                "distance": helper_routes.safeget(
                    route_data, "walking", "rows", 0, "elements", 0, "distance"
                ),
                "duration": helper_routes.safeget(
                    route_data, "walking", "rows", 0, "elements", 0, "duration"
                ),
            },
            "driving": {
                "distance": helper_routes.safeget(
                    route_data, "driving", "rows", 0, "elements", 0, "distance"
                ),
                "duration": helper_routes.safeget(
                    route_data, "driving", "rows", 0, "elements", 0, "duration"
                ),
            },
            "cycling": {
                "distance": helper_routes.safeget(
                    route_data, "cycling", "rows", 0, "elements", 0, "distance"
                ),
                "duration": helper_routes.safeget(
                    route_data, "cycling", "rows", 0, "elements", 0, "duration"
                ),
            },
            "transit": {
                "distance": helper_routes.safeget(
                    route_data, "transit", "rows", 0, "elements", 0, "distance"
                ),
                "duration": helper_routes.safeget(
                    route_data, "transit", "rows", 0, "elements", 0, "duration"
                ),
            },
        }
        print(details)

        distances = {k: v["distance"]["value"] for k, v in details.items()}
        sorted_keys = sorted(distances, key=distances.get)
        lowest, highest = helper_routes.safeget(
            details, sorted_keys[0], "distance", "text"
        ), helper_routes.safeget(details, sorted_keys[-1], "distance", "text")
        range = f"{lowest} - {highest}"

        return render_template("routes.html", distance_range=range, details=details)
