"""
Tests the correctness of information given by routes analysis.
"""

import travel_buddy.helpers.helper_routes as helper_routes


def test_convert_km_to_miles():
    """
    Tests whether kilometres are converted to miles correctly.
    """
    assert helper_routes.convert_km_to_miles(0) == 0
    assert helper_routes.convert_km_to_miles(1) == 0.621371
    assert helper_routes.convert_km_to_miles(10) == 6.21371


def test_convert_gallons_to_litres():
    """
    Tests whether gallons are converted into litres correctly.
    """
    assert helper_routes.convert_gallons_to_litres(0) == 0
    assert helper_routes.convert_gallons_to_litres(1) == 4.54609
    assert helper_routes.convert_gallons_to_litres(10) == 45.4609


def test_calculate_fuel_used():
    """
    Tests that the correct fuel used is calculated based on miles per gallon
    and miles travelled.
    """
    assert helper_routes.calculate_fuel_used(1, 1) == 4.54609
    assert helper_routes.calculate_fuel_used(0, 1) == 0
    assert helper_routes.calculate_fuel_used(10, 1) == 45.4609


def test_calculate_fuel_cost():
    """
    Tests that the correct fuel costs are calculated based on amount of fuel
    used and fuel price per litre.
    """
    assert helper_routes.calculate_fuel_cost(10, 1.5) == 15
    assert helper_routes.calculate_fuel_cost(0, 10) == 0
    assert helper_routes.calculate_fuel_cost(10, 0) == 0


def test_get_total_routes_searched():
    """
    Tests that the number of routes (unique and total) is calculated correctly.
    """
    # The username '@' isn't allowed, so it should have no carpools searched.
    assert helper_routes.get_total_routes_searched("@") == (0, 0)
