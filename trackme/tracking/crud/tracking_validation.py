from typing import Optional, List
from sqlalchemy.sql import select
from fastapi import HTTPException
from trackme.tracking.models import EntryModel
from trackme.storage import async_session


UNKNOWN_ID = "No entry with this id was found"


async def does_entry_exist(id: int) -> Optional[int]:
    async with async_session() as db:
        return (
            id
            if (await db.execute(select(EntryModel).filter(EntryModel.id == id)))
            .scalars()
            .first()
            is not None
            else None
        )


async def validate_tracking_ids(ids: List[int]) -> List[int]:
    existing_ids = [await does_entry_exist(id) for id in ids]
    if not any(existing_ids):
        raise HTTPException(404, UNKNOWN_ID)
    return ids
