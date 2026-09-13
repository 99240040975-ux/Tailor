from flask import Blueprint, jsonify, request

from models.location import (
    City,
    District,
    Locality,
    State,
    Taluk,
    Town,
    Village,
)


locations_bp = Blueprint("locations", __name__)


def _json_list(items):
    """Convert SQLAlchemy location objects into JSON-safe dictionaries."""
    return [item.to_dict() for item in items]


# ------------------------------------------------------------
# States
# ------------------------------------------------------------

@locations_bp.route("/states", methods=["GET"])
def get_states():
    """Return all states with Tamil Nadu first."""
    states = (
        State.query
        .order_by(State.name.asc())
        .all()
    )

    tamil_nadu = []
    others = []

    for state in states:
        name = (state.name or "").upper()
        code = str(state.code or "").upper()

        if (
            "TAMIL NADU" in name
            or code == "TN"
            or code == "33"
        ):
            tamil_nadu.append(state.to_dict())
        else:
            others.append(state.to_dict())

    return jsonify(tamil_nadu + others)


# ------------------------------------------------------------
# Districts
# ------------------------------------------------------------

@locations_bp.route(
    "/districts/<int:state_id>",
    methods=["GET"],
)
def get_districts(state_id):
    """Return districts belonging to a state."""
    districts = (
        District.query
        .filter_by(state_id=state_id)
        .order_by(District.name.asc())
        .all()
    )

    return jsonify(_json_list(districts))


# ------------------------------------------------------------
# Taluks
# ------------------------------------------------------------

@locations_bp.route(
    "/taluks/<int:district_id>",
    methods=["GET"],
)
def get_taluks(district_id):
    """Return taluks belonging to a district."""
    taluks = (
        Taluk.query
        .filter_by(district_id=district_id)
        .order_by(Taluk.name.asc())
        .all()
    )

    return jsonify(_json_list(taluks))


# ------------------------------------------------------------
# Cities
# ------------------------------------------------------------

@locations_bp.route(
    "/cities/<int:taluk_id>",
    methods=["GET"],
)
def get_cities(taluk_id):
    """
    Return cities for a taluk.

    If no cities are mapped to the taluk, optionally fall back
    to the supplied district_id.
    """
    district_id = request.args.get(
        "district_id",
        type=int,
    )

    cities = []

    if taluk_id > 0:
        cities = (
            City.query
            .filter_by(taluk_id=taluk_id)
            .order_by(City.name.asc())
            .all()
        )

        if not cities and district_id:
            cities = (
                City.query
                .filter_by(district_id=district_id)
                .order_by(City.name.asc())
                .all()
            )

    elif district_id:
        cities = (
            City.query
            .filter_by(district_id=district_id)
            .order_by(City.name.asc())
            .all()
        )

    return jsonify(_json_list(cities))


# ------------------------------------------------------------
# Towns
# ------------------------------------------------------------

@locations_bp.route(
    "/towns/<int:city_id>",
    methods=["GET"],
)
def get_towns(city_id):
    """
    Return towns for a city.

    Supports fallback to taluk or district when needed.
    """
    taluk_id = request.args.get(
        "taluk_id",
        type=int,
    )

    district_id = request.args.get(
        "district_id",
        type=int,
    )

    towns = []

    if city_id > 0:
        towns = (
            Town.query
            .filter_by(city_id=city_id)
            .order_by(Town.name.asc())
            .all()
        )

        if not towns and taluk_id:
            towns = (
                Town.query
                .filter_by(taluk_id=taluk_id)
                .order_by(Town.name.asc())
                .all()
            )

        if not towns and district_id:
            towns = (
                Town.query
                .filter_by(district_id=district_id)
                .order_by(Town.name.asc())
                .all()
            )

    elif taluk_id:
        towns = (
            Town.query
            .filter_by(taluk_id=taluk_id)
            .order_by(Town.name.asc())
            .all()
        )

    elif district_id:
        towns = (
            Town.query
            .filter_by(district_id=district_id)
            .order_by(Town.name.asc())
            .all()
        )

    return jsonify(_json_list(towns))


@locations_bp.route(
    "/towns-by-taluk/<int:taluk_id>",
    methods=["GET"],
)
def get_towns_by_taluk(taluk_id):
    """Return all towns under a taluk."""
    towns = (
        Town.query
        .filter_by(taluk_id=taluk_id)
        .order_by(Town.name.asc())
        .all()
    )

    return jsonify(_json_list(towns))


# ------------------------------------------------------------
# Villages
# ------------------------------------------------------------

@locations_bp.route(
    "/villages/<int:town_id>",
    methods=["GET"],
)
def get_villages(town_id):
    """
    Return villages for a town.

    Falls back to taluk_id when the town has no mapped villages.
    """
    taluk_id = request.args.get(
        "taluk_id",
        type=int,
    )

    villages = []

    if town_id > 0:
        villages = (
            Village.query
            .filter_by(town_id=town_id)
            .order_by(Village.name.asc())
            .limit(200)
            .all()
        )

        if not villages and taluk_id:
            villages = (
                Village.query
                .filter_by(taluk_id=taluk_id)
                .order_by(Village.name.asc())
                .limit(200)
                .all()
            )

    elif taluk_id:
        villages = (
            Village.query
            .filter_by(taluk_id=taluk_id)
            .order_by(Village.name.asc())
            .limit(200)
            .all()
        )

    return jsonify(_json_list(villages))


