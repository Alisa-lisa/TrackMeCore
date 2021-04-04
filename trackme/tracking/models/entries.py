""" central model for data collection """
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import backref, relationship
from datetime import datetime

from trackme.storage import Base


class TrackingActivity(Base):
    __tablename__ = "tracking"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    edit_at = Column(DateTime, nullable=True)
    comment = Column(String, nullable=True)
    estimation = Column(Integer, nullable=False)

    topic_id = Column(Integer, ForeignKey("topics.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    attributes = relationship("Attribute", uselist=True, backref="tracking")
