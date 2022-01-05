from typing import Optional, List
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import func
from fastapi import HTTPException
from trackme.tracking.models import EntryModel
from trackme.storage import async_session


UNKNOWN_ID = "No entry with this id was found"


async def does_entry_exist(id: int) -> Optional[int]:
    async with async_session() as db:
        return (
            id
            if (await db.execute(select(EntryModel).filter(EntryModel.id == id))).scalars().first() is not None
            else None
        )


async def validate_tracking_ids(ids: List[int]) -> List[int]:
    existing_ids = [await does_entry_exist(id) for id in ids]
    if not any(existing_ids):
        raise HTTPException(404, UNKNOWN_ID)
    return ids


async def is_attribute_binary(attribute_id: int, user_id: int) -> bool:
    """
    Continuous attribute: most estimations (>90%) are set
    Binary attribute: most estimations (>90%) are not set
    """
    async with async_session() as db:
        base_query = (
            select(func.count(EntryModel.id))
            .filter(EntryModel.attribute_id == attribute_id)
            .filter(EntryModel.user_id == user_id)
        )
        nullable = (await db.execute(base_query.filter(EntryModel.estimation.is_(None)))).scalars().first()
        nonnullabel = (await db.execute(base_query.filter(EntryModel.estimation.isnot(None)))).scalars().first()
        return nullable / (nullable + nonnullabel) > 0.5
