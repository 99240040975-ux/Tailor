from flask import Blueprint, jsonify, request
from models import db
from models.location import State, District, Taluk, City, Town, Village, Locality

locations_bp = Blueprint('locations', __name__)


@locations_bp.route('/states', methods=['GET'])
def get_states():
    """Return all states, placing Tamil Nadu at the top if present."""
    states = State.query.order_by(State.name.asc()).all()
    # Prioritize Tamil Nadu
    tn_first = []
    others = []
    for s in states:
        if 'TAMIL NADU' in s.name.upper() or s.code == '33':
            tn_first.append(s.to_dict())
        else:
            others.append(s.to_dict())
    return jsonify(tn_first + others)


@locations_bp.route('/districts/<int:state_id>', methods=['GET'])
def get_districts(state_id):
    """Return all districts for a given state."""
    districts = District.query.filter_by(state_id=state_id).order_by(District.name.asc()).all()
    return jsonify([d.to_dict() for d in districts])


@locations_bp.route('/taluks/<int:district_id>', methods=['GET'])
def get_taluks(district_id):
    """Return all taluks/sub-districts for a given district."""
    taluks = Taluk.query.filter_by(district_id=district_id).order_by(Taluk.name.asc()).all()
    return jsonify([t.to_dict() for t in taluks])


@locations_bp.route('/cities/<int:taluk_id>', methods=['GET'])
def get_cities(taluk_id):
    """
    Return cities for a given taluk.
    If taluk_id is 0 or query param district_id is provided, returns cities for the district.
    """
    district_id = request.args.get('district_id', type=int)
    if taluk_id > 0:
        cities = City.query.filter_by(taluk_id=taluk_id).order_by(City.name.asc()).all()
        # Fallback to district-level if taluk has no mapped municipal corporations
        if not cities and district_id:
            cities = City.query.filter_by(district_id=district_id).order_by(City.name.asc()).all()
    elif district_id:
        cities = City.query.filter_by(district_id=district_id).order_by(City.name.asc()).all()
    else:
        cities = []
    return jsonify([c.to_dict() for c in cities])


@locations_bp.route('/towns/<int:city_id>', methods=['GET'])
def get_towns(city_id):
    """
    Return towns for a given city.
    If city_id is 0, checks query param taluk_id or district_id.
    """
    taluk_id = request.args.get('taluk_id', type=int)
    district_id = request.args.get('district_id', type=int)

    if city_id > 0:
        towns = Town.query.filter_by(city_id=city_id).order_by(Town.name.asc()).all()
        if not towns and taluk_id:
            towns = Town.query.filter_by(taluk_id=taluk_id).order_by(Town.name.asc()).all()
    elif taluk_id:
        towns = Town.query.filter_by(taluk_id=taluk_id).order_by(Town.name.asc()).all()
    elif district_id:
        towns = Town.query.filter_by(district_id=district_id).order_by(Town.name.asc()).all()
    else:
        towns = []
    return jsonify([t.to_dict() for t in towns])


@locations_bp.route('/towns-by-taluk/<int:taluk_id>', methods=['GET'])
def get_towns_by_taluk(taluk_id):
    """Return all towns under a given taluk."""
    towns = Town.query.filter_by(taluk_id=taluk_id).order_by(Town.name.asc()).all()
    return jsonify([t.to_dict() for t in towns])


@locations_bp.route('/villages/<int:town_id>', methods=['GET'])
def get_villages(town_id):
    """
    Return villages for a given town or fallback to taluk_id query parameter.
    """
    taluk_id = request.args.get('taluk_id', type=int)
    if town_id > 0:
        villages = Village.query.filter_by(town_id=town_id).order_by(Village.name.asc()).limit(200).all()
        if not villages and taluk_id:
            villages = Village.query.filter_by(taluk_id=taluk_id).order_by(Village.name.asc()).limit(200).all()
    elif taluk_id:
        villages = Village.query.filter_by(taluk_id=taluk_id).order_by(Village.name.asc()).limit(200).all()
    else:
        villages = []
    return jsonify([v.to_dict() for v in villages])


@locations_bp.route('/villages-by-taluk/<int:taluk_id>', methods=['GET'])
def get_villages_by_taluk(taluk_id):
    """Return all revenue villages under a given taluk."""
    villages = Village.query.filter_by(taluk_id=taluk_id).order_by(Village.name.asc()).all()
    return jsonify([v.to_dict() for v in villages])


@locations_bp.route('/search', methods=['GET'])
def search_locations():
    """Autocomplete search across districts, taluks, cities, towns, and villages."""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])

    results = []
    # Search districts
    districts = District.query.filter(District.name.ilike(f'%{query}%')).limit(5).all()
    for d in districts:
        results.append({
            'type': 'district',
            'id': d.id,
            'name': d.name,
            'display': f"{d.name} (District)"
        })

    # Search taluks
    taluks = Taluk.query.filter(Taluk.name.ilike(f'%{query}%')).limit(5).all()
    for t in taluks:
        results.append({
            'type': 'taluk',
            'id': t.id,
            'district_id': t.district_id,
            'name': t.name,
            'display': f"{t.name} (Taluk, {t.district.name})"
        })

    # Search cities / towns
    cities = City.query.filter(City.name.ilike(f'%{query}%')).limit(5).all()
    for c in cities:
        results.append({
            'type': 'city',
            'id': c.id,
            'name': c.name,
            'display': f"{c.name} (City, {c.district.name})"
        })

    towns = Town.query.filter(Town.name.ilike(f'%{query}%')).limit(5).all()
    for tn in towns:
        results.append({
            'type': 'town',
            'id': tn.id,
            'name': tn.name,
            'display': f"{tn.name} (Town, {tn.district.name})"
        })

    villages = Village.query.filter(Village.name.ilike(f'%{query}%')).limit(10).all()
    for v in villages:
        taluk_str = f", {v.taluk.name}" if v.taluk else ""
        results.append({
            'type': 'village',
            'id': v.id,
            'name': v.name,
            'display': f"{v.name} (Village{taluk_str})"
        })

    return jsonify(results)
