import logging
from time import sleep

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


def get_fuel_price(fuel_type):
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


def calculate_fuel_consumption(mpg, distance):
    """
    Calculates the fuel consumption in one journey given the miles per
    gallon of the car and the distance travelled in the journey

    Returns:
        The number of litres of fuel used
    """
    return gallons_to_litres(distance / mpg)


def calculate_fuel_cost(fuel_used, fuel_type):
    """
    Calculates the cost of fuel used in pounds, for one journey

    Returns:
        The cost of fuel used
    """
    fuel_price = get_fuel_price(fuel_type)
    total_cost = gallons_to_litres(fuel_used) * fuel_price
    return total_cost


def get_car():
    """
    Fetches the user's car make, miles per gallon and fuel type

    Returns:
        User's car make
        User's car miles per gallon
        User's car fuel_type
    """
    username = session["username"]
    # Gets the user's details from the database.
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT make, mpg, fuel_type " "FROM cars WHERE owner=?;",
            (username,),
        )
        row = cur.fetchall()
    make, mpg, fuel_type = row[0]
    return make, mpg, fuel_type


def km_to_miles(km):
    """
    Converts kilometres to miles
    """
    return km * 0.621371


def gallons_to_litres(gallons):
    """
    Converts gallons to litres
    """
    return gallons * 4.54609


# TODO
def validate_address(address: str):
    pass
