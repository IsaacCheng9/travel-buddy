import logging
import sqlite3
from datetime import datetime, timedelta
from time import sleep
from typing import Tuple
from flask import session
import googlemaps
import requests
import travel_buddy.helpers.helper_general as helper_general
from lxml import html

DB_PATH = helper_general.get_database_path()


def get_most_frequent_route():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT route_id, origin, destination FROM route WHERE route_id=(SELECT route_id FROM route_search WHERE search_count=(SELECT MAX(search_count) FROM route_search WHERE username=?) AND username=?);",
            (session["username"], session["username"]),
        )
        row = cur.fetchone()
        return row


def get_home_and_work():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT home, work FROM profile WHERE username=?;", (session["username"],)
        )
        row = cur.fetchone()
        return row


def generate_client(api_key: str) -> object:
    """
    Generates the Google Maps API client.
    """
    try:
        return googlemaps.Client(api_key)
    except Exception as e:
        logging.warning(f"Failed to generate google maps client - {e}")
        return None


def run_api(map_client: object, origins: str, destinations: str, mode: str) -> dict:
    """
    Run Google Maps API using information on route origin, destination, and
    mode of transport.

    Returns:
        API response as a dictionary of route data.
    """
    try:
        response = map_client.distance_matrix(origins, destinations, mode=mode)
        next_page_token = response.get("next_page_token")
        while next_page_token:
            sleep(2)
            response = map_client.distance_matrix(origins, destinations, mode=mode)
            next_page_token = response.get("next_page_token")
    except Exception as e:
        logging.warning(f"Api Error - {e}")
        return {}

    return response


def safeget(dct: dict, *keys):
    """
    Safely gets key from possibly nested dictionary with error trapping and
    logging failures.
    """
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            logging.warning(f"Safeget failed to find key '{key}' in dict")
            return None
        except Exception as e:
            logging.warning(f"Error in dictionary key search - {e}")
            return None
    return dct


def get_calorie_count(distance: int, calories: int) -> int:
    """
    Returns the estimated count of calories burned by route
    """
    return int(calories * (distance / 1000))


def get_calorie_conversions():
    """
    Returns dictionary of conversions from transport mode to calories burned
    per 1km.
    """
    # Source: bupa.co.uk/health-information/tools-calculators/calories-calculator
    conversions = {"walking": 35, "running": 91, "cycling": 47}
    return conversions


def convert_km_to_miles(kilometres: float) -> float:
    """
    Converts kilometres to miles (5 significant figures).
    """
    return kilometres * 0.621371


def convert_gallons_to_litres(gallons: float) -> float:
    """
    Converts gallons to litres (5 significant figures).
    """
    return gallons * 4.54609


def calculate_total_fuel_cost(driving_distance, car_mpg, fuel_type):
    """
    Fetches the user's car information and calculates the fuel cost and
    consumption for the journey.
    """
    # initialise values to prevent crash later
    fuel_used_driving = 0
    fuel_cost_driving = 0.0
    fuel_price = get_fuel_price(fuel_type)
    if driving_distance is not None:
        driving_distance = float(driving_distance / 1000)
        distance_miles = convert_km_to_miles(driving_distance)
        fuel_used_driving = round(calculate_fuel_used(distance_miles, car_mpg), 2)
        fuel_cost_driving = round(calculate_fuel_cost(fuel_used_driving, fuel_price), 2)
    return fuel_used_driving, fuel_cost_driving, fuel_price


def get_fuel_price(fuel_type: str) -> float:
    """
    Collects the current UK petrol or diesel prices from an online source.

    Args:
        fuel_type: The type of fuel (petrol or diesel).

    Returns:
        The price (£) of petrol or diesel per litre.
    """
    if fuel_type.lower() == "diesel":
        url = "https://www.globalpetrolprices.com/United-Kingdom/diesel_prices/"
    else:
        url = "https://www.globalpetrolprices.com/United-Kingdom/gasoline_prices/"
    page = requests.get(url)
    tree = html.fromstring(page.content)
    price = float(
        tree.xpath('//*[@id="graphPageLeft"]/table/tbody/tr[1]/td[1]/text()')[0]
    )
    return price


def calculate_fuel_used(distance_miles: float, mpg: float) -> float:
    """
    Calculates the fuel consumption in one journey given the miles per
    gallon of the car and the distance travelled in the journey.

    Args:
        distance_miles: The distance travelled in the journey.
        mpg: The miles per gallon of the car.

    Returns:
        The number of litres of fuel used
    """
    return convert_gallons_to_litres(distance_miles / mpg)


