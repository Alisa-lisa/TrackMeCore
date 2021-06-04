""" central model for data collection """
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from datetime import datetime

from trackme.storage import Base


class TrackingActivity(Base):
    __tablename__ = "tracking"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    edit_at = Column(DateTime, nullable=True)
    comment = Column(String, nullable=True)
    estimation = Column(Integer, nullable=False)

    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)  # missing topic id is fast-track case
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attribute_id = Column(Integer, ForeignKey("attributes.id", name="tracking_attributes_fk"), nullable=False)

    # the data is not dropped when custom attribute is deleted by the user,
    # but is kept in stale state for future models to pick up on this change
    stale = Column(Boolean, default=False)
