from typing import Optional, List
from trackme.tracking.types.data_type import (
        Topic,
        Attribute,
)
from sqlalchemy.sql import select, delete
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
            db.add(EntryModel(comment=comment, estimation=estimation, topic_id=topic_id, attributes=collected_attributes, user_id=user_id))
            await db.commit()
            return True
        except Exception as ex:
            logger.error(f"Couldn't save entry due to {ex}")
            return False


async def _get_entry_by_id(db: AsyncSession, entry_id: int, user_id: int) -> Optional[EntryModel]:
    return (await db.execute(select(EntryModel).filter(EntryModel.id == entry_id).filter(EntryModel.user_id == user_id))).scalars().first()


async def edit_entry(user_id: int, entry_id: int, comment: Optional[str], delete_attribuets: List[int], add_attributes: List[Attribute]) -> bool:
    async with async_session() as db:
        try:
            entry = (await _get_entry_by_id(db, entry_id, user_id))
            entry.comment = comment

            new_attributes_set = [a for a in entry.attributes if a.id not in delete_attribuets]
            # TODO: create new attributes and add them to the event update
            # new_attributes_set = new_attributes_set.extend([AttributeModel(name=a.name, topic_id=a.topic_id, user_id=user_id)])
            entry.attributes = new_attributes_set

            await db.commit()
            return True
        except Exception as ex:
            logger.error(f"Could not update entry due to {ex}")
            return False

# TODO: where to put validation connected to DB?
async def delete_entry(entry_id: int, user_id: int) -> bool:
    async with async_session() as db:
        try:
            entry = (await _get_entry_by_id(db, entry_id, user_id))
            if entry is None:
                return False
            await db.execute(delete(EntryModel).where(EntryModel.id == entry_id, EntryModel.user_id == user_id))
            return True
        except Exception as ex:
            logger.error(f"Could not delete entry due to {ex}")
            return False

