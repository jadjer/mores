#  Copyright 2022 Pavel Suprunov
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pytest

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine
)
from sqlalchemy.orm import sessionmaker

from app.core.settings.app import AppSettings
from app.database.repositories import UsersRepository
from app.database.repositories.posts import PostsRepository
from app.models.domain.post import Post
from app.models.domain.user import User
from app.services import jwt


@pytest.fixture
def settings() -> AppSettings:
    from app.core.config import get_app_settings

    return get_app_settings()


@pytest.fixture
def app() -> FastAPI:
    from app.main import get_application  # local import for testing purpose

    return get_application()


@pytest.fixture
async def engine(settings: AppSettings) -> AsyncEngine:
    engine = create_async_engine(settings.get_database_url)

    return engine


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncSession:
    connection = await engine.connect()
    transaction = await connection.begin()

    async_session = sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)
    session = async_session()

    try:
        yield session

    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()


@pytest.fixture
async def initialized_app(app: FastAPI, session: AsyncSession) -> FastAPI:
    app.state.session = session

    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(
            app=app,
            base_url="http://localhost:10000",
            headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
async def test_user(session: AsyncSession) -> User:
    users_repo = UsersRepository(session)

    user: User = await users_repo.create_user(
        username="username",
        phone="+375257654321",
        password="password",
    )

    return user


@pytest.fixture
def authorization_prefix(settings: AppSettings) -> str:
    jwt_token_prefix = settings.jwt_token_prefix

    return jwt_token_prefix


@pytest.fixture
def token(test_user: User) -> str:
    return jwt.create_access_token_for_user(
        user_id=test_user.id,
        username=test_user.username,
        phone=test_user.phone,
        secret_key="secret_key"
    )


@pytest.fixture
def authorized_client(client: AsyncClient, authorization_prefix: str, token: str) -> AsyncClient:
    client.headers = {
        "Authorization": f"{authorization_prefix} {token}",
        **client.headers,
    }
    return client


# @pytest.fixture
# async def test_profile(test_user: User, session: AsyncSession) -> Profile:
#     profiles_repo = ProfilesRepository(session)
#
#     return await profiles_repo.create_profile_by_user_id(
#         test_user.id,
#     )


@pytest.fixture
async def test_post(test_user: User, session: AsyncSession) -> Post:
    posts_repo = PostsRepository(session)

    return await posts_repo.create_post_by_user(
        user=test_user,
        title="Test Slug",
        description="Slug for tests",
        thumbnail="",
        body="Test " * 100,
    )