def calculate_fuel_cost(fuel_used: float, fuel_price: float) -> float:
    """
    Calculates the cost of fuel (£) for the given journey.

    Args:
        fuel_used: The number of litres of fuel used.
        fuel_price: The price of the fuel per litre.

    Returns:
        The cost (£) of fuel used.
    """
    return fuel_used * fuel_price


def get_car(username) -> Tuple[str, float, str, float]:
    """
    Fetches the user's car make, miles per gallon and fuel type

    Returns:
        The make, miles per gallon, fuel type, and engine size of the user's
        car.
    """
    # Gets the user's details from the database.
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT make, mpg, fuel_type, engine_size FROM car WHERE owner=?;",
            (username,),
        )
        row = cur.fetchall()
    # TODO: Add error handling for when the user has no car.
    make, mpg, fuel_type, engine_size = row[0]
    return make, mpg, fuel_type, engine_size


def get_distance_range(sorted_keys, details) -> str:
    """
    Calculate range of distances and format as string
    """
    lowest, highest = safeget(
        details, "modes", sorted_keys[0], "distance", "text"
    ), safeget(details, "modes", sorted_keys[-1], "distance", "text")
    if lowest == highest:
        return lowest
    else:
        return f"{lowest} - {highest}"


def get_co2_emissions_from_api(payload: str, api_key: str) -> int:
    """
    Use derived emission query to find carbon emission data for route
    """
    url = "https://beta2.api.climatiq.io/estimate"
    headers = {"Authorization": f"Bearer {api_key}"}

    r = requests.post(url, headers=headers, json=payload)
    return r.json()


def generate_co2_emissions(
    distance: int, mode: str, fuel: str = "na", engine_size: float = -1
) -> float:
    """
    Prepares data in format suitable for carbon emissions api to calculate and
    returns carbon emission value.
    """

    if distance is None:
        return 0

    file_name = "keys.json"
    keys = helper_general.get_keys(file_name)

    if mode == "driving":
        query = "passenger_vehicle-vehicle_type_car-fuel_source_"
        if fuel in ("petrol", "diesel"):
            query += fuel
        else:
            query += "na"
        query += "-engine_size_"
        # TODO: query fails with engine size specified - cannot find format to use
        # if engine_size > 0:
        #    query += str(engine_size)
        # else:
        query += "na"
        query += "-vehicle_age_na-vehicle_weight_na"

        payload = {
            "emission_factor": query,
            "parameters": {"distance": distance, "distance_unit": "m"},
        }
        carbon = get_co2_emissions_from_api(payload, keys["carbon_emissions"]).get(
            "co2e", -1
        )
        return carbon

    elif mode == "public transport":
        """
        #bus
        query_bus = "passenger_vehicle-vehicle_type_local_bus-fuel_source_na-distance_na-engine_size_na"

        payload_bus = {
            "emission_factor": query_bus,
            "parameters": {
                "passengers": 1,
                "distance": distance,
                "distance_unit": "m"
            }
        }

        #train
        query_train = "passenger_train-route_type_national_rail-fuel_source_na"

        payload_train = {
            "emission_factor": query_train,
            "parameters": {
                "passengers": 1,
                "distance": distance,
                "distance_unit": "m"
            }
        }

        print(query_bus)
        carbon_bus = get_co2_emissions_from_api(distance, payload_bus, keys["carbon_emissions"]).get("co2e", -1)
        print(carbon_bus)

        print(query_train)
        carbon_train = get_co2_emissions_from_api(distance, payload_train, keys["carbon_emissions"]).get("co2e", -1)
        print(carbon_train)

        if carbon_bus < 0:
            if carbon_train < 0:
                carbon = -1
            else:
                carbon = carbon_train
        else:
            if carbon_train < 0:
                carbon = carbon_bus
            else:
                carbon = (carbon_bus + carbon_train) / 2
        """

        # bus co2 per km per person
        bus_base = 0.10227
        bus_emissions = bus_base * (distance / 1000)

        # train co2 per km per person
        train_base = 0.00446
        train_emissions = train_base * (distance / 1000)

        carbon = (bus_emissions + train_emissions) / 2
        return carbon

    return 0


