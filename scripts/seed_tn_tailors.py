"""
Populate and update tailors across Tamil Nadu with authentic coordinates,
districts, addresses, and specialties for the live map.
"""
import random
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from models.tailor import Tailor
from models.location import District, State

TN_LOCATIONS = [
    {
        "city": "Chennai",
        "district_id": 547,
        "lat": 13.0418,
        "lng": 80.2341,
        "address": "42 Usman Road, T. Nagar, Chennai - 600017",
        "specialties": "Silk Saree Blouses, Designer Lehengas, Zari Embroidery"
    },
    {
        "city": "Chennai",
        "district_id": 547,
        "lat": 13.0850,
        "lng": 80.2101,
        "address": "15 2nd Avenue, Anna Nagar, Chennai - 600040",
        "specialties": "Bespoke Men's Suits, Tuxedos, Formal Blazers"
    },
    {
        "city": "Chennai",
        "district_id": 547,
        "lat": 13.0368,
        "lng": 80.2676,
        "address": "88 Luz Church Road, Mylapore, Chennai - 600004",
        "specialties": "Traditional Kanjivaram Blouses, Salwar Suits, Alterations"
    },
    {
        "city": "Madurai",
        "district_id": 557,
        "lat": 9.9195,
        "lng": 78.1205,
        "address": "12 West Chitrai Street, Near Meenakshi Temple, Madurai - 625001",
        "specialties": "Chungudi Saree Blouses, Bridal Aari Work, Pattu Pavadai"
    },
    {
        "city": "Madurai",
        "district_id": 557,
        "lat": 9.9392,
        "lng": 78.1512,
        "address": "76 East Veli Street, KK Nagar, Madurai - 625020",
        "specialties": "Men's Safari Suits, Linen Shirts, Traditional Dhoti Shirts"
    },
    {
        "city": "Coimbatore",
        "district_id": 548,
        "lat": 11.0116,
        "lng": 76.9482,
        "address": "29 DB Road, RS Puram, Coimbatore - 641002",
        "specialties": "Contemporary Designer Blouses, Gowns, Bespoke Suits"
    },
    {
        "city": "Coimbatore",
        "district_id": 548,
        "lat": 11.0183,
        "lng": 76.9644,
        "address": "104 Cross Cut Road, Gandhipuram, Coimbatore - 641012",
        "specialties": "Cotton Kurtas, Formal Trousers, Express Alterations"
    },
    {
        "city": "Tiruchirappalli",
        "district_id": 569,
        "lat": 10.8240,
        "lng": 78.6860,
        "address": "34 11th Cross, Thillai Nagar, Tiruchirappalli - 620018",
        "specialties": "Bridal Lehengas, Maggam Work, Silk Saree Stitching"
    },
    {
        "city": "Tiruchirappalli",
        "district_id": 569,
        "lat": 10.7905,
        "lng": 78.7047,
        "address": "55 Big Bazaar Street, Trichy Fort, Tiruchirappalli - 620002",
        "specialties": "Men's Ethnic Sherwanis, Kurta Pyjama, Suiting"
    },
    {
        "city": "Salem",
        "district_id": 564,
        "lat": 11.6643,
        "lng": 78.1460,
        "address": "18 Saradha College Road, Fairlands, Salem - 636016",
        "specialties": "Pure Silk Blouses, Dhoti Sets, Precision Alterations"
    },
    {
        "city": "Tirunelveli",
        "district_id": 570,
        "lat": 8.7139,
        "lng": 77.7567,
        "address": "45 High Ground Road, Palayamkottai, Tirunelveli - 627002",
        "specialties": "Traditional Pattu Blouses, Men's Shirts, Custom Fits"
    },
    {
        "city": "Erode",
        "district_id": 552,
        "lat": 11.3410,
        "lng": 77.7172,
        "address": "62 Brough Road, Erode - 638001",
        "specialties": "Textile Weave Custom Tailoring, Kurtis, Linen Suits"
    },
    {
        "city": "Kanchipuram",
        "district_id": 553,
        "lat": 12.8342,
        "lng": 79.7036,
        "address": "112 Gandhi Road, Near Ekambareswarar, Kanchipuram - 631501",
        "specialties": "Master Kanchipuram Silk Saree Blouses, Heavy Zari Work"
    },
    {
        "city": "Vellore",
        "district_id": 575,
        "lat": 12.9165,
        "lng": 79.1325,
        "address": "23 Officer's Line, Anna Salai, Vellore - 632001",
        "specialties": "Uniforms, Western Suits, Designer Blouses"
    },
    {
        "city": "Thanjavur",
        "district_id": 566,
        "lat": 10.7870,
        "lng": 79.1378,
        "address": "81 South Main Street, Thanjavur - 613001",
        "specialties": "Thanjavur Art Inspired Blouses, Traditional Ethnic Wear"
    },
    {
        "city": "Tiruppur",
        "district_id": 571,
        "lat": 11.1085,
        "lng": 77.3411,
        "address": "19 Avinashi Road, Tiruppur - 641602",
        "specialties": "Knitwear Alterations, Custom Cotton Fits, Polos"
    },
    {
        "city": "Dindigul",
        "district_id": 551,
        "lat": 10.3673,
        "lng": 77.9803,
        "address": "37 Salai Road, Dindigul - 624001",
        "specialties": "Men's Formal Suits, Wedding Kurta Sets, Alterations"
    }
]

