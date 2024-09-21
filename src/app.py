from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from dynaconf import LazySettings
    from fastapi import FastAPI
    from fastapi.routing import APIRoute


def create_app() -> FastAPI:
    import logging.config as logging_config
    import os

    from src import __typography__
    from src.logging import get_logging_dict
    from src.setting import settings

    print(__typography__, flush=True)
    print(f"Using Environment '{settings.ENVIRONMENT}'", end=os.linesep * 3, flush=True)

    # configure the logging
    logging_config.dictConfig(get_logging_dict())

    return _create_app(settings)


def _create_app(settings: LazySettings) -> FastAPI:
    from fastapi import FastAPI

    from src import __version__

    app = FastAPI(
        debug=settings.ENVIRONMENT in frozenset({"staging", "development"}),
        title=settings.PROJECT_NAME,
        version=__version__,
        openapi_url=(
            rf"{settings.BASE_URL}/openapi.json"
            if settings.ENVIRONMENT != "production"
            else None
        ),
        docs_url=(
            rf"{settings.BASE_URL}/docs"
            if settings.ENVIRONMENT != "production"
            else None
        ),
        redoc_url=(
            rf"{settings.BASE_URL}/redoc"
            if settings.ENVIRONMENT != "production"
            else None
        ),
        swagger_ui_oauth2_redirect_url=(
            rf"{settings.BASE_URL}/docs/oauth2-redirect"
            if settings.ENVIRONMENT != "production"
            else None
        ),
        generate_unique_id_function=_generate_custom_unique_id,
        lifespan=_lifespan,
    )

    _register_middlewares(app, settings)
    _register_routes(app, settings)

    return app


def _generate_custom_unique_id(route: APIRoute) -> str:
    return rf"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    _init_db()
    yield


def _init_db() -> None:
    # make sure all SQLModel models are imported (src.model) before initializing db
    # otherwise, SQLModel might fail to initialize relationships properly
    # for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28

    from src.model import UserCreate  # noqa

    from sqlmodel import SQLModel, Session
    from src.extension import engine
    from src.setting import settings
    from src.util.crud.user import get_user_by_email, create_new_user

    SQLModel.metadata.create_all(engine)

    db_user = None
    with Session(engine) as session:
        db_user = get_user_by_email(session=session, email=settings.SUPERUSER_EMAIL)

        if not db_user:
            create_new_user(
                session=session,
                user_detail=UserCreate(
                    email=settings.SUPERUSER_EMAIL,
                    password=settings.SUPERUSER_PASSWORD,
                    is_superuser=True,
                ),
            )


def _register_middlewares(app: FastAPI, settings: LazySettings) -> None:
    from starlette.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=settings.CORS_ALLOWED_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _register_routes(app: FastAPI, settings: LazySettings) -> None:
    from .router import router

    app.include_router(router, prefix=settings.BASE_URL)
