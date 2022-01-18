import requests
import json
import googlemaps
from time import sleep
from base64 import b64decode


def get_keys(file_name):
    with open(file_name, "r") as f:
        keys = json.loads(f.read())
    keys = {k: b64decode(v.encode()).decode() for (k, v) in keys.items()}
    return keys


def generate_client(api_key):
    return googlemaps.Client(api_key)


def run_api(map_client, origins, destinations, mode):
    response = map_client.distance_matrix(origins, destinations, mode=mode)
    next_page_token = response.get("next_page_token")

    while next_page_token:
        sleep(2)
        response = map_client.distance_matrix(origins, destinations, mode=mode)
        next_page_token = response.get("next_page_token")

    return response


def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


# TODO
def validate_address(adr):
    pass
