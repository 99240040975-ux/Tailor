from datetime import datetime
from models.tailor import Tailor
from models.message import Message


def format_currency(value):
    if value is None:
        return 'N/A'
    try:
        return f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_date(dt, format_str='%b %d, %Y'):
    if not dt:
        return ''
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except Exception:
            return dt
    return dt.strftime(format_str)


def get_unread_count(user_id):
    if not user_id:
        return 0
    return Message.query.filter_by(receiver_id=user_id, is_read=False).count()


def match_tailors_for_request(clothing_type, service_type, city=None):
    """
    Intelligent tailor matching algorithm:
    Matches based on specialization keywords, city location, availability, and rating.
    """
    query = Tailor.query.filter_by(availability=True)
    if city:
        query = query.filter(Tailor.city.ilike(f"%{city}%"))

    tailors = query.all()
    scored_tailors = []

    search_terms = []
    if clothing_type:
        search_terms.append(clothing_type.lower())
    if service_type:
        search_terms.append(service_type.lower())

    for tailor in tailors:
        score = 0.0
        # Rating contribution (0 to 50 pts)
        score += (tailor.rating or 0) * 10

        # Specialization match (0 to 30 pts)
        spec = (tailor.specialization or '').lower()
        desc = (tailor.description or '').lower()
        for term in search_terms:
            if term in spec:
                score += 25
            elif term in desc:
                score += 10

        # Experience contribution (up to 15 pts)
        score += min(tailor.experience or 0, 15)

        # Reviews contribution (up to 10 pts)
        score += min(tailor.total_reviews or 0, 10)

        # Verified bonus (10 pts)
        if tailor.is_verified:
            score += 10

        scored_tailors.append((tailor, score))

    scored_tailors.sort(key=lambda x: x[1], reverse=True)
    return [t[0] for t in scored_tailors]
