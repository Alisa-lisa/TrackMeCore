""" user related objects """
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from trackme.storage import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    pwhash = Column(String(240), nullable=False)
    email = Column(String(240), nullable=False, unique=True)
    registration = Column(DateTime, nullable=False, default=datetime.now(), index=True)
    last_active = Column(DateTime, nullable=True, index=True)

    activity = relationship("UserActivity", backref="users", cascade="all, delete-orphan")
    tracking = relationship("TrackingActivity", backref="users", cascade="all, delete-orphan")
    attributes = relationship("Attribute", backref="users", cascade="all, delete-orphan")
    experiments = relationship("Experiment", backref="experiments", cascade="all, delete-orphan")


class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(UUID(as_uuid=True), unique=True, nullable=False)
    activation = Column(DateTime, nullable=False)
