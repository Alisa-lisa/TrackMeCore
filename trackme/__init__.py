""" setup module """
from trackme.tracking.models import (
    UserModel,
    UserActivityModel,
    TopicModel,
    AttributeModel,
    EntryModel,
)
from fastapi import FastAPI 



def app_factory():
    app = FastAPI(   
    title="TrackMe",
    description="Core tracking functionality",
    version="0.0.1"
    )

    # routes
    from trackme.tracking.api import user_router, tracking_router
    app.include_router(
            user_router,
            prefix="/user",
            tags=["user"],
            dependencies=[],
            responses={}
            )

    app.include_router(
        tracking_router,
        prefix="/track",
        tags=["tracking"],
        dependencies=[],
        responses={}
        )


    return app

