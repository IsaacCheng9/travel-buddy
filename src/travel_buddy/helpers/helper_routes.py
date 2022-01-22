import googlemaps
import logging
from time import sleep


def generate_client(api_key: str) -> object:
    try:
        return googlemaps.Client(api_key)
    except Exception as e:
        logging.warning(f"Failed to generate google maps client - {e}")
        return None


def run_api(map_client: object, origins: str, destinations: str, mode: str) -> dict:
    """
    Run google maps api based on given information on route origin, destination, and mode of transport.
    Return dictionary api response
    """
    response = map_client.distance_matrix(origins, destinations, mode=mode)
    next_page_token = response.get("next_page_token")
    while next_page_token:
        sleep(2)
        response = map_client.distance_matrix(origins, destinations, mode=mode)
        next_page_token = response.get("next_page_token")

    return response


def safeget(dct: dict, *keys):
    """
    Safely get key from possibly nested dictionary with error trapping and logging failures
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


# TODO
def validate_address(address: str):
    pass