def get_recommendations(
    travel_mode_simple: str,
    route_details: dict,
    co2_list: dict,
    calories: dict,
    fuel_cost: float,
    fuel_type: str,
) -> list:
    """
    Generates recommendation points relevant to the journey the user is viewing
    and return as list.
    """
    time_walking = safeget(route_details, "walking", "duration", "value")
    time_cycling = safeget(route_details, "cycling", "duration", "value")
    time_public_transport = safeget(
        route_details, "public transport", "duration", "value"
    )
    time_driving = safeget(route_details, "driving", "duration", "value")

    body = []

    if travel_mode_simple == "cycling":
        body.append(
            "Cycling this journey? Great job! You're saving "
            f"<b>{co2_list.get('driving', 0)}kg</b> of CO2 compared to if you "
            "drove this journey!"
        )
        if safeget(route_details, "walking", "distance", "value") > 25000:
            trees = helper_general.co2_to_trees(round(co2_list["driving"] * 40, 2), 30)
            body.append(
                "Is this your daily commute? Cycling this journey twice every week day for "
                "one month would save about "
                f"<b>{round(co2_list.get('driving', 0) * 40, 2)} kg</b> of CO2 "
                f"emissions!<br> That's the same as the amount of oxygen <b>{trees}</b> "
                "trees offset in a month! "
                "(<a href='https://www.viessmann.co.uk/heating-advice/how-much-co2-does-tree-absorb' target='_blank'>Source</a>)"
            )

    elif travel_mode_simple == "walking":
        body.append(
            "Walking this journey? Great job! You're saving "
            f"<b>{co2_list.get('driving', 0)}kg</b> of CO2 compared to if you drove "
            "this journey!"
        )
        trees = helper_general.co2_to_trees(round(co2_list["driving"] * 40, 2), 30)
        walk_distance = safeget(route_details, "walking", "distance", "value")
        if walk_distance < 5000:
            body.append(
                "Is this your daily commute? Walking this journey twice every week day for "
                f"one month would save about <b>{round(co2_list.get('driving', 0) * 40, 2)}"
                " kg</b> of CO2 emissions!<br> That's the same as the amount of oxygen "
                f"<b>{trees}</b> trees offset in a month! "
                "(<a href='https://www.viessmann.co.uk/heating-advice/how-much-co2-does-tree-absorb' target='_blank'>Source</a>)"
            )
        if walk_distance < 40000:
            time_saved = 60 * round(((time_walking * 40) - (time_cycling * 40)) / 60)
            time_saved_daily = 60 * round((time_walking - time_cycling) / 60)
            if time_saved > 120:
                time_saved = timedelta(seconds=time_saved)
                body.append(
                    "If you were to cycle this route instead, you could also save about "
                    f"<b>{time_saved_daily}</b> each day, or <b>{time_saved}</b> over your "
                    "working days for the month!"
                )

    if travel_mode_simple == "public transport":
        co2_saved_over_driving = round(
            co2_list["driving"] - co2_list["public transport"], 2
        )
        if safeget(route_details, "walking", "distance", "value") > 50000:
            if co2_saved_over_driving > 0:
                body.append(
                    "Planning to take public transport? This is a long journey! You "
                    f"would be saving about <b>{co2_saved_over_driving} kg</b> of CO2 "
                    "by using public transport instead of driving."
                )

        elif safeget(route_details, "walking", "distance", "value") > 10000:
            if co2_saved_over_driving > 0:
                body.append(
                    "Planning to take public transport? You would be saving about "
                    f"<b>{co2_saved_over_driving} kg</b> of CO2 by using public "
                    "transport instead of driving."
                )
            body.append(
                append_cycle_walk_str(time_cycling, time_public_transport, "cycle")
            )
            body[-1] += (
                f"you would save about <b>{co2_list['public transport']} kg</b> of "
                f"CO2 and would burn about <b>{calories['cycling']} kcal</b>!"
            )

        else:
            body.append(
                append_cycle_walk_str(time_cycling, time_public_transport, "cycle")
            )
            body[-1] += (
                f"you would save about <b>{co2_list['public transport']} kg</b> of "
                f"CO2 and would burn about <b>{calories['cycling']} kcal</b>!"
            )
            body.append(
                append_cycle_walk_str(time_walking, time_public_transport, "walk")
            )
            body[-1] += (
                f"you would save about <b>{co2_list['public transport']} kg</b> of "
                f"CO2 and would burn <b>{calories['walking']} - {calories['running']} "
                "kcal</b>!"
            )
            trees = helper_general.co2_to_trees(
                round(co2_list["public transport"] * 40, 2), 30
            )
            body.append(
                f"Is this your daily commute? Cycling this journey twice every working "
                f"day would save about <b>{round(co2_list['public transport'] * 40, 2)}"
                "kg</b> of CO2 emissions over a month!<br> That's the same as the "
                f"amount of oxygen <b>{trees}</b> trees offset in a month! "
                "(<a href='https://www.viessmann.co.uk/heating-advice/how-much-co2-does-tree-absorb' target='_blank'>Source</a>)"
            )

    if travel_mode_simple == "driving":
        co2_excess_over_transit = round(
            co2_list["driving"] - co2_list["public transport"], 2
        )
        cost = format(fuel_cost, ".2f")
        walk_distance = safeget(route_details, "walking", "distance", "value")
        if walk_distance is not None:
            if walk_distance > 40000:
                if co2_excess_over_transit > 0:
                    body.append(
                        "Planning to drive? This is a long journey! If you could travel "
                        "with public transport instead you would save about "
                        f"<b>{co2_excess_over_transit} kg</b> of CO2 as well as "
                        f"<b>£{cost}</b> of fuel!"
                    )

            elif walk_distance > 20000:
                if co2_excess_over_transit > 0:
                    body.append(
                        "Planning to drive? You would save about "
                        f"<b>{co2_excess_over_transit} kg</b> of CO2 by using public "
                        "transport instead of driving!"
                    )
                body.append(append_cycle_walk_str(time_cycling, time_driving, "cycle"))
                body[-1] += (
                    f"you would save about <b>{co2_list['driving']} kg</b> of CO2 and "
                    f"would save <b>£{cost}</b> of fuel, as well as burning about "
                    f"<b>{calories['cycling']} kcal</b>!"
                )

            else:
                extra_time = 60 * round((time_cycling - time_driving) / 60)
                if abs(extra_time) > 120:
                    body.append(
                        append_cycle_walk_str(time_cycling, time_driving, "cycle")
                    )
                    body[-1] += (
                        f"you would save about <b>{co2_list['driving']} kg</b> of CO2 and "
                        f"would burn about <b>{calories['cycling']} kcal</b>!"
                    )
                if abs(extra_time) > 60:
                    body.append(
                        append_cycle_walk_str(time_walking, time_driving, "walk")
                    )
                    body[-1] += (
                        f"you would save about <b>{co2_list['driving']} kg</b> of CO2 and "
                        f"would burn <b>{calories['walking']} - {calories['running']} kcal</b>!"
                    )
                trees = helper_general.co2_to_trees(
                    round(co2_list["driving"] * 40, 2), 30
                )
                cost = format((fuel_cost * 40), ".2f")
                print(float(trees), float(cost), round(co2_list["driving"] * 40, 2))
                if (
                    float(trees) >= 1
                    and float(cost) > 0.0
                    and round(co2_list["driving"] * 40, 2) > 0.0
                ):
                    body.append(
                        "Is this your daily commute? Cycling this journey twice every working "
                        f"day would save <b>£{cost}</b> of fuel as well as about "
                        f"<b>{round(co2_list['driving'] * 40, 2)} kg</b> of CO2 emissions over "
                        f"a month!<br> That's the same as the amount of oxygen <b>{trees}</b> "
                        "trees offset in a month! "
                        "(<a href='https://www.viessmann.co.uk/heating-advice/how-much-co2-does-tree-absorb' target='_blank'>Source</a>)"
                    )
            if fuel_type.lower() != "electric":
                body.append(
                    append_ev_recommendation(
                        safeget(route_details, "driving", "distance", "value"),
                        float(fuel_cost),
                        co2_list.get("driving"),
                    )
                )

    return body


