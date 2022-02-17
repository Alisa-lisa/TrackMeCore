from datetime import datetime
from trackme.tracking.crud.meta_validation import does_topic_exist
from typing import List, Optional
from trackme.tracking.types.meta import (
    Topic,
    Attribute,
    AttributeInput,
    AttributeUpdateInput,
    Experiment,
    ExperimentInput,
    ExperimentUpdateInput,
)
from trackme.tracking.models import (
    AttributeModel,
    TopicModel,
    ExperimentModel,
)
from sqlalchemy.sql import select
from trackme.storage import async_session
from fastapi.logger import logger


# READ
async def get_topics() -> List[Topic]:
    async with async_session() as db:
        try:
            topics = (await db.execute(select(TopicModel))).scalars().all()
            return [Topic.from_orm(topic) for topic in topics]
        except Exception as ex:
            logger.error(f"Could not collect topics due to {ex}")
            return []


async def get_attributes(user_id: Optional[int], topic_id: int) -> List[Attribute]:
    """
    Collect default attributes and attributes for specific user
    """
    async with async_session() as db:
        try:
            # collect only default attributes
            attributes_statement = select(AttributeModel).filter(
                (AttributeModel.topic_id == topic_id) & (AttributeModel.user_id.is_(None))
            )
            default_attributes = (await db.execute(attributes_statement)).scalars().all()
            default = [Attribute.from_orm(a) for a in default_attributes]

            # collect purely custom attributes
            custom = []
            if user_id is not None:
                custom_attributes_query = select(AttributeModel).filter(
                    (AttributeModel.topic_id == topic_id) & (AttributeModel.user_id == user_id)
                )
                custom_attributes = (await db.execute(custom_attributes_query)).scalars().all()
                custom = [Attribute.from_orm(attribute) for attribute in custom_attributes]
                default.extend(custom)
            return default
        except Exception as ex:
            logger.error(f"Could not collect attributes due to {ex}")
            return []


async def get_all_experiments(user_id: int) -> List[Experiment]:
    async with async_session() as db:
        result = []
        try:
            experiments = (
                (await db.execute(select(ExperimentModel).filter(ExperimentModel.user_id == user_id))).scalars().all()
            )
            result = [Experiment.from_orm(exp) for exp in experiments]
        except Exception as ex:
            logger.error(f"Could not collect experiments for the user due to {ex}")
        finally:
            return result


# WRITE
async def add_experiment(experiment: ExperimentInput, user_id: int) -> Optional[Experiment]:
    """Add experiment to start scoped tracking"""
    async with async_session() as db:
        try:
            # experiment is only allowed once the previous is closed - first iteration
            old_experiment_query = (
                select(ExperimentModel)
                .filter(ExperimentModel.user_id == user_id)
                .filter(ExperimentModel.closed_at.is_(None))
            )
            old_experiment = (await db.execute(old_experiment_query)).scalars().first()
            if old_experiment is not None:
                logger.error("Close previous experiment first!")
                return None
            new_experiment = ExperimentModel(user_id=user_id, name=experiment.name)
            db.add(new_experiment)
            await db.commit()
            new_experiment = (await db.execute(old_experiment_query)).scalars().first()
            return Experiment.from_orm(new_experiment)
        except Exception as ex:
            logger.error(f"Could not create an experiment due to {ex}")
            return None


# later on update
async def close_experiments(experiment: ExperimentUpdateInput, user_id: int) -> bool:
    async with async_session() as db:
        try:
            experiment_to_close = (
                (await db.execute(select(ExperimentModel).filter(ExperimentModel.id == experiment.id))).scalars().one()
            )
            assert experiment_to_close.user_id == user_id
            experiment_to_close.closed_at = datetime.today()
            await db.commit()
            return True
        except Exception as ex:
            logger.error(f"Could not close experiment {experiment.id} due to {ex}")
            return False


async def add_attributes(attribute: AttributeInput, user_id: int) -> Optional[Attribute]:
    """Try to add a new attribute for specific topic and user
    :params attribute: AttributeInput basic information for the new Attribute object
    :returns: Attribute if creation is successful, None otherwise
    """
    async with async_session() as db:
        try:
            # validate existence of the topic and user
            if await does_topic_exist(db, attribute.topic_id):
                db.add_all(
                    [
                        AttributeModel(
                            name=attribute.name,
                            topic_id=attribute.topic_id,
                            user_id=user_id,
                            icon_name=attribute.icon_name,
                        )
                    ]
                )
                await db.commit()
            new_attribute = (
                (
                    await db.execute(
                        select(AttributeModel)
                        .filter(AttributeModel.topic_id == attribute.topic_id)
                        .filter(AttributeModel.name == attribute.name)
                        .filter(AttributeModel.user_id == user_id)
                    )
                )
                .scalars()
                .first()
            )
            return Attribute.from_orm(new_attribute)
        except Exception as ex:
            logger.error(f"Could not create attribute due to {ex}")
            return None


async def update_attributes(attribute: AttributeUpdateInput) -> bool:
    async with async_session() as db:
        try:
            attribute_to_update = (
                (await db.execute(select(AttributeModel).filter(AttributeModel.id == attribute.id))).scalars().first()
            )
            logger.error(f"attribute_to_update is {attribute_to_update}")
            if attribute_to_update is not None:
                if attribute.active is not None:
                    attribute_to_update.active = attribute.active

                await db.commit()
                return True
            return False
        except Exception as ex:
            logger.error(f"Could not update an attribute due to {ex}")
            return False


async def delete_attributes(attribute_id: int) -> bool:
    """delete existing attribute except defaults
    TODO: full customization is a future feature
    """
    async with async_session() as db:
        try:
            attribute_to_delete = (
                (await db.execute(select(AttributeModel).filter(AttributeModel.id == attribute_id))).scalars().first()
            )
            await db.delete(attribute_to_delete)
            await db.commit()
            return True
        except Exception as ex:
            logger.error(f"Could not delete attribute due to {ex}")
            return False
