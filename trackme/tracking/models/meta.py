""" categorical classification for the tracking data """
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from trackme.storage import Base


# topic is one of 4 main areas of information: Mental, Social, Physical, Consumable
class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    associated_attributes = relationship(
        "Attribute", backref="topics", cascade="all, delete-orphan", uselist=True
    )


# attributes are some activities or events associated with a topic in an entry
class Attribute(Base):
    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    # default icons are hardcoded for now in the frontend, but can be changed in the future
    icon_name = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", "name", name="unique_attribute"),
    )