def get_min_distance(details: dict) -> float:
    distances = [
        distance["distance"]["value"]
        for distance in details["modes"].values()
        if distance["distance"] is not None
    ]
    return min(distances, default=-1)


def append_cycle_walk_str(time_1: int, time_2: int, mode: str) -> str:
    """
    Return string of common point on comparison of times
    """
    extra_time = 60 * round((time_1 - time_2) / 60)
    if extra_time > 0:
        extra_time = timedelta(seconds=extra_time)
        return (
            f"If you were to {mode} this journey instead then it would take about "
            f"an extra <b>{extra_time}</b>, but "
        )
    else:
        extra_time = timedelta(seconds=abs(extra_time))
        return (
            f"If you were to {mode} this journey instead then you would be able to "
            f"complete the journey <b>{extra_time} faster</b>! Also, "
        )


def append_ev_recommendation(distance, petrol_cost, petrol_co2) -> str:
    """
    Return a string on information on electric vehicle recommendation
    source for fuel_per_m_ev:
        https://insights.leaseplan.co.uk/electric-vehicles/ev-news/electric-vehicle-cost/
    """
    fuel_per_m_ev = 0.000034176
    fuel_cost_ev = fuel_per_m_ev * distance

    co2_per_m_ev = 0.000035
    co2_emission_ev = co2_per_m_ev * distance

    cost_saved = petrol_cost - fuel_cost_ev
    fuel_cost_ev = format(fuel_cost_ev, ".2f")
    cost_saved_2dp = format(cost_saved, ".2f")

    co2_saved = petrol_co2 - co2_emission_ev

    if cost_saved > 0 and co2_saved > 0:
        return (
            "Have you thought about buying an electric car? "
            "An estimate for the electricity cost of this route "
            f"is <b>£{fuel_cost_ev}</b>, that's a saving of <b>£{cost_saved_2dp}</b>! "
            f"Additionally, you could expect to use just <b>{round(co2_emission_ev, 2)}kg</b> of CO2, "
            f"that's <b>{round(co2_saved,2)}kg</b> less than in a petrol car."
        )
    else:
        return ""


