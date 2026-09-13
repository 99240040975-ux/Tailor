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
    app = create_app()
    with app.app_context():
        # Ensure Tamil Nadu State exists
        tn_state = State.query.filter_by(name="Tamil Nadu").first()
        state_id = tn_state.id if tn_state else 31

        tailors = Tailor.query.all()
        print(f"Updating {len(tailors)} tailors across Tamil Nadu...")

        for idx, tailor in enumerate(tailors):
            loc = TN_LOCATIONS[idx % len(TN_LOCATIONS)]
            
            # Keep special shop names if customized, otherwise give clean Tamil Nadu craft shop name
            if "Studio" in tailor.shop_name or "053c9e19" in tailor.shop_name or "Test" in tailor.shop_name:
                tailor.shop_name = f"{SHOP_NAMES[idx % len(SHOP_NAMES)]} ({loc['city']})"
            
            tailor.state_id = state_id
            tailor.city = loc["city"]
            tailor.district_id = loc["district_id"]
            tailor.latitude = loc["lat"] + round(random.uniform(-0.015, 0.015), 5)
            tailor.longitude = loc["lng"] + round(random.uniform(-0.015, 0.015), 5)
            tailor.address = loc["address"]
            tailor.specialization = loc["specialties"]
            tailor.is_active = True
            tailor.is_verified = True
            tailor.availability = "Available"
            if not tailor.rating or tailor.rating < 4.0:
                tailor.rating = round(random.uniform(4.5, 4.95), 1)
            if not tailor.total_reviews or tailor.total_reviews < 10:
                tailor.total_reviews = random.randint(18, 95)
            if not tailor.experience:
                tailor.experience = random.randint(6, 25)
            if not tailor.price_range:
                tailor.price_range = random.choice(["₹450 - ₹1,800", "₹600 - ₹2,500", "₹800 - ₹3,500", "₹1,200 - ₹5,000"])

        db.session.commit()
        print("Successfully updated tailors with authentic Tamil Nadu coordinates & locations!")

if __name__ == "__main__":
    seed_tn_tailors()
