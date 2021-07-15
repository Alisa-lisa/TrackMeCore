""" setup module """
from trackme.tracking.models import *
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def app_factory():
    app = FastAPI(title="TrackMe", description="Core tracking functionality", version="0.0.1")

    # TODO: move allowed origins to config
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # routes
    from trackme.tracking.api import user_router, tracking_router, meta_router

    app.include_router(meta_router, prefix="/meta", tags=["meta"], dependencies=[], responses={})

    app.include_router(user_router, prefix="/user", tags=["user"], dependencies=[], responses={})

    app.include_router(tracking_router, prefix="/track", tags=["tracking"], dependencies=[], responses={})

    return app
