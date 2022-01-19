"""
Tests the validity of api keys and api return values
"""

import travel_buddy.helpers.helper_routes as helper_routes


def test_key_is_read():
    API_KEY_FILE = "tests/keys_test.json"
    KEYS = helper_routes.get_keys(API_KEY_FILE)

    assert KEYS.get("test_key1") == "decoded_test_key_123"
    assert KEYS.get("test_key2") == "12345"
    assert KEYS.get("test_key3") == "!!!!!"
    assert KEYS.get("test_key4") == "   "


def test_api_key_is_valid():

    API_KEY_FILE = "keys.json"
    KEYS = helper_routes.get_keys(API_KEY_FILE)

    map_client = helper_routes.generate_client(KEYS["google_maps"])

    assert map_client is not None

    origin = "University of Exeter Forum Library, Stocker Rd, Exeter EX4 4PT"
    destination = "Exeter Quay, Exeter EX2 4BZ"

    data = helper_routes.run_api(map_client, origin, destination, "walking")

    assert data is not None
    assert data.get("origin_addresses")[0] == "Stocker Rd, Exeter EX4 4PT, UK"
    assert data.get("destination_addresses")[0] == "Exeter Quay, Exeter EX2 4BZ, UK"
