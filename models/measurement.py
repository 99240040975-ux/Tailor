from datetime import datetime
from models import db


class Measurement(db.Model):
    __tablename__ = 'measurements'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    profile_name = db.Column(db.String(100), nullable=False)  # e.g., "Arjun Formal Suit", "Casual Kurta"
    chest = db.Column(db.Float, nullable=True)
    waist = db.Column(db.Float, nullable=True)
    hip = db.Column(db.Float, nullable=True)
    shoulder = db.Column(db.Float, nullable=True)
    sleeve = db.Column(db.Float, nullable=True)
    neck = db.Column(db.Float, nullable=True)
    inseam = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(10), default='inches', nullable=False)  # 'inches' or 'cm'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    orders = db.relationship('Order', backref='measurement', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'profile_name': self.profile_name,
            'chest': self.chest,
            'waist': self.waist,
            'hip': self.hip,
            'shoulder': self.shoulder,
            'sleeve': self.sleeve,
            'neck': self.neck,
            'inseam': self.inseam,
            'height': self.height,
            'unit': self.unit,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }

    def __repr__(self):
        return f'<Measurement {self.profile_name} for User {self.customer_id}>'
