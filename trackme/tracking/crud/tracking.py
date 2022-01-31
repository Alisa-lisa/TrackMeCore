from datetime import datetime
from typing import Optional, List, Tuple
import csv
from sqlalchemy import desc, func, distinct
from sqlalchemy.sql import select, delete
from sqlalchemy.ext.asyncio.session import AsyncSession

from trackme.tracking.models import EntryModel
from trackme.tracking.types.tracking import TrackingActivity, TrackingActivityInput

from trackme.tracking.crud.meta_validation import (
    _collect_attribute_name_for_entry,
)

from trackme.storage import async_session
from fastapi.logger import logger


async def simple_track(entries: List[TrackingActivityInput], user_id: int) -> bool:
    async with async_session() as db:
        logger.error(f"tracking entry has tag {entries[0].balance_tag}")
        try:
            # TODO: validate attribute ids
            trackings = [
                EntryModel(
                    comment=entry.comment,
                    estimation=entry.estimation,
                    topic_id=entry.topic_id,
                    user_id=user_id,
                    attribute_id=entry.attribute,
                    created_at=entry.time if entry.time is not None else None,
                    balance_tag=entry.balance_tag if entry.balance_tag is not None else None,
                )
                for entry in entries
            ]
            db.add_all(trackings)
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


async def edit_entry(
    user_id: int,
    entry_id: int,
    topic: Optional[int],
    comment: Optional[str],
    attribute: Optional[int],
) -> TrackingActivity:
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
            if topic is not None:
                entry.topic_id = topic
            await db.commit()
        except Exception as ex:
            logger.error(f"Could not update entry due to {ex}")
        finally:
            return await _prepare_tracking_attribute(db, entry)


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
    topics: Optional[int] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    attribute: Optional[int] = None,
    comments: Optional[bool] = None,
    ts: bool = False,
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
            if comments is not None:
                if comments:
                    entries_query = entries_query.filter(EntryModel.comment.isnot(None))
                else:
                    entries_query = entries_query.filter(EntryModel.comment.is_(None))
            if attribute is not None:
                entries_query = entries_query.filter(EntryModel.attribute_id == attribute)
            if ts:
                entries_query = entries_query.order_by(EntryModel.created_at.asc())
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
                    balance_tag=entry.balance_tag,
                )
                for entry in entries
            ]
            return entries
        except Exception as ex:
            logger.error(f"Could not collect entries due to {ex}")
            return []


async def get_time_horizon(user_id: int, attribute_id: int) -> list:
    """get earliest and latest entry dates"""
    async with async_session() as db:
        query_start = (
            select(func.min(EntryModel.created_at))
            .filter(EntryModel.attribute_id == attribute_id)
            .filter(EntryModel.user_id == user_id)
        )
        start = (await db.execute(query_start)).scalars().one()
        query_end = select(func.max(EntryModel.created_at)).filter(EntryModel.attribute_id == attribute_id)
        end = (await db.execute(query_end)).scalars().one()
        return [start.date() if start is not None else None, end.date() if end is not None else None]


# TODO: stricter definition of binary and non-binary attributes
# define what it means for binary to have an estimation
# define what it means for continuous not to have an estimation
async def collect_attributes_ids(user_id: int, binary: bool = False) -> List[int]:
    """Collect all attribute's ids binary or continuous
    binary attribute - all estimations are not set
    continuous attribute - all entries have estimations
    """
    async with async_session() as db:
        try:
            attributes_query = select(distinct(EntryModel.attribute_id)).filter(EntryModel.user_id == user_id)
            if not binary:
                attributes_query = attributes_query.filter(EntryModel.estimation.isnot(None))
            else:
                attributes_query = attributes_query.filter(EntryModel.estimation.is_(None))
            attributes = (await db.execute(attributes_query)).scalars().all()
            return attributes
        except Exception as ex:
            logger.error(f"Could not collect non-binary attributes for user {user_id} due to {ex}")
            return []


async def prepara_data_for_download(user_id: int) -> Tuple[str, str]:
    """create file and write collected data to it"""
    now = datetime.today().date()
    file_name = f"{user_id}_{now}_tracking.csv"
    file_path = f"./files/{file_name}"
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(["id", "created", "edited", "comment", "estimation", "topic", "attribute", "balance"])
        entries = await filter_entries(user_id=user_id)
        for entry in entries:
            comment = None if entry.comment is None else entry.comment.replace(",", ";")
            writer.writerow(
                [
                    entry.id,
                    entry.created_at,
                    entry.edit_at,
                    comment,
                    entry.estimation,
                    entry.deleted_at,
                    entry.topic_id,
                    entry.attribute,
                    entry.balance_tag,
                ]
            )
    return file_name, file_path
