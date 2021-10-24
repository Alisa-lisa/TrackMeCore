from typing import List
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from trackme.storage import async_session

from trackme.tracking.types.meta import Attribute

from trackme.tracking.models import AttributeModel, TopicModel


async def _collect_attribute_name_for_entry(db: AsyncSession, entry_attribute_id: int) -> str:
    attribute_name = (
        (await db.execute(select(AttributeModel.name).filter(AttributeModel.id == entry_attribute_id)))
        .scalars()
        .first()
    )
    return attribute_name


async def _get_topics_by_name(names: List[str]) -> List[int]:
    async with async_session() as db:
        return (await db.execute(select(TopicModel.id).where(TopicModel.name.in_(names)))).scalars().all()


async def _get_attributes_by_name(names: List[str]) -> List[int]:
    async with async_session() as db:
        return (await db.execute(select(AttributeModel.id).where(AttributeModel.name.in_(names)))).scalars().all()


async def _prepare_attributes(db: AsyncSession, attributes: List[Attribute]) -> List[AttributeModel]:
    return (
        (await db.execute(select(AttributeModel).filter(AttributeModel.id.in_([a.id for a in attributes]))))
        .scalars()
        .all()
    )


async def does_topic_exist(db: AsyncSession, id: int) -> bool:
    attribute = (await db.execute(select(AttributeModel).filter(AttributeModel.id == id))).scalars()
    return True if attribute is not None else False