SHOP_NAMES = [
    "Meenakshi Royal Silks & Tailors",
    "Chennai Bespoke Studio",
    "Kongu Master Crafters",
    "Kanchi Silk Couture Atelier",
    "Cauvery Threads & Tailoring",
    "Chola Heritage Bespoke",
    "Southern Needlecraft Studio",
    "Mylapore Classic Fits",
    "Nellai Artisan Tailors",
    "Salem Silk & Stitch Works",
    "The Royal Loom & Shears",
    "Annam Crafts & Alterations"
]

def seed_tn_tailors():
    from models.user import User
    # Ensure Tamil Nadu State exists
    tn_state = State.query.filter(
        db.or_(
            State.name.ilike("Tamil Nadu"),
            State.code.ilike("TN")
        )
    ).first()
    state_id = tn_state.id if tn_state else 31

    # If we have fewer than len(TN_LOCATIONS) tailors, create missing tailors
    current_tailor_count = Tailor.query.count()
    if current_tailor_count < len(TN_LOCATIONS):
        for idx in range(current_tailor_count, len(TN_LOCATIONS)):
            loc = TN_LOCATIONS[idx]
            email = f"tailor_{loc['city'].lower()}_{idx+1}@tailorconnect.test"
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    name=f"Master {loc['city']} Artisan",
                    email=email,
                    role="tailor",
                    phone=f"987654{idx:04d}",
                    is_active=True
                )
                user.set_password("password123")
                db.session.add(user)
                db.session.flush()

            tailor = Tailor.query.filter_by(user_id=user.id).first()
            if not tailor:
                tailor = Tailor(
                    user_id=user.id,
                    shop_name=f"{SHOP_NAMES[idx % len(SHOP_NAMES)]} ({loc['city']})",
                    city=loc["city"],
                    state_id=state_id,
                    district_id=loc["district_id"],
                    latitude=loc["lat"] + round(random.uniform(-0.012, 0.012), 5),
                    longitude=loc["lng"] + round(random.uniform(-0.012, 0.012), 5),
                    address=loc["address"],
                    specialization=loc["specialties"],
                    is_active=True,
                    is_verified=True,
                    availability="Available",
                    rating=round(random.uniform(4.6, 4.95), 1),
                    total_reviews=random.randint(22, 98),
                    experience=random.randint(8, 25),
                    price_range=random.choice(["₹450 - ₹1,800", "₹600 - ₹2,500", "₹800 - ₹3,500", "₹1,200 - ₹5,000"])
                )
                db.session.add(tailor)

    # Now update all existing tailors to ensure they have TN coordinates
    tailors = Tailor.query.all()
    print(f"Ensuring {len(tailors)} tailors across Tamil Nadu...")

    for idx, tailor in enumerate(tailors):
        loc = TN_LOCATIONS[idx % len(TN_LOCATIONS)]
        if not tailor.city or tailor.city not in [l['city'] for l in TN_LOCATIONS]:
            tailor.city = loc["city"]
        if not tailor.district_id:
            tailor.district_id = loc["district_id"]
        if not tailor.state_id:
            tailor.state_id = state_id
        if not tailor.latitude or not tailor.longitude:
            tailor.latitude = loc["lat"] + round(random.uniform(-0.012, 0.012), 5)
            tailor.longitude = loc["lng"] + round(random.uniform(-0.012, 0.012), 5)
        if not tailor.address:
            tailor.address = loc["address"]
        if not tailor.specialization:
            tailor.specialization = loc["specialties"]
        tailor.is_active = True
        tailor.is_verified = True
        tailor.availability = "Available"
        if not tailor.rating or tailor.rating < 4.0:
            tailor.rating = round(random.uniform(4.6, 4.95), 1)
        if not tailor.total_reviews or tailor.total_reviews < 10:
            tailor.total_reviews = random.randint(18, 95)
        if not tailor.experience:
            tailor.experience = random.randint(6, 25)
        if not tailor.price_range:
            tailor.price_range = random.choice(["₹450 - ₹1,800", "₹600 - ₹2,500", "₹800 - ₹3,500", "₹1,200 - ₹5,000"])

    db.session.commit()
    print("Successfully ensured tailors across Tamil Nadu with coordinates & locations!")

if __name__ == "__main__":
    seed_tn_tailors()
