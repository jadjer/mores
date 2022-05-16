from fastapi import FastAPI
from loguru import logger

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.settings.app import AppSettings
from app.database.base import Base
from app.database.models import User, Token


async def connect_to_db(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Connecting to Postgres")

    engine = create_async_engine(
        settings.get_database_url,
        echo=True
    )
    app.state.database_engine = engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession
    )
    app.state.database_session = async_session

    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    await app.state.database_engine.dispose()

    logger.info("Connection closed")
