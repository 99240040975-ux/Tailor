from datetime import datetime
from models import db


class Tailor(db.Model):
    __tablename__ = 'tailors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    shop_name = db.Column(db.String(150), nullable=False)
    specialization = db.Column(db.String(200), nullable=True)  # e.g. "Suits, Ethnic Wear, Alterations"
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Integer, default=0)  # years
    price_range = db.Column(db.String(50), nullable=True)  # e.g. "₹300 - ₹2500"
    availability = db.Column(db.Boolean, default=True, index=True)
    rating = db.Column(db.Float, default=0.0, index=True)
    total_reviews = db.Column(db.Integer, default=0)
    
    # Location hierarchy Foreign Keys
    state_id = db.Column(db.Integer, db.ForeignKey('states.id', ondelete='SET NULL'), nullable=True, index=True)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id', ondelete='SET NULL'), nullable=True, index=True)
    taluk_id = db.Column(db.Integer, db.ForeignKey('taluks.id', ondelete='SET NULL'), nullable=True, index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id', ondelete='SET NULL'), nullable=True, index=True)
    town_id = db.Column(db.Integer, db.ForeignKey('towns.id', ondelete='SET NULL'), nullable=True, index=True)
    village_id = db.Column(db.Integer, db.ForeignKey('villages.id', ondelete='SET NULL'), nullable=True, index=True)
    
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    orders = db.relationship('Order', foreign_keys='Order.tailor_id', backref='tailor', lazy='dynamic')
    reviews = db.relationship('Review', foreign_keys='Review.tailor_id', backref='tailor', lazy='dynamic')

    @property
    def location_display(self):
        """Returns readable location hierarchy breadcrumb."""
        parts = []
        if self.village:
            parts.append(self.village.name)
        elif self.town:
            parts.append(self.town.name)
        elif self.city_rel:
            parts.append(self.city_rel.name)
        elif self.city:
            parts.append(self.city)
            
        if self.taluk:
            parts.append(f"{self.taluk.name} Taluk")
        if self.district:
            parts.append(self.district.name)
        if self.state:
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
            self.rating = round(sum(r.rating for r in reviews_list) / len(reviews_list), 1)
        db.session.commit()

    def __repr__(self):
        return f'<Tailor {self.shop_name} ({self.city})>'
