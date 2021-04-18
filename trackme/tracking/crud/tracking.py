from typing import Optional, List
from trackme.tracking.types import (
        # TrackingActivityInput, 
        # TrackingActivityOutput,
        # TrackingActivityOption,
        Topic,
        Attribute,
        # UserInput,
)
from sqlalchemy.sql import select 
from sqlalchemy.ext.asyncio.session import AsyncSession
from trackme.tracking.models import AttributeModel, TopicModel, EntryModel
from trackme.storage import async_session
from fastapi.logger import logger 



async def get_topics() -> List[Topic]:
    async with async_session() as db:
        try:
            topics = (await db.execute(select(TopicModel))).scalars().all()
            return [Topic.from_orm(topic) for topic in topics]
        except Exception as ex:
            logger.error(f"Could not collect topics due to {ex}")
            return []


async def get_attributes(user_id: Optional[int], topic_id: int) -> List[Attribute]:
    async with async_session() as db:
        try:
            attributes_statement = select(AttributeModel).filter(AttributeModel.topic_id == topic_id)
            if user_id is not None:
                attributes_statement.filter(AttributeModel.user_id == user_id)
            attributes = (await db.execute(attributes_statement)).scalars().all()
            return [Attribute.from_orm(attribute) for attribute in attributes]
        except Exception as ex:
            logger.error(f"Could not collect attributes due to {ex}")
            return []


async def _prepare_attributes(db: AsyncSession, attributes: List[Attribute]) -> List[AttributeModel]:
    return (await db.execute(select(AttributeModel).filter(AttributeModel.id.in_([a.id for a in attributes])))).scalars().all()


async def simple_track(topic_id: int, comment: Optional[str], estimation: int, attributes: List[Attribute], user_id: int) -> bool:
    async with async_session() as db:
        try:
            collected_attributes = await _prepare_attributes(db, attributes)
            print(f"user is {user_id}")
            db.add(EntryModel(comment=comment, estimation=estimation, topic_id=topic_id, attributes=collected_attributes, user_id=user_id))
            await db.commit()
            return True
        except Exception as ex:
            logger.error(f"Couldn't save entry due to {ex}")
            return False
