from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(100),
        nullable=False,
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="customer",
        index=True,
    )

    phone = db.Column(
        db.String(20),
    )

    active = db.Column(
        "is_active",
        db.Boolean,
        nullable=False,
        default=True,
    )

    @property
    def is_active(self):
        return self.active

    @is_active.setter
    def is_active(self, value):
        self.active = value

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

    tailor_profile = db.relationship(
        "Tailor",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    measurements = db.relationship(
        "Measurement",
        backref="customer",
        cascade="all, delete-orphan",
        lazy=True,
    )

    customer_orders = db.relationship(
        "Order",
        foreign_keys="Order.customer_id",
        backref="customer",
        cascade="all, delete-orphan",
        lazy=True,
    )

    sent_messages = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        backref="sender",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy=True,
    )

    received_messages = db.relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        backref="receiver",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy=True,
    )

    # --------------------------------------------------------
    # Password security
    # --------------------------------------------------------

    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty.")

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):
        if not password or not self.password_hash:
            return False

        return check_password_hash(
            self.password_hash,
            password,
        )

    # --------------------------------------------------------
    # Role helpers
    # --------------------------------------------------------

    @property
    def is_customer(self):
        return self.role == "customer"

    @property
    def is_tailor(self):
        return self.role == "tailor"

    @property
    def is_admin(self):
        return self.role == "admin"

    # --------------------------------------------------------
    # Display helpers
    # --------------------------------------------------------

    @property
    def initials(self):
        parts = self.name.strip().split()

        if not parts:
            return "TC"

        if len(parts) == 1:
            return parts[0][0].upper()

        return (
            parts[0][0] +
            parts[-1][0]
        ).upper()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

    def __repr__(self):
        return (
            f"<User {self.id}: "
            f"{self.email}>"
        )