from datetime import datetime

from models.message import Message
from models.tailor import Tailor


def format_currency(value):
    """Format a numeric value as Indian Rupees."""
    if value is None:
        return "N/A"

    try:
        return f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_date(dt, format_str="%b %d, %Y"):
    """Format a date or datetime safely."""
    if not dt:
        return ""

    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except (TypeError, ValueError):
            return dt

    try:
        return dt.strftime(format_str)
    except (AttributeError, ValueError):
        return str(dt)


def get_unread_count(user_id):
    """Return the number of unread messages for a user."""
    if not user_id:
        return 0

    return (
        Message.query
        .filter_by(
            receiver_id=user_id,
            is_read=False,
        )
        .count()
    )


def match_tailors_for_request(
    clothing_type=None,
    service_type=None,
    city=None,
):
    """
    Rank active tailors according to the customer's request.

    Matching considers:
    - city
    - specialization
    - description
    - rating
    - experience
    - number of reviews
    - verification
    - availability
    """

    query = Tailor.query.filter_by(is_active=True)

    if city:
        query = query.filter(
            Tailor.city.ilike(f"%{city.strip()}%")
        )

    tailors = query.all()

    search_terms = []

    if clothing_type:
        search_terms.append(
            clothing_type.strip().lower()
        )

    if service_type:
        search_terms.append(
            service_type.strip().lower()
        )

    scored_tailors = []

    for tailor in tailors:
        score = 0.0

        rating = float(tailor.rating or 0)
        experience = int(tailor.experience or 0)
        reviews = int(tailor.total_reviews or 0)

        specialization = (
            tailor.specialization or ""
        ).lower()

        description = (
            tailor.description or ""
        ).lower()

        shop_name = (
            tailor.shop_name or ""
        ).lower()

        tailor_city = (
            tailor.city or ""
        ).lower()

        # Rating contribution: up to 50 points.
        score += min(rating, 5) * 10

        # Specialization / description matching.
        for term in search_terms:
            if not term:
                continue

            if term in specialization:
                score += 25
            elif term in description:
                score += 10
            elif term in shop_name:
                score += 5

        # Experience contribution: up to 15 points.
        score += min(experience, 15)

        # Review count contribution: up to 10 points.
        score += min(reviews, 10)

        # Verified tailor bonus.
        if tailor.is_verified:
            score += 10

        # Availability bonus.
        availability = (
            str(tailor.availability or "")
            .strip()
            .lower()
        )

        if availability in {
            "available",
            "open",
            "yes",
            "true",
            "1",
        }:
            score += 8

        # Exact city match bonus.
        if city and city.strip().lower() == tailor_city:
            score += 15

        scored_tailors.append(
            (tailor, score)
        )

    scored_tailors.sort(
        key=lambda item: (
            item[1],
            float(item[0].rating or 0),
            int(item[0].total_reviews or 0),
        ),
        reverse=True,
    )

    return [
        tailor
        for tailor, _score in scored_tailors
    ]


