from datetime import datetime

from . import db


class Tailor(db.Model):
    __tablename__ = "tailors"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    shop_name = db.Column(
        db.String(150),
        nullable=False,
    )

    specialization = db.Column(
        db.String(255),
    )

    address = db.Column(
        db.String(255),
    )

    city = db.Column(
        db.String(100),
        index=True,
    )

    # Location hierarchy Foreign Keys
    state_id = db.Column(
        db.Integer,
        db.ForeignKey("states.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    district_id = db.Column(
        db.Integer,
        db.ForeignKey("districts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    taluk_id = db.Column(
        db.Integer,
        db.ForeignKey("taluks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    city_id = db.Column(
        db.Integer,
        db.ForeignKey("cities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    town_id = db.Column(
        db.Integer,
        db.ForeignKey("towns.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    village_id = db.Column(
        db.Integer,
        db.ForeignKey("villages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    latitude = db.Column(
        db.Float,
        nullable=True,
    )

    longitude = db.Column(
        db.Float,
        nullable=True,
    )

    description = db.Column(
        db.Text,
    )

    experience = db.Column(
        db.Integer,
        default=0,
    )

    price_range = db.Column(
        db.String(100),
    )

    availability = db.Column(
        db.String(100),
        default="Available",
    )

    rating = db.Column(
        db.Float,
        default=0,
    )

    total_reviews = db.Column(
        db.Integer,
        default=0,
    )

    is_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    orders = db.relationship(
        "Order",
        backref="tailor",
        cascade="all, delete-orphan",
        lazy=True,
    )

    reviews = db.relationship(
        "Review",
        backref="tailor",
        cascade="all, delete-orphan",
        lazy=True,
    )

    state = db.relationship(
        "State",
        backref="tailors",
        foreign_keys=[state_id],
    )

    district = db.relationship(
        "District",
        backref="tailors",
        foreign_keys=[district_id],
    )

    taluk = db.relationship(
        "Taluk",
        backref="tailors",
        foreign_keys=[taluk_id],
    )

    city_rel = db.relationship(
        "City",
        backref="tailors",
        foreign_keys=[city_id],
    )

    town = db.relationship(
        "Town",
        backref="tailors",
        foreign_keys=[town_id],
    )

    village = db.relationship(
        "Village",
        backref="tailors",
        foreign_keys=[village_id],
    )

    # --------------------------------------------------------
    # Display helpers
    # --------------------------------------------------------

    @property
    def display_rating(self):
        if self.rating is None:
            return 0

        return round(float(self.rating), 1)

    @property
    def experience_label(self):
        years = self.experience or 0

        if years == 0:
            return "New tailor"

        if years == 1:
            return "1 year experience"

        return f"{years} years experience"

    @property
    def availability_label(self):
        return self.availability or "Available"

    @property
    def location_display(self):
        """Returns readable location hierarchy breadcrumb."""
        parts = []
        if getattr(self, "village", None):
            parts.append(self.village.name)
        elif getattr(self, "town", None):
            parts.append(self.town.name)
        elif getattr(self, "city_rel", None):
            parts.append(self.city_rel.name)
        elif self.city:
            parts.append(self.city)

        if getattr(self, "taluk", None):
            parts.append(f"{self.taluk.name} Taluk")
        if getattr(self, "district", None):
            parts.append(self.district.name)
        if getattr(self, "state", None):
            parts.append(self.state.name)
        elif not parts:
            parts.append("Tamil Nadu")

        return ", ".join(parts)

    def recalculate_rating(self):
        from models.review import Review

        reviews_list = Review.query.filter_by(tailor_id=self.id).all()
        if not reviews_list:
            self.rating = 0.0
            self.total_reviews = 0
        else:
            self.total_reviews = len(reviews_list)
            self.rating = round(
                sum(r.rating for r in reviews_list) / len(reviews_list), 1
            )
        db.session.commit()

    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "shop_name": self.shop_name,
            "specialization": self.specialization,
            "address": self.address,
            "city": self.city,
            "state_id": self.state_id,
            "district_id": self.district_id,
            "taluk_id": self.taluk_id,
            "city_id": self.city_id,
            "town_id": self.town_id,
            "village_id": self.village_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_display": self.location_display,
            "description": self.description,
            "experience": self.experience,
            "price_range": self.price_range,
            "availability": self.availability,
            "rating": self.display_rating,
            "total_reviews": self.total_reviews or 0,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

    def __repr__(self):
        return (
            f"<Tailor {self.id}: "
            f"{self.shop_name}>"
        )