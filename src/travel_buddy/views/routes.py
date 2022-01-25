"""
Handles the view for the route details check functionality
"""

import logging

import travel_buddy.helpers.helper_general as helper_general
import travel_buddy.helpers.helper_routes as helper_routes
from flask import Blueprint, render_template, request
from travel_buddy.helpers.helper_limiter import limiter

routes_blueprint = Blueprint(
    "routes", __name__, static_folder="static", template_folder="templates"
)


@routes_blueprint.route("/routes", methods=["GET", "POST"])
@limiter.limit("6/minute")
def routes() -> object:
    """
    Generates information on route details using Google Maps API functions.

    Returns:
        A view populated with data about travel times.
    """
    API_KEY_FILE = "keys.json"
    KEYS = helper_general.get_keys(API_KEY_FILE)
    AUTOCOMPLETE_QUERY = (
        f"https://maps.googleapis.com/maps/api/js"
        f"?key={KEYS['google_maps']}&callback=initMap&libraries=places&v=weekly"
    )

    if request.method == "GET":
        MAP_QUERY = (
            f"https://www.google.com/maps/embed/v1/view"
            f"?key={KEYS['google_maps']}&center=50.9,-1.4&zoom=8"
        )
        return render_template(
            "routes.html", MAP_QUERY=MAP_QUERY, AUTOCOMPLETE_QUERY=AUTOCOMPLETE_QUERY
        )

    elif request.method == "POST":
        origins = request.form["start_point"].strip()
        destinations = request.form["destination"].strip()
        travel_mode = request.form["mode"]
        if travel_mode == "cycling":
            travel_mode = "bicycling"

        # Generates the Google Maps API client to get data on routes using
        # different modes of transport.
        map_client = helper_routes.generate_client(KEYS["google_maps"])
        if map_client is None:
            # TODO error
            logging.warning(f"Failed to generate maps api client")
            return
        route_data = {}
        modes = ("walking", "driving", "bicycling", "transit")

        # Gets the distances and durations for each mode of transport.
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

        # Finds the shortest and longest distances from the routes.
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

        # Gets the full address of the origin and destination.
        address1, address2 = helper_routes.safeget(
            details, "origin"
        ), helper_routes.safeget(details, "destination")

        # Displays Google Map preview for the selected mode of transport.
        origin_convert = address1.replace(" ", "+")
        destination_convert = address2.replace(" ", "+")
        MAP_QUERY = (
            f"https://www.google.com/maps/embed/v1/directions"
            f"?key={KEYS['google_maps']}&origin={origin_convert}"
            f"&destination={destination_convert}&mode={travel_mode}&units=metric"
        )

        # Fetches the user's car information and calculates the fuel cost and
        # consumption for the journey.
        car_make, car_mpg, fuel_type = helper_routes.get_car()
        driving_distance = float(
            details["modes"]["driving"]["distance"]["value"] / 1000
        )
        distance = helper_routes.convert_km_to_miles(driving_distance)
        fuel_used = round(
            helper_routes.calculate_fuel_consumption(car_mpg, distance), 2
        )
        fuel_cost = round(helper_routes.calculate_fuel_cost(fuel_used, fuel_type), 2)
        fuel_price = round(helper_routes.get_fuel_price(fuel_type), 2)

        return render_template(
            "routes_display.html",
            distance_range=distance_range,
            details=details,
            origin=address1,
            destination=address2,
            MAP_QUERY=MAP_QUERY,
            AUTOCOMPLETE_QUERY=AUTOCOMPLETE_QUERY,
            fuel_used=fuel_used,
            fuel_cost=fuel_cost,
            car_make=car_make,
            car_mpg=car_mpg,
            fuel_price=fuel_price,
        )
