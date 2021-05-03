from datetime import datetime
from typing import Optional, List

from sqlalchemy import desc
from sqlalchemy.sql import select, delete
from sqlalchemy.ext.asyncio.session import AsyncSession

from trackme.tracking.models import EntryModel, TAModel
from trackme.tracking.types.tracking import TrackingActivity
from trackme.tracking.types.meta import Attribute

from trackme.tracking.crud.meta_validation import (
    _get_attributes_by_name,
    _get_topics_by_name,
    _collect_attributes_for_entry,
)

from trackme.storage import async_session
from fastapi.logger import logger


async def simple_track(
    topic_id: int, comment: Optional[str], estimation: int, attributes: List[Attribute], user_id: int
) -> bool:
    async with async_session() as db:
        try:
            # TODO: validate attribute ids
            tracking_attributes = [TAModel(attribute_id=attribute.id) for attribute in attributes]
            new_tracking = EntryModel(comment=comment, estimation=estimation, topic_id=topic_id, user_id=user_id)
            new_tracking.tracking_attributes = tracking_attributes
            db.add_all([new_tracking] + tracking_attributes)
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


async def edit_entry(
    user_id: int, entry_id: int, comment: Optional[str], delete_attribuets: List[int], add_attributes: List[Attribute]
) -> bool:
    async with async_session() as db:
        try:
            entry = await _get_entry_by_id(db, [entry_id], user_id)
            if entry is None:
                return False
            entry = entry[0]
            entry.comment = comment
            entry.edit_at = datetime.now()

            # updating entries happens on TAModel: create and delete
            deleted_ta = (
                (
                    await db.execute(
                        select(TAModel)
                        .filter(TAModel.attribute_id.in_(delete_attribuets))
                        .filter(TAModel.tracking_id == entry_id)
                        .filter(TAModel.deleted_at.is_(None))
                    )
                )
                .scalars()
                .all()
            )
            for ta in deleted_ta:
                ta.deleted_at = datetime.now()

            # creating new attributes for tracking entry
            new_ta = [TAModel(attribute_id=a.id, tracking_id=entry_id) for a in add_attributes]
            db.add_all(new_ta)
            await db.commit()
            return True
        except Exception as ex:
            logger.error(f"Could not update entry due to {ex}")
            return False


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
    topics: Optional[List[str]],
    start: Optional[str],
    end: Optional[str],
    attributes: Optional[List[str]],
    comments: bool,
) -> List[TrackingActivity]:
    async with async_session() as db:
        try:
            entries_query = select(EntryModel).filter(EntryModel.user_id == user_id)
            if topics is not None:
                if bool(topics):
                    topics_ids = await _get_topics_by_name(topics)
                    entries_query = entries_query.filter(EntryModel.topic_id.in_(topics_ids))
            if start is not None:
                entries_query = entries_query.filter(EntryModel.created_at >= start)
            if end is not None:
                entries_query = entries_query.filter(EntryModel.created_at <= end)
            if comments:
                entries_query = entries_query.filter(EntryModel.comment.isnot(None))
            if attributes is not None:
                if bool(attributes):
                    attributes_ids = await _get_attributes_by_name(attributes)
                    entries_query = (
                        entries_query.join(TAModel)
                        .filter(TAModel.tracking_id == EntryModel.id)
                        .filter(TAModel.deleted_at.is_(None))
                        .filter(TAModel.attribute_id.in_(attributes_ids))
                    )

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
                    attributes=await _collect_attributes_for_entry(db, entry.id),
                )
                for entry in entries
            ]
            return entries
        except Exception as ex:
            logger.error(f"Could not collect entries due to {ex}")
            return []
