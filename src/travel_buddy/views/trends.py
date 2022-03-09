"""
Handles the view for long term trends and estimations for a user.
"""
import travel_buddy.helpers.helper_routes as helper_routes
import travel_buddy.helpers.helper_general as helper_general

from flask import Blueprint, redirect, render_template, request, session, url_for
from travel_buddy.helpers.helper_limiter import limiter

trends_blueprint = Blueprint(
    "trends", __name__, static_folder="static", template_folder="templates"
)

DB_PATH = helper_general.get_database_path()


@trends_blueprint.route("/trends", methods=["GET", "POST"])
@limiter.limit("15/minute")
def trends():
    if "username" not in session:
        return redirect("/")

    (
        user_car_make,
        user_car_mpg,
        user_fuel_type,
        user_engine_size,
    ) = helper_routes.get_car(session.get("username"))

    evs = helper_general.get_best_efficiency_electric(
        helper_general.get_electric_cars()
    )

    # monthly_miles = request.form.get("monthly_miles")
    # try:
    #    monthly_miles = int(monthly_miles)
    #    if monthly_miles < 0:
    #        monthly_miles = 1000
    # except Exception:
    #    monthly_miles = 1000

    monthly_miles = 1000

    evs_fuel_costs = []
    evs_co2_emissions = []

    for ev in evs:
        wpm = int(ev[3][:-5])
        evs_fuel_costs.append(
            round(helper_general.get_ev_cost_1_month(wpm, monthly_miles), 2)
        )
        watts_required = helper_general.get_watts_required(wpm, monthly_miles)
        evs_co2_emissions.append(
            round(helper_general.get_ev_co2_1_month(watts_required), 2)
        )

    print(evs_fuel_costs)
    print(evs_co2_emissions)

    denominations = [1, 3, 6, 12, 60, 120]
    meters_in_1_mile = 1609 * monthly_miles

    user_co2_emissions_1_month = helper_routes.generate_co2_emissions(
        meters_in_1_mile, "driving", user_fuel_type
    )
    fuel_price = helper_routes.get_fuel_price(user_fuel_type)
    user_fuel_used_1_month = helper_routes.calculate_fuel_used(
        monthly_miles, float(user_car_mpg)
    )
    user_fuel_cost_1_month = helper_routes.calculate_fuel_cost(
        user_fuel_used_1_month, fuel_price
    )

    user_fuel_costs = [
        "{:,}".format(round(user_fuel_cost_1_month * x)) for x in denominations
    ]
    user_co2_emissions = [
        "{:,}".format(round(user_co2_emissions_1_month * x)) for x in denominations
    ]

    # foreach car in evs calculate the co2 emissions and fuel cost and save into a list
    evs_co2_emissions = []
    evs_fuel_costs = []

    for ev in evs:
        wpm = int(ev[3][:-5])

        watts_required = helper_general.get_watts_required(wpm, 1000)
        co2_emissions_1_month = helper_general.get_ev_co2_1_month(watts_required)

        fuel_cost_1_month = helper_general.get_ev_cost_1_month(wpm, 1000)

        evs_co2_emissions.append(co2_emissions_1_month)
        evs_fuel_costs.append(fuel_cost_1_month)

    fuel_cost_1_month = helper_general.get_ev_cost_1_month(wpm, 1000)

    fuel_costs = ["{:,}".format(round(fuel_cost_1_month * x)) for x in denominations]

    return render_template(
        "trends.html",
        username=session.get("username"),
        comparison=False,
        evs=evs,
        user_car_make=user_car_make,
        user_car_mpg=user_car_mpg,
        user_fuel_type=user_fuel_type,
        user_engine_size=user_engine_size,
        user_fuel_costs=user_fuel_costs,
        user_co2_emissions=user_co2_emissions,
        fuel_costs=fuel_costs,
        evs_co2_emissions=evs_co2_emissions,
        evs_fuel_costs=evs_fuel_costs,
        co2_emissions=user_co2_emissions,
    )

    """elif request.method == "POST":

        car = request.form.get("car")
        wpm = request.form.get("wpm")

        if wpm:
            wpm = int(wpm[:-5])

        fuel_cost_1_month = helper_general.get_ev_cost_1_month(wpm, monthly_miles)

        fuel_costs = [
            "{:,}".format(round(fuel_cost_1_month * x)) for x in denominations
        ]

        watts_required = helper_general.get_watts_required(wpm, monthly_miles)
        co2_emissions_1_month = helper_general.get_ev_co2_1_month(watts_required)

        print(evs)

        co2_emissions = [
            "{:,}".format(round(co2_emissions_1_month * x)) for x in denominations
        ]

        return render_template(
            "trends.html",
            username=session.get("username"),
            comparison=True,
            evs=evs,
            user_car_make=user_car_make,
            user_car_mpg=user_car_mpg,
            user_fuel_type=user_fuel_type,
            user_engine_size=user_engine_size,
            user_fuel_costs=user_fuel_costs,
            user_co2_emissions=user_co2_emissions,
            car_make=car,
            car_wpm=wpm,
            fuel_costs=fuel_costs,
            co2_emissions=co2_emissions,
        )
            evs_fuel_costs=evs_fuel_costs,
            evs_co2_emissions=evs_co2_emissions,
            monthly_miles=monthly_miles,
        )"""
