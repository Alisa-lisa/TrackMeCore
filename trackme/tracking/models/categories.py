""" categorical classification for the tracking data """
from sqlalchemy import Column, ForeignKey, Integer, String 
from sqlalchemy.orm import relationship

from trackme.storage import Base


# topic is one of 4 main areas of information: Mental, Social, Physical, Consumable
class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    associated_attributes = relationship("Attribute", backref="topics", cascade="all, delete-orphan")


# attributes are some activities or events associated with a topic in an entry
class Attribute(Base):
    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
