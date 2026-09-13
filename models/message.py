from datetime import datetime

from . import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=True,
        index=True,
    )

    message = db.Column(
        db.Text,
        nullable=False,
    )

    is_read = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    def mark_as_read(self):
        self.is_read = True

    @property
    def preview(self):
        if not self.message:
            return ""

        if len(self.message) <= 100:
            return self.message

        return self.message[:97] + "..."

    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "order_id": self.order_id,
            "message": self.message,
            "preview": self.preview,
            "is_read": self.is_read,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

    def __repr__(self):
        return (
            f"<Message {self.id}: "
            f"{self.sender_id} -> "
            f"{self.receiver_id}>"
        )