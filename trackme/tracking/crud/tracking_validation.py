from sqlalchemy.sql import select
from trackme.tracking.models import EntryModel
from trackme.storage import async_session


async def does_entry_exist(id: int) -> bool:
    async with async_session() as db:
        return (
            True
            if (await db.execute(select(EntryModel).filter(EntryModel.id == id))).scalars().first() is not None
            else False
        )
