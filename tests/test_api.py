"""
Tests the validity of api keys and api return values
"""

import travel_buddy.helpers.helper_routes as helper_routes
import travel_buddy.helpers.helper_general as helper_general


def test_key_is_read():
    """
    Tests some example encoded data can be read from json and decoded correctly.
    """
    API_KEY_FILE = "tests/keys_test.json"
    KEYS = helper_general.get_keys(API_KEY_FILE)

    assert KEYS.get("test_key1") == "decoded_test_key_123"
    assert KEYS.get("test_key2") == "12345"
    assert KEYS.get("test_key3") == "!!!!!"
    assert KEYS.get("test_key4") == "   "


# !IMPPORTANT: Disabled the test indefinitely due to expired Google Maps API key.
# def test_api_key_is_valid():
#     """
#     Tests that the given encoded api keys can be decoded, the google maps client can be created,
#     and the keys can be used in with the google maps api to return correct data.
#     """
#     API_KEY_FILE = "keys.json"
#     KEYS = helper_general.get_keys(API_KEY_FILE)

#     map_client = helper_routes.generate_client(KEYS["google_maps"])

#     assert map_client is not None

#     origin = "University of Exeter Forum Library, Stocker Rd, Exeter EX4 4PT"
#     destination = "Exeter Quay, Exeter EX2 4BZ"

#     data = helper_routes.run_api(map_client, origin, destination, "walking")

#     assert data is not None
#     assert data.get("origin_addresses")[0] == "Stocker Rd, Exeter EX4 4PT, UK"
#     assert data.get("destination_addresses")[0] == "Exeter Quay, Exeter EX2 4BZ, UK"