TN_LOCATION_COORDINATES = {
    # Chennai Localities
    "t nagar": (13.0418, 80.2341),
    "t. nagar": (13.0418, 80.2341),
    "anna nagar": (13.0850, 80.2101),
    "mylapore": (13.0368, 80.2676),
    "adyar": (13.0012, 80.2565),
    "nungambakkam": (13.0604, 80.2425),
    "velachery": (12.9815, 80.2180),
    "porur": (13.0382, 80.1565),
    "tambaram": (12.9249, 80.1000),
    "guindy": (13.0067, 80.2023),
    "purasawalkam": (13.0903, 80.2570),
    "egmore": (13.0732, 80.2609),
    "triplicane": (13.0587, 80.2757),
    "chromepet": (12.9516, 80.1462),
    "alwarpet": (13.0372, 80.2523),
    "gopalapuram": (13.0532, 80.2520),
    "royapettah": (13.0594, 80.2642),
    "kilpauk": (13.0784, 80.2437),
    "chennai": (13.0827, 80.2707),

    # Madurai Localities
    "kk nagar": (9.9392, 78.1512),
    "k.k. nagar": (9.9392, 78.1512),
    "simmakkal": (9.9280, 78.1210),
    "tallakulam": (9.9360, 78.1340),
    "villapuram": (9.9020, 78.1310),
    "west chitrai": (9.9195, 78.1205),
    "south veli": (9.9150, 78.1180),
    "town hall road": (9.9240, 78.1150),
    "madurai": (9.9252, 78.1198),

    # Coimbatore Localities
    "rs puram": (11.0116, 76.9482),
    "r.s. puram": (11.0116, 76.9482),
    "gandhipuram": (11.0183, 76.9644),
    "cross cut road": (11.0183, 76.9644),
    "peelamedu": (11.0310, 77.0160),
    "saibaba colony": (11.0330, 76.9480),
    "singanallur": (10.9990, 77.0250),
    "saravanampatti": (11.0797, 76.9997),
    "sukrawarpet": (10.9980, 76.9580),
    "coimbatore": (11.0168, 76.9558),

    # Tiruchirappalli (Trichy) Localities
    "thillai nagar": (10.8240, 78.6860),
    "srirangam": (10.8622, 78.6908),
    "cantonment": (10.8060, 78.6870),
    "big bazaar": (10.7905, 78.7047),
    "trichy": (10.7905, 78.7047),
    "tiruchirappalli": (10.7905, 78.7047),

    # Salem Localities
    "fairlands": (11.6780, 78.1410),
    "saradha college": (11.6643, 78.1460),
    "meyyanur": (11.6710, 78.1320),
    "salem": (11.6643, 78.1460),

    # Erode Localities
    "perundurai road": (11.3410, 77.7172),
    "brough road": (11.3480, 77.7250),
    "erode": (11.3410, 77.7172),

    # Tirunelveli Localities
    "palayamkottai": (8.7139, 77.7567),
    "tirunelveli town": (8.7280, 77.7080),
    "high ground": (8.7139, 77.7567),
    "tirunelveli": (8.7139, 77.7567),

    # Kanchipuram
    "gandhi road": (12.8342, 79.7036),
    "ennaikara": (12.8290, 79.7120),
    "kanchipuram": (12.8342, 79.7036),

    # Vellore
    "sathuvachari": (12.9165, 79.1325),
    "katpadi": (12.9698, 79.1399),
    "officers line": (12.9230, 79.1380),
    "vellore": (12.9165, 79.1325),

    # Thanjavur
    "south main street": (10.7870, 79.1378),
    "thanjavur": (10.7870, 79.1378),

    # Tiruppur
    "avinashi road": (11.1085, 77.3411),
    "tiruppur": (11.1085, 77.3411),

    # Dindigul
    "salai road": (10.3673, 77.9803),
    "dindigul": (10.3673, 77.9803),

    # Nilgiris
    "ooty": (11.4102, 76.6950),
    "coonoor": (11.3530, 76.7959),

    # Kanyakumari
    "nagercoil": (8.1833, 77.4119),
    "kanyakumari": (8.0883, 77.5385),

    # Other Tamil Nadu Districts
    "karur": (10.9601, 78.0766),
    "namakkal": (11.2189, 78.1674),
    "cuddalore": (11.7480, 79.7714),
    "dharmapuri": (12.1211, 78.1582),
    "krishnagiri": (12.5186, 78.2137),
    "nagapattinam": (10.7672, 79.8449),
    "pudukkottai": (10.3833, 78.8001),
    "ramanathapuram": (9.3639, 78.8395),
    "sivaganga": (9.8433, 78.4809),
    "theni": (10.0104, 77.4768),
    "thiruvallur": (13.1439, 79.9079),
    "thiruvarur": (10.7717, 79.6366),
    "thoothukudi": (8.7642, 78.1348),
    "tiruvannamalai": (12.2253, 79.0747),
    "viluppuram": (11.9401, 79.4861),
    "virudhunagar": (9.5680, 77.9624),
    "ariyalur": (11.1401, 79.0786),
    "perambalur": (11.2342, 78.8787),
    "chengalpattu": (12.6819, 79.9888),
    "kallakurichi": (11.7374, 78.9634),
    "ranipet": (12.9272, 79.3330),
    "tenkasi": (8.9594, 77.3152),
    "tirupathur": (12.4958, 78.5678),
    "mayiladuthurai": (11.1018, 79.6522),
}


def resolve_tamil_nadu_coordinates(city=None, area=None, address=None):
    """
    Resolve realistic latitude and longitude for any place or area in Tamil Nadu.
    Considers area/locality first, then city/district, with a micro studio jitter.
    """
    import random

    search_text = f"{area or ''} {address or ''} {city or ''}".lower()

    # 1. Search for specific locality/area match
    for place_key, coords in TN_LOCATION_COORDINATES.items():
        if place_key in search_text:
            jitter_lat = round(random.uniform(-0.005, 0.005), 5)
            jitter_lng = round(random.uniform(-0.005, 0.005), 5)
            return coords[0] + jitter_lat, coords[1] + jitter_lng

    # 2. Check city specifically
    if city:
        city_lower = city.strip().lower()
        for place_key, coords in TN_LOCATION_COORDINATES.items():
            if place_key == city_lower or place_key in city_lower:
                jitter_lat = round(random.uniform(-0.008, 0.008), 5)
                jitter_lng = round(random.uniform(-0.008, 0.008), 5)
                return coords[0] + jitter_lat, coords[1] + jitter_lng

    # 3. Default to center of Tamil Nadu (Trichy / Tiruchirappalli)
    return 10.7905 + round(random.uniform(-0.01, 0.01), 5), 78.7047 + round(random.uniform(-0.01, 0.01), 5)