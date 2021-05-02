""" central model for data collection """
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from trackme.storage import Base


class TrackingAndAttributes(Base):
    __tablename__ = "tracking_attributes"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    deleted_at = Column(DateTime, nullable=True)
    attribute_id = Column(Integer, ForeignKey("attributes.id"))
    tracking_id = Column(Integer, ForeignKey("tracking.id", ondelete="CASCADE"))

    unique_combination = UniqueConstraint("attribute_id", "tracking_id", name="unique_combo_idx")


class TrackingActivity(Base):
    __tablename__ = "tracking"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    edit_at = Column(DateTime, nullable=True)
    comment = Column(String, nullable=True)
    estimation = Column(Integer, nullable=False)

    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)  # missing topic id is fast-track case
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    tracking_attributes = relationship(
        "TrackingAndAttributes", uselist=True, backref="tracking", cascade="all, delete-orphan"
    )
