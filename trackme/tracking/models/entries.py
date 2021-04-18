""" central model for data collection """
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from trackme.storage import Base


attributes_of_entry = Table('attributes_2_entry', Base.metadata,
        Column('attribute_id', Integer, ForeignKey('attributes.id')),
        Column('tracking_entry_id', Integer, ForeignKey('tracking.id')))


class TrackingActivity(Base):
    __tablename__ = "tracking"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    edit_at = Column(DateTime, nullable=True)
    comment = Column(String, nullable=True)
    estimation = Column(Integer, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)  # missing topic id is fast-track case
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attributes = relationship("Attribute", uselist=True, secondary=attributes_of_entry, backref="tracking")