@locations_bp.route(
    "/villages-by-taluk/<int:taluk_id>",
    methods=["GET"],
)
def get_villages_by_taluk(taluk_id):
    """Return all villages under a taluk."""
    villages = (
        Village.query
        .filter_by(taluk_id=taluk_id)
        .order_by(Village.name.asc())
        .all()
    )

    return jsonify(_json_list(villages))


# ------------------------------------------------------------
# Localities
# ------------------------------------------------------------

@locations_bp.route(
    "/localities",
    methods=["GET"],
)
def get_localities():
    """
    Return localities using one of the supported parent IDs:
    city_id, town_id, or village_id.
    """
    city_id = request.args.get(
        "city_id",
        type=int,
    )

    town_id = request.args.get(
        "town_id",
        type=int,
    )

    village_id = request.args.get(
        "village_id",
        type=int,
    )

    query = Locality.query

    if city_id:
        query = query.filter_by(
            city_id=city_id
        )

    elif town_id:
        query = query.filter_by(
            town_id=town_id
        )

    elif village_id:
        query = query.filter_by(
            village_id=village_id
        )

    else:
        return jsonify([])

    localities = (
        query
        .order_by(Locality.name.asc())
        .limit(200)
        .all()
    )

    return jsonify(_json_list(localities))


# ------------------------------------------------------------
# Location search / autocomplete
# ------------------------------------------------------------

@locations_bp.route(
    "/search",
    methods=["GET"],
)
def search_locations():
    """
    Search across districts, taluks, cities, towns,
    villages, and localities.
    """
    query_text = request.args.get(
        "q",
        "",
    ).strip()

    if len(query_text) < 2:
        return jsonify([])

    pattern = f"%{query_text}%"
    results = []

    # Districts
    districts = (
        District.query
        .filter(
            District.name.ilike(pattern)
        )
        .order_by(District.name.asc())
        .limit(5)
        .all()
    )

    for district in districts:
        results.append({
            "type": "district",
            "id": district.id,
            "name": district.name,
            "display": (
                f"{district.name} (District)"
            ),
        })

    # Taluks
    taluks = (
        Taluk.query
        .filter(
            Taluk.name.ilike(pattern)
        )
        .order_by(Taluk.name.asc())
        .limit(5)
        .all()
    )

    for taluk in taluks:
        district_name = (
            taluk.district.name
            if taluk.district
            else ""
        )

        display = f"{taluk.name} (Taluk"

        if district_name:
            display += f", {district_name}"

        display += ")"

        results.append({
            "type": "taluk",
            "id": taluk.id,
            "district_id": taluk.district_id,
            "name": taluk.name,
            "display": display,
        })

    # Cities
    cities = (
        City.query
        .filter(
            City.name.ilike(pattern)
        )
        .order_by(City.name.asc())
        .limit(5)
        .all()
    )

    for city in cities:
        district_name = (
            city.district.name
            if city.district
            else ""
        )

        display = f"{city.name} (City"

        if district_name:
            display += f", {district_name}"

        display += ")"

        results.append({
            "type": "city",
            "id": city.id,
            "district_id": city.district_id,
            "taluk_id": city.taluk_id,
            "name": city.name,
            "display": display,
        })

    # Towns
    towns = (
        Town.query
        .filter(
            Town.name.ilike(pattern)
        )
        .order_by(Town.name.asc())
        .limit(5)
        .all()
    )

    for town in towns:
        district_name = (
            town.district.name
            if town.district
            else ""
        )

        display = f"{town.name} (Town"

        if district_name:
            display += f", {district_name}"

        display += ")"

        results.append({
            "type": "town",
            "id": town.id,
            "district_id": town.district_id,
            "taluk_id": town.taluk_id,
            "city_id": town.city_id,
            "name": town.name,
            "display": display,
        })

    # Villages
    villages = (
        Village.query
        .filter(
            Village.name.ilike(pattern)
        )
        .order_by(Village.name.asc())
        .limit(10)
        .all()
    )

    for village in villages:
        taluk_name = (
            village.taluk.name
            if village.taluk
            else ""
        )

        display = f"{village.name} (Village"

        if taluk_name:
            display += f", {taluk_name}"

        display += ")"

        results.append({
            "type": "village",
            "id": village.id,
            "district_id": village.district_id,
            "taluk_id": village.taluk_id,
            "town_id": village.town_id,
            "name": village.name,
            "display": display,
        })

    # Localities
    localities = (
        Locality.query
        .filter(
            Locality.name.ilike(pattern)
        )
        .order_by(Locality.name.asc())
        .limit(10)
        .all()
    )

    for locality in localities:
        results.append({
            "type": "locality",
            "id": locality.id,
            "city_id": locality.city_id,
            "town_id": locality.town_id,
            "village_id": locality.village_id,
            "name": locality.name,
            "pincode": locality.pincode,
            "display": (
                f"{locality.name} (Locality)"
            ),
        })

    return jsonify(results)