def save_route(username: str, origin: str, destination: str):
    """
    Save a specific route search to a user
    """
    with sqlite3.connect(DB_PATH) as conn:
        route_id = get_route_id(conn, origin, destination)
        if not route_id:
            route_id = register_route(conn, origin, destination)
            logging.debug(f"Registered new route with ID - {route_id}")

        add_route_to_user(conn, username, route_id)


def get_route_id(conn, origin: str, destination: str) -> int:
    """
    Get route ID if exists, else return None
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT route_id FROM route WHERE origin=? AND destination=?;",
        (origin, destination),
    )
    id = cur.fetchone()
    if id:
        return id[0]
    return None


def register_route(conn, origin: str, destination: str):
    """
    Register a route in the databse
    """
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO route (origin, destination) VALUES (?, ?);",
        (origin, destination),
    )
    conn.commit()
    return get_route_id(conn, origin, destination)


def add_route_to_user(conn, username: str, route_id: int):
    """
    Increment count of searches for this route on a user,
    or add a new row if the user has not searched this before
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT search_count, last_updated_timestamp FROM route_search "
        "WHERE route_id=?;",
        (route_id,),
    )
    route_search = cur.fetchone()
    if route_search:
        if datetime.strptime(
            route_search[1], "%Y-%m-%d %H:%M:%S"
        ) < datetime.now() - timedelta(minutes=5):
            cur.execute(
                "UPDATE route_search "
                "SET search_count=?, last_searched_timestamp=CURRENT_TIMESTAMP, "
                "last_updated_timestamp=CURRENT_TIMESTAMP "
                "WHERE username=? AND route_id=?;",
                (route_search[0] + 1, username, route_id),
            )
        else:
            cur.execute(
                "UPDATE route_search "
                "SET last_searched_timestamp=CURRENT_TIMESTAMP "
                "WHERE username=? AND route_id=?;",
                (username, route_id),
            )
    else:
        cur.execute(
            "INSERT INTO route_search (username, route_id, search_count, "
            "last_searched_timestamp, last_updated_timestamp) "
            "VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);",
            (username, route_id, 1),
        )
        conn.commit()


def get_total_routes_searched(username: str) -> Tuple[int, int]:
    """
    Gets the number of routes searched by the user (unique and total).
    Args:
        username: The user to calculate the statistic for.
    Returns:
        The unique and total number of routes searched by the user.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # Queries the total unique routes searched.
        cur.execute(
            "SELECT COUNT(route_id) FROM route_search WHERE username=?;",
            (username,),
        )
        total_unique_routes_searched = cur.fetchone()[0]
        # Prevents 0, None from being returned when there are no routes searched.
        if total_unique_routes_searched == 0:
            return 0, 0

        # Queries the total number of routes searched.
        cur.execute(
            "SELECT SUM(search_count) FROM route_search WHERE username=?;",
            (username,),
        )
        total_routes_searched = cur.fetchone()[0]
    return total_routes_searched, total_unique_routes_searched
