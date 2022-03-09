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


@trends_blueprint.route("/trends", methods=["GET"])
@limiter.limit("15/minute")
def show_trends():
    if "username" not in session:
        return redirect("/")

    car_make, car_mpg, fuel_type, engine_size = helper_routes.get_car(
        session.get("username")
    )

    return redirect(
        url_for(
            "trends.show_car",
            car=car_make,
            mpg=car_mpg,
            fuel=fuel_type,
            engine=engine_size,
        )
    )


@trends_blueprint.route("/trends/view_car", methods=["GET"])
@limiter.limit("15/minute")
def show_car():
    if "username" not in session:
        return redirect("/")

    car_make, car_mpg, fuel_type, engine_size = helper_routes.get_car(
        session.get("username")
    )

    evs = helper_general.get_best_efficiency_electric(helper_general.get_electric_cars())

    print(request.args)
    details = {k: v for k, v in request.args.items()} if request.args else {}
    print(details)

    fuel_price = helper_routes.get_fuel_price(details.get("fuel"))
    fuel_used_1_month = helper_routes.calculate_fuel_used(
        1000, float(details.get("mpg"))
    )
    fuel_cost_1_month = helper_routes.calculate_fuel_cost(fuel_used_1_month, fuel_price)
    co2_emissions_1_month = helper_routes.generate_co2_emissions(
        1609340, "driving", details.get("fuel")
    )
    denominations = [1, 3, 6, 12, 60, 120]
    fuel_costs = [round(fuel_cost_1_month * x) for x in denominations]
    co2_emissions = [round(co2_emissions_1_month * x) for x in denominations]
    print(fuel_costs)
    print(co2_emissions)

    return render_template(
        "trends.html",
        username=session.get("username"),
        evs=evs,
        car_make=car_make,
        car_mpg=car_mpg,
        fuel_type=fuel_type,
        engine_size=engine_size,
        fuel_costs=fuel_costs,
        co2_emissions=co2_emissions,
    )
