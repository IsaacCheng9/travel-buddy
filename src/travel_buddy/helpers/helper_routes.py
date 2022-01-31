import logging
from time import sleep
from typing import Tuple
from datetime import timedelta, datetime

import googlemaps
import sqlite3
import travel_buddy.helpers.helper_general as helper_general
import requests
from flask import session
from lxml import html

DB_PATH = helper_general.get_database_path()


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
        return

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
    Returns dictionary of conversions from transport mode to calories burned per 1km
    Source: bupa.co.uk/health-information/tools-calculators/calories-calculator
    """
    conversions = {"walking": 35, "running": 91, "cycling": 47}

    return conversions


def get_fuel_price(fuel_type: str) -> float:
    """
    Collects the current UK petrol or diesel prices from an online source

    Returns:
        The price in pounds of petrol or diesel per litre
    """
    if fuel_type == "petrol":
        url = "https://www.globalpetrolprices.com/United-Kingdom/gasoline_prices/"
    elif fuel_type == "diesel":
        url = "https://www.globalpetrolprices.com/United-Kingdom/diesel_prices/"
    page = requests.get(url)
    tree = html.fromstring(page.content)
    price = float(
        tree.xpath('//*[@id="graphPageLeft"]/table/tbody/tr[1]/td[1]/text()')[0]
    )
    return price


def calculate_fuel_consumption(mpg: float, distance: float) -> float:
    """
    Calculates the fuel consumption in one journey given the miles per
    gallon of the car and the distance travelled in the journey

    Returns:
        The number of litres of fuel used
    """
    # TODO: Add a test for this.
    return convert_gallons_to_litres(distance / mpg)


def calculate_fuel_cost(fuel_used: float, fuel_type: str) -> float:
    """
    Calculates the cost of fuel used in pounds, for one journey

    Returns:
        The cost of fuel used
    """
    fuel_price = get_fuel_price(fuel_type)
    total_cost = convert_gallons_to_litres(fuel_used) * fuel_price
    return total_cost


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


def convert_km_to_miles(kilometres: float) -> float:
    """
    Converts kilometres to miles
    """
    # TODO: Add a test for this.
    return kilometres * 0.621371


def convert_gallons_to_litres(gallons: float) -> float:
    """
    Converts gallons to litres
    """
    # TODO: Add a test for this.
    return gallons * 4.54609


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
) -> list:
    """
    Generate recommendation points relevant to the journey the user is viewing and return as list
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
            f"Cycling this journey? Great Job! You're saving <b>{co2_list.get('driving', 0)}kg</b> \
                    of CO2 compared to if you drove this journey!"
        )
        trees = co2_to_trees(round(co2_list["driving"] * 40, 2), 30)
        body.append(
            f"Is this your daily commute? Cycling this journey twice every week day for one month \
                      would save about <b>{round(co2_list.get('driving', 0) * 40, 2)}kg</b> of CO2 emissions!<br> \
                      - Thats the same as the amount of oxegen <b>{trees}</b> trees offset in a month!"
        )

    elif travel_mode_simple == "walking":
        body.append(
            f"Walking this journey? Great Job! You're saving <b>{co2_list.get('driving', 0)}kg</b> \
                    of CO2 compared to if you drove this journey!"
        )
        trees = co2_to_trees(round(co2_list["driving"] * 40, 2), 30)
        body.append(
            f"Is this your daily commute? Walking this journey twice every week day for one month \
                      would save about <b>{round(co2_list.get('driving', 0) * 40, 2)}kg</b> of CO2 emissions!<br> \
                      - Thats the same as the amount of oxegen <b>{trees}</b> trees offset in a month!"
        )
        time_saved = 60 * round(((time_walking * 40) - (time_cycling * 40)) / 60)
        time_saved_daily = 60 * round((time_walking - time_cycling) / 60)
        if time_saved > 0:
            time_saved = timedelta(seconds=time_saved)
            body.append(
                f"If you were to cycle this route instead you could also save about \
                          <b>{time_saved_daily}</b> each day, or <b>{time_saved}</b> over your working days for the month!"
            )

    if travel_mode_simple == "public transport":
        co2_saved_over_driving = round(
            co2_list["driving"] - co2_list["public transport"], 2
        )
        if safeget(route_details, "walking", "distance", "value") > 50000:
            if co2_saved_over_driving > 0:
                body.append(
                    f"Planning to take public transport? This is a long journey! You would be saving about \
                              <b>{co2_saved_over_driving}kg</b> of CO2 by using public transport instead of driving."
                )

        elif safeget(route_details, "walking", "distance", "value") > 10000:
            if co2_saved_over_driving > 0:
                body.append(
                    f"Planning to take public transport? You would be saving about \
                              <b>{co2_saved_over_driving}kg</b> of CO2 by using public transport instead of driving."
                )
            body.append(
                append_cycle_walk_str(time_cycling, time_public_transport, "cycle")
            )
            body[
                -1
            ] += f"you would save about <b>{co2_list['public transport']}kg</b> of CO2 and would \
                           burn about <b>{calories['cycling']}kcal</b>!"

        else:
            body.append(
                append_cycle_walk_str(time_cycling, time_public_transport, "cycle")
            )
            body[
                -1
            ] += f"you would save about <b>{co2_list['public transport']}kg</b> of CO2 and would \
                          burn about <b>{calories['cycling']}kcal</b>!"
            body.append(
                append_cycle_walk_str(time_walking, time_public_transport, "walk")
            )
            body[
                -1
            ] += f"you would save about <b>{co2_list['public transport']}kg</b> of CO2 and would \
                          burn <b>{calories['walking']}-{calories['running']}kcal</b>!"
            trees = co2_to_trees(round(co2_list["public transport"] * 40, 2), 30)
            body.append(
                f"Is this your daily commute? Cycling this journey twice every working day would save \
                          about <b>{round(co2_list['public transport'] * 40, 2)}kg</b> of CO2 emissions over a month!<br> \
                          - Thats the same as the amount of oxegen <b>{trees}</b> trees offset in a month!"
            )

    if travel_mode_simple == "driving":
        co2_excess_over_transit = round(
            co2_list["driving"] - co2_list["public transport"], 2
        )
        if safeget(route_details, "walking", "distance", "value") > 50000:
            if co2_excess_over_transit > 0:
                body.append(
                    f"Planning to drive? This is a long journey! If you could travel with public transport instead \
                              you would save about <b>{co2_excess_over_transit}kg</b> of CO2!"
                )

        elif safeget(route_details, "walking", "distance", "value") > 10000:
            if co2_excess_over_transit > 0:
                body.append(
                    f"Planning to drive? You would save about <b>{co2_excess_over_transit}kg</b> of CO2 by using public \
                              transport instead of driving!"
                )
            body.append(append_cycle_walk_str(time_cycling, time_driving, "cycle"))
            body[
                -1
            ] += f"you would save about <b>{co2_list['driving']}kg</b> of CO2 and would \
                          save <b>£{fuel_cost}</b> of fuel, as well as \
                          burning about <b>{calories['cycling']}kcal</b>!"

        else:
            body.append(append_cycle_walk_str(time_cycling, time_driving, "cycle"))
            body[
                -1
            ] += f"you would save about <b>{co2_list['driving']}kg</b> of CO2 and would \
                          burn about <b>{calories['cycling']}kcal</b>!"
            body.append(append_cycle_walk_str(time_walking, time_driving, "walk"))
            body[
                -1
            ] += f"you would save about <b>{co2_list['driving']}kg</b> of CO2 and would \
                          burn <b>{calories['walking']}-{calories['running']}kcal</b>!"
            trees = co2_to_trees(round(co2_list["driving"] * 40, 2), 30)
            body.append(
                f"Is this your daily commute? Cycling this journey twice every working day would save \
                          <b>£{round((fuel_cost * 40), 2)}</b> of fuel as well as \
                          about <b>{round(co2_list['driving'] * 40, 2)}kg</b> of CO2 emissions over a month!<br> \
                          - Thats the same as the amount of oxegen <b>{trees}</b> trees offset in a month!"
            )

    return body


def append_cycle_walk_str(time_1: int, time_2: int, mode: str) -> str:
    """
    Return string of common point on comparison of times
    """
    extra_time = 60 * round((time_1 - time_2) / 60)
    if extra_time > 0:
        extra_time = timedelta(seconds=extra_time)
        return f"If you were to {mode} this journey instead then it would take about \
                 an extra <b>{extra_time}</b>, but "
    else:
        extra_time = timedelta(seconds=abs(extra_time))
        return f"If you were to {mode} this journey instead then you would be able to complete \
                 the journey <b>{extra_time} faster</b>! Also, "


def co2_to_trees(co2: float, days: int) -> float:
    """
    Convert kilograms of CO2 to yearly tree offset
    Source: https://www.viessmann.co.uk/heating-advice/how-much-co2-does-tree-absorb
    """
    yearly_offset = 21
    daily_offset = yearly_offset / 365
    required_trees = co2 / (daily_offset * days)
    return round(required_trees, 2)
