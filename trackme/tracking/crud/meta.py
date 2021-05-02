from typing import List, Optional
from trackme.tracking.types.meta import (
    Topic,
    Attribute,
)
from trackme.tracking.models import AttributeModel, TopicModel
from sqlalchemy.sql import select
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
