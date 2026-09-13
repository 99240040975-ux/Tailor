from datetime import datetime

from . import db


class Order(db.Model):
    __tablename__ = "orders"

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

    tailor_id = db.Column(
        db.Integer,
        db.ForeignKey("tailors.id"),
        nullable=False,
        index=True,
    )

    measurement_id = db.Column(
        db.Integer,
        db.ForeignKey("measurements.id"),
        nullable=True,
    )

    service_type = db.Column(
        db.String(100),
        nullable=False,
    )

    clothing_type = db.Column(
        db.String(100),
        nullable=False,
    )

    description = db.Column(
        db.Text,
    )

    reference_image = db.Column(
        db.String(255),
    )

    quotation = db.Column(
        db.Float,
        nullable=True,
    )

    quotation_notes = db.Column(
        db.Text,
        nullable=True,
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="pending",
        index=True,
    )

    delivery_method = db.Column(
        db.String(50),
        nullable=False,
        default="Pickup",
    )

    delivery_address = db.Column(
        db.String(255),
    )

    expected_date = db.Column(
        db.Date,
        nullable=True,
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

    measurement = db.relationship(
        "Measurement",
        backref="orders",
        lazy=True,
    )

    # --------------------------------------------------------
    # Order lifecycle
    # --------------------------------------------------------

    STATUS_FLOW = [
        "pending",
        "quoted",
        "confirmed",
        "cutting",
        "stitching",
        "alteration",
        "quality_check",
        "ready",
        "delivered",
    ]

    STATUS_LABELS = {
        "pending": "Order Received",
        "quoted": "Quotation Sent",
        "confirmed": "Confirmed",
        "cutting": "Cutting",
        "stitching": "Stitching",
        "alteration": "Alteration",
        "quality_check": "Quality Check",
        "ready": "Ready",
        "delivered": "Delivered",
    }

    # --------------------------------------------------------
    # Status helpers
    # --------------------------------------------------------

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(
            self.status,
            self.status.replace("_", " ").title()
            if self.status
            else "Unknown",
        )

    @property
    def status_index(self):
        try:
            return self.STATUS_FLOW.index(
                self.status
            )
        except ValueError:
            return 0

    @property
    def progress_percentage(self):
        if self.status == "delivered":
            return 100

        total_steps = len(self.STATUS_FLOW) - 1

        if total_steps <= 0:
            return 0

        return round(
            (self.status_index / total_steps) * 100
        )

    def can_move_to(self, new_status):
        if new_status not in self.STATUS_FLOW:
            return False

        if self.status not in self.STATUS_FLOW:
            return False

        new_index = self.STATUS_FLOW.index(
            new_status
        )

        current_index = self.STATUS_FLOW.index(
            self.status
        )

        return new_index == current_index + 1

    def advance_status(self):
        if self.status not in self.STATUS_FLOW:
            self.status = "pending"
            return self.status

        current_index = self.STATUS_FLOW.index(
            self.status
        )

        if current_index < len(self.STATUS_FLOW) - 1:
            self.status = self.STATUS_FLOW[
                current_index + 1
            ]

        return self.status

    # --------------------------------------------------------
    # Display helpers
    # --------------------------------------------------------

    @property
    def formatted_quotation(self):
        if self.quotation is None:
            return None

        return f"₹{self.quotation:,.2f}"

    @property
    def short_description(self):
        if not self.description:
            return ""

        if len(self.description) <= 120:
            return self.description

        return self.description[:117] + "..."

    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "tailor_id": self.tailor_id,
            "measurement_id": self.measurement_id,
            "service_type": self.service_type,
            "clothing_type": self.clothing_type,
            "description": self.description,
            "reference_image": self.reference_image,
            "quotation": self.quotation,
            "quotation_notes": self.quotation_notes,
            "status": self.status,
            "status_label": self.status_label,
            "progress_percentage": self.progress_percentage,
            "delivery_method": self.delivery_method,
            "delivery_address": self.delivery_address,
            "expected_date": (
                self.expected_date.isoformat()
                if self.expected_date
                else None
            ),
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
        }

    def __repr__(self):
        return f"<Order {self.id}: {self.status}>"