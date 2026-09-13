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