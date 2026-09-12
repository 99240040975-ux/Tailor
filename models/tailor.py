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
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    orders = db.relationship('Order', foreign_keys='Order.tailor_id', backref='tailor', lazy='dynamic')
    reviews = db.relationship('Review', foreign_keys='Review.tailor_id', backref='tailor', lazy='dynamic')

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
