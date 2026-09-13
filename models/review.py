from datetime import datetime

from . import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    tailor_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tailors.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "orders.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    rating = db.Column(
        db.Integer,
        nullable=False,
    )

    comment = db.Column(
        db.Text,
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    def __init__(
        self,
        customer_id=None,
        tailor_id=None,
        order_id=None,
        rating=None,
        comment=None,
        **kwargs,
    ):
        init_kwargs = {
            "customer_id": customer_id,
            "tailor_id": tailor_id,
            "order_id": order_id,
            "rating": rating,
            "comment": comment,
        }
        for key, val in init_kwargs.items():
            if val is not None:
                kwargs[key] = val
        super().__init__(**kwargs)

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    def set_rating(self, rating):
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            raise ValueError(
                "Rating must be a number from 1 to 5."
            )

        if rating < 1 or rating > 5:
            raise ValueError(
                "Rating must be between 1 and 5."
            )

        self.rating = rating

    @property
    def stars(self):
        rating = max(
            0,
            min(
                5,
                int(self.rating or 0),
            ),
        )

        return "★" * rating + "☆" * (5 - rating)

    @property
    def rating_label(self):
        labels = {
            1: "Poor",
            2: "Needs improvement",
            3: "Good",
            4: "Very good",
            5: "Excellent",
        }

        return labels.get(
            int(self.rating or 0),
            "Not rated",
        )

    @property
    def short_comment(self):
        if not self.comment:
            return ""

        if len(self.comment) <= 120:
            return self.comment

        return self.comment[:117] + "..."

    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "tailor_id": self.tailor_id,
            "order_id": self.order_id,
            "rating": self.rating,
            "stars": self.stars,
            "rating_label": self.rating_label,
            "comment": self.comment,
            "short_comment": self.short_comment,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

    def __repr__(self):
        return (
            f"<Review #{self.id} "
            f"for Tailor {self.tailor_id} "
            f"({self.rating} stars)>"
        )