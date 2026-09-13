from datetime import datetime

from . import db


class Measurement(db.Model):
    __tablename__ = "measurements"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    profile_name = db.Column(
        db.String(100),
        nullable=False,
    )

    chest = db.Column(db.Float)
    waist = db.Column(db.Float)
    hip = db.Column(db.Float)
    shoulder = db.Column(db.Float)
    sleeve = db.Column(db.Float)
    neck = db.Column(db.Float)
    inseam = db.Column(db.Float)
    height = db.Column(db.Float)

    unit = db.Column(
        db.String(10),
        nullable=False,
        default="cm",
    )

    notes = db.Column(
        db.Text,
    )

    is_default = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
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
    # Helpers
    # --------------------------------------------------------

    def measurement_count(self):
        values = [
            self.chest,
            self.waist,
            self.hip,
            self.shoulder,
            self.sleeve,
            self.neck,
            self.inseam,
            self.height,
        ]

        return sum(
            1 for value in values
            if value is not None
        )

    @property
    def completion_percentage(self):
        total = 8

        completed = self.measurement_count()

        return round(
            (completed / total) * 100
        )

    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "profile_name": self.profile_name,
            "chest": self.chest,
            "waist": self.waist,
            "hip": self.hip,
            "shoulder": self.shoulder,
            "sleeve": self.sleeve,
            "neck": self.neck,
            "inseam": self.inseam,
            "height": self.height,
            "unit": self.unit,
            "notes": self.notes,
            "is_default": self.is_default,
            "completion_percentage": (
                self.completion_percentage
            ),
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

    def __repr__(self):
        return (
            f"<Measurement {self.id}: "
            f"{self.profile_name}>"
        )