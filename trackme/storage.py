""" factory method for session creation """
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from trackme.config import Configuration

conf = Configuration()

Base = declarative_base()
engine = create_async_engine(conf.DB_URI)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
