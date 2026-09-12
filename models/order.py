from datetime import datetime
from models import db


class Order(db.Model):
    __tablename__ = 'orders'

    STATUS_STAGES = [
        ('pending', 'Pending Review'),
        ('quoted', 'Quotation Provided'),
        ('confirmed', 'Confirmed & Measurement Verified'),
        ('cutting', 'Fabric Cutting'),
        ('stitching', 'Stitching in Progress'),
        ('alteration', 'Alteration / Fitting'),
        ('quality_check', 'Quality Inspection'),
        ('ready', 'Ready for Pickup / Delivery'),
        ('delivered', 'Completed / Delivered'),
        ('cancelled', 'Cancelled')
    ]

    STATUS_PROGRESS = {
        'pending': 10,
        'quoted': 20,
        'confirmed': 35,
        'cutting': 50,
        'stitching': 65,
        'alteration': 80,
        'quality_check': 90,
        'ready': 95,
        'delivered': 100,
        'cancelled': 0
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    tailor_id = db.Column(db.Integer, db.ForeignKey('tailors.id', ondelete='RESTRICT'), nullable=False, index=True)
    measurement_id = db.Column(db.Integer, db.ForeignKey('measurements.id', ondelete='SET NULL'), nullable=True)
    service_type = db.Column(db.String(50), nullable=False, default='custom')  # custom, alteration, repair, etc.
    clothing_type = db.Column(db.String(100), nullable=True)  # Shirt, Suit, Kurta, Blouse, etc.
    description = db.Column(db.Text, nullable=True)
    reference_image = db.Column(db.String(255), nullable=True)
    quotation = db.Column(db.Float, nullable=True)
    quotation_notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending', nullable=False, index=True)
    delivery_method = db.Column(db.String(50), default='pickup', nullable=False)  # pickup, delivery
    delivery_address = db.Column(db.Text, nullable=True)
    expected_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    messages = db.relationship('Message', backref='order', cascade='all, delete-orphan', lazy='dynamic')
    review = db.relationship('Review', backref='order', uselist=False, cascade='all, delete-orphan')

    @property
    def progress_percentage(self):
        return self.STATUS_PROGRESS.get(self.status, 10)

    @property
    def status_display(self):
        mapping = dict(self.STATUS_STAGES)
        return mapping.get(self.status, self.status.capitalize())

    def __repr__(self):
        return f'<Order #{self.id} {self.service_type} - {self.status}>'
