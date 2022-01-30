import logging
from time import sleep
from typing import Tuple

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
        The price in pounds of petrol or diesel
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


def get_car(username) -> Tuple[str, float, str]:
    """
    Fetches the user's car make, miles per gallon and fuel type

    Returns:
        The make, miles per gallon, and fuel type of the user's car.
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
    print(r.json())
    return r.json()


def generate_co2_emissions(
    distance: int, mode: str, fuel: str = "na", engine_size: float = -1
) -> float:
    """
    Prepares data in format suitable for carbon emissions api to calculate and returns carbon emission value
    """
    filename = "keys.json"
    keys = helper_general.get_keys(filename)

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

        print(query)

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

        print(distance)
        # bus co2 per km per person
        bus_base = 0.10227
        bus_emissions = bus_base * (distance / 1000)

        # train co2 per km per person
        train_base = 0.00446
        train_emissions = train_base * (distance / 1000)

        carbon = (bus_emissions + train_emissions) / 2

        print(carbon)

        return carbon

    else:
        return 0
