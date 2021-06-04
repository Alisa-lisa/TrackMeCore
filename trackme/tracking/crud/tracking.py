from datetime import datetime
from typing import Optional, List

from sqlalchemy import desc
from sqlalchemy.sql import select, delete
from sqlalchemy.ext.asyncio.session import AsyncSession

from trackme.tracking.models import EntryModel
from trackme.tracking.types.tracking import TrackingActivity

from trackme.tracking.crud.meta_validation import (
    _collect_attribute_name_for_entry,
)

from trackme.storage import async_session
from fastapi.logger import logger


async def simple_track(topic_id: int, comment: Optional[str], estimation: int, attribute: int, user_id: int) -> bool:
    async with async_session() as db:
        try:
            # TODO: validate attribute ids
            new_tracking = EntryModel(
                comment=comment, estimation=estimation, topic_id=topic_id, user_id=user_id, attribute_id=attribute
            )
            db.add(new_tracking)
            await db.commit()
            return True
        except Exception as ex:
            logger.error(f"Couldn't save entry due to {ex}")
            return False


async def _get_entry_by_id(db: AsyncSession, entry_ids: List[int], user_id: int) -> Optional[List[EntryModel]]:
    return (
        (
            await db.execute(
                select(EntryModel).filter(EntryModel.id.in_(entry_ids)).filter(EntryModel.user_id == user_id)
            )
        )
        .scalars()
        .all()
    )


async def _prepare_tracking_attribute(db: AsyncSession, entry: EntryModel) -> TrackingActivity:
    return TrackingActivity(
        id=entry.id,
        created_at=entry.created_at,
        edit_at=entry.edit_at,
        comment=entry.comment,
        estimation=entry.estimation,
        topic_id=entry.topic_id,
        user_id=entry.user_id,
        attribute=await _collect_attribute_name_for_entry(db, entry.attribute_id),
    )


async def edit_entry(user_id: int, entry_id: int, comment: Optional[str], attribute: Optional[int]) -> TrackingActivity:
    async with async_session() as db:
        entry = await _get_entry_by_id(db, [entry_id], user_id)
        if entry is None:
            raise ValueError("No entry found")
        entry = entry[0]
        try:
            if comment is not None:
                entry.comment = comment
            entry.edit_at = datetime.now()
            if attribute is not None:
                entry.attribute_id = attribute
            await db.commit()
        except Exception as ex:
            logger.error(f"Could not update entry due to {ex}")
        finally:
            return await _prepare_tracking_attribute(db, entry)


# TODO: where to put validation connected to DB?
async def delete_entry(entry_ids: List[int], user_id: int) -> bool:
    async with async_session() as db:
        try:
            entries = await _get_entry_by_id(db, entry_ids, user_id)
            if entries is None:
                return False
            await db.execute(delete(EntryModel).where(EntryModel.id.in_(entry_ids), EntryModel.user_id == user_id))
            await db.commit()
            return True
        except Exception as ex:
            logger.error(f"Could not delete entry due to {ex}")
            return False


async def filter_entries(
    user_id: int,
    topics: Optional[int],
    start: Optional[str],
    end: Optional[str],
    attribute: Optional[int],
    comments: bool,
) -> List[TrackingActivity]:
    async with async_session() as db:
        try:
            entries_query = select(EntryModel).filter(EntryModel.user_id == user_id)
            if topics is not None:
                entries_query = entries_query.filter(EntryModel.topic_id == topics)
            if start is not None:
                entries_query = entries_query.filter(EntryModel.created_at >= start)
            if end is not None:
                entries_query = entries_query.filter(EntryModel.created_at <= end)
            if comments:
                entries_query = entries_query.filter(EntryModel.comment.isnot(None))
            if attribute is not None:
                entries_query = entries_query.filter(EntryModel.attribute_id == attribute)
            entries_query = entries_query.order_by(desc(EntryModel.created_at))
            entries = (await db.execute(entries_query)).scalars().all()
            entries = [
                TrackingActivity(
                    id=entry.id,
                    created_at=entry.created_at,
                    edit_at=entry.edit_at,
                    comment=entry.comment,
                    estimation=entry.estimation,
                    topic_id=entry.topic_id,
                    user_id=entry.user_id,
                    attribute=await _collect_attribute_name_for_entry(db, entry.attribute_id),
                )
                for entry in entries
            ]
            return entries
        except Exception as ex:
            logger.error(f"Could not collect entries due to {ex}")
            return []
