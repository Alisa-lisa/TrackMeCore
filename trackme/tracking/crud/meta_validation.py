from typing import List
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from trackme.storage import async_session

from trackme.tracking.types.meta import AttributeOutput, Attribute

from trackme.tracking.models import AttributeModel, TAModel, TopicModel


async def _collect_attributes_for_entry(db: AsyncSession, entry_id: int) -> List[AttributeOutput]:
    attributes = (
        (
            await db.execute(
                select(AttributeModel)
                .join(TAModel)
                .filter(TAModel.deleted_at.is_(None))
                .filter(TAModel.tracking_id == entry_id)
                .filter(AttributeModel.id == TAModel.attribute_id)
            )
        )
        .scalars()
        .all()
    )
    return [AttributeOutput(name=a.name) for a in attributes]


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
