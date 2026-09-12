from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from models import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='customer')  # 'customer', 'tailor', 'admin'
    profile_pic = db.Column(db.String(255), nullable=True)
    is_active_account = db.Column('is_active', db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tailor_profile = db.relationship('Tailor', backref='user', uselist=False, cascade='all, delete-orphan')
    measurements = db.relationship('Measurement', backref='customer', cascade='all, delete-orphan', lazy='dynamic')
    orders = db.relationship('Order', foreign_keys='Order.customer_id', backref='customer', lazy='dynamic')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy='dynamic')
    reviews_written = db.relationship('Review', foreign_keys='Review.customer_id', backref='customer', lazy='dynamic')

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    @property
    def is_customer(self):
        return self.role == 'customer'

    @property
    def is_tailor(self):
        return self.role == 'tailor'

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
