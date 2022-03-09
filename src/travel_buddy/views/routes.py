"""
Handles the view for the route details check functionality
"""

import logging

import travel_buddy.helpers.helper_general as helper_general
import travel_buddy.helpers.helper_routes as helper_routes
from flask import Blueprint, render_template, request, session, redirect
from travel_buddy.helpers.helper_limiter import limiter

routes_blueprint = Blueprint(
    "routes", __name__, static_folder="static", template_folder="templates"
)


@routes_blueprint.route("/routes", methods=["GET", "POST"])
@limiter.limit("10/minute")
def routes() -> object:
    """
    Generates information on route details using Google Maps API functions.

    Returns:
        A view populated with data about travel times.
    """

    if "username" not in session:
        return redirect("/")

    api_key_file = "keys.json"
    keys = helper_general.get_keys(api_key_file)
    autocomplete_query = helper_general.get_autocomplete_query(
        key=keys["google_maps"], func="initMap"
    )

    if request.method == "GET":
        map_query = (
            f"https://www.google.com/maps/embed/v1/view"
            f"?key={keys['google_maps']}&center=50.9,-1.4&zoom=8"
        )
        most_frequent_route = helper_routes.get_most_frequent_route()
        home_and_work = helper_routes.get_home_and_work()
        return render_template(
            "routes.html",
            username=session.get("username"),
            most_frequent_route=most_frequent_route,
            map_query=map_query,
            autocomplete_query=autocomplete_query,
            route_exists=False,
            home_and_work=home_and_work,
        )

    elif request.method == "POST":
        origins = request.form["start_point"].strip()
        destinations = request.form["destination"].strip()
        travel_mode_full = request.form["mode"]

        if travel_mode_full == "bicycling":
            travel_mode_simple = "cycling"
        elif travel_mode_full == "transit":
            travel_mode_simple = "public transport"
        else:
            travel_mode_simple = travel_mode_full

        # Generates the Google Maps API client to get data on routes using
        # different modes of transport.
        map_client = helper_routes.generate_client(keys["google_maps"])
        if map_client is None:
            # TODO error
            logging.warning(f"Failed to generate maps api client")
            return
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
        details["modes"]["cycling"] = details["modes"].pop("bicycling")
        details["modes"]["public transport"] = details["modes"].pop("transit")
        distances = {
            k: helper_routes.safeget(v, "distance", "value")
            for k, v in helper_routes.safeget(details, "modes").items()
            if helper_routes.safeget(v, "distance", "value") is not None
        }

        try:
            conversions = helper_routes.get_calorie_conversions()
            calories = {
                "walking": helper_routes.get_calorie_count(
                    helper_routes.safeget(
                        details, "modes", "walking", "distance", "value"
                    ),
                    conversions.get("walking"),
                ),
                "running": helper_routes.get_calorie_count(
                    helper_routes.safeget(
                        details, "modes", "walking", "distance", "value"
                    ),
                    conversions.get("running"),
                ),
                "cycling": helper_routes.get_calorie_count(
                    helper_routes.safeget(
                        details, "modes", "cycling", "distance", "value"
                    ),
                    conversions.get("cycling"),
                ),
            }
        except Exception as e:
            logging.warning(f"Failed to find calorie counts - {e}")
            calories = {
                "walking": "N/A",
                "running": "N/A",
                "cycling": "N/A",
            }

        # Finds the shortest and longest distances from the routes.
        try:
            sorted_keys = sorted(distances, key=distances.get)
            distance_range = helper_routes.get_distance_range(sorted_keys, details)
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
        map_query = (
            f"https://www.google.com/maps/embed/v1/directions"
            f"?key={keys['google_maps']}&origin={origin_convert}"
            f"&destination={destination_convert}&mode={travel_mode_full}&units=metric"
        )

        driving_distance = helper_routes.safeget(
            details, "modes", "driving", "distance", "value"
        )

        car_make, car_mpg, fuel_type, engine_size = helper_routes.get_car(
            session["username"]
        )

        (
            fuel_used_driving,
            fuel_cost_driving,
            fuel_price,
        ) = helper_routes.calculate_total_fuel_cost(
            driving_distance, car_mpg, fuel_type
        )

        fuel_used = fuel_used_driving if travel_mode_full == "driving" else 0
        fuel_cost = fuel_cost_driving if travel_mode_full == "driving" else 0

        # Finds carbon emissions for each mode.
        co2_list = {"walking": 0, "cycling": 0, "driving": 0, "public transport": 0}
        for m in ("driving", "public transport"):
            co2_list[m] = round(
                helper_routes.generate_co2_emissions(
                    distances.get(m), m, fuel_type, engine_size
                ),
                2,
            )
            if co2_list[m] < 0:
                logging.warning(f"Failed to find CO2 emission for {m}")
                co2_list[m] = "Unknown"
        co2 = co2_list[travel_mode_simple]

        recommendations = helper_routes.get_recommendations(
            travel_mode_simple,
            details.get("modes"),
            co2_list,
            calories,
            fuel_cost_driving,
            fuel_type,
        )

        helper_routes.save_route(session.get("username", "unknown"), address1, address2)
        most_frequent_route = helper_routes.get_most_frequent_route()
        home_and_work = helper_routes.get_home_and_work()
        return render_template(
            "routes.html",
            username=session.get("username"),
            distance_range=distance_range,
            mode=travel_mode_simple,
            details=details,
            origin=address1,
            destination=address2,
            map_query=map_query,
            autocomplete_query=autocomplete_query,
            route_exists=True,
            most_frequent_route=most_frequent_route,
            co2_emissions=co2,
            fuel_used=fuel_used,
            fuel_cost=format(fuel_cost, ".2f"),
            car_make=car_make,
            car_mpg=car_mpg,
            min_distance=helper_routes.get_min_distance(details),
            fuel_price=format(fuel_price, ".2f"),
            calories=calories,
            recommendations=recommendations,
            home_and_work=home_and_work,
        )